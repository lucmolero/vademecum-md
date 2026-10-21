"""Audit promoted editorial documents against their current official sources.

This is a reproducible technical-legal curation audit.  It verifies identity,
local completeness, source availability and the legal-body hash captured from
the official page.  It does not infer a consolidated text when the source is
unavailable and never publishes private snapshot paths.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from migrate_public_corpus import CURATED, parse_frontmatter  # noqa: E402


ROOT = Path(__file__).parents[2]
DEFAULT_SOURCE_REPORT = ROOT / ".private" / "audit-expansion-2026-10-21.json"
DEFAULT_OUTPUT = ROOT / "bases" / "derived" / "relatorios" / "editorial-legal-audit.json"
LEGAL_MARKERS = ("Art.", "ART.", "LEI ", "DECRETO-LEI ")


def load_matrix() -> dict[str, dict[str, str]]:
    with (ROOT / "manifests/corpus.csv").open(encoding="utf-8-sig", newline="") as stream:
        return {row["document_id"]: row for row in csv.DictReader(stream, delimiter=";")}


def find_document(document_id: str) -> tuple[Path, dict[str, object], str] | None:
    for path in CURATED.rglob("*.md"):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
        if str(metadata.get("id")) == document_id:
            return path, metadata, body
    return None


def load_curated_documents() -> dict[str, tuple[Path, dict[str, object], str]]:
    documents: dict[str, tuple[Path, dict[str, object], str]] = {}
    for path in CURATED.rglob("*.md"):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
        identifier = str(metadata.get("id") or "")
        if identifier:
            documents[identifier] = (path, metadata, body)
    return documents


def graph_counts() -> Counter[str]:
    counts: Counter[str] = Counter()
    graph = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    if not graph.is_file():
        return counts
    for line in graph.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        counts[str(item.get("source_id"))] += 1
        counts[str(item.get("target_id"))] += 1
    return counts


def load_source_resolutions() -> dict[str, dict[str, object]]:
    path = ROOT / "manifests/source-resolution.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(key): value for key, value in (payload.get("documents") or {}).items()}


def load_source_manifest() -> dict[str, dict[str, object]]:
    path = ROOT / "manifests/sources-official.json"
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(item.get("id")): item for item in payload.get("documents", [])}


def audit(source_report: Path, output: Path) -> dict[str, object]:
    report = json.loads(source_report.read_text(encoding="utf-8"))
    matrix = load_matrix()
    resolutions = load_source_resolutions()
    source_manifest = load_source_manifest()
    graph = graph_counts()
    curated_documents = load_curated_documents()
    entries: list[dict[str, object]] = []
    errors: list[str] = []

    for result in report.get("results", []):
        document_id = str(result.get("document_id") or "")
        found = curated_documents.get(document_id)
        if not found:
            errors.append(f"documento ausente: {document_id}")
            continue
        entry_errors: list[str] = []
        path, metadata, body = found
        matrix_row = matrix.get(document_id, {})
        attempts = [item for item in result.get("attempts", []) if item.get("status") == "fetched"]
        resolution = resolutions.get(str(result.get("matrix_id") or ""), {})
        selected_source_id = str(resolution.get("selected_source_id") or "")
        attempt = next((item for item in attempts if item.get("source_id") == selected_source_id), attempts[0] if attempts else {})
        observed_hash = str(attempt.get("sha256_body") or "")
        observed_raw_hash = str(attempt.get("sha256_raw") or "")
        source_url = str(attempt.get("url") or (metadata.get("fonte_oficial", [""])[0]))
        expected_hash = str(metadata.get("sha256_corpo") or "")
        if not expected_hash:
            primary_manifest = source_manifest.get(document_id, {})
            expected_hash = str(primary_manifest.get("sha256_corpo") or "")
            manifest_entries = [primary_manifest]
            manifest_entries.extend(
                source_manifest.get(str(identifier), {})
                for identifier in result.get("source_manifest_ids", [])
                if str(identifier) != document_id
            )
            per_source = [
                item
                for manifest_entry in manifest_entries
                for item in (manifest_entry.get("sha256_corpo_por_fonte") or [])
            ]
            if not expected_hash:
                expected_hash = next(
                    (
                        str(item.get("sha256_corpo") or "")
                        for item in per_source
                        if str(item.get("fonte") or "") == source_url
                    ),
                    "",
                )
        identity = {
            "document_id": document_id == str(matrix_row.get("document_id") or ""),
            "numero": str(metadata.get("numero") or "") == str(matrix_row.get("numero") or ""),
            "ano": str(metadata.get("ano") or "") == str(matrix_row.get("ano") or ""),
            "tipo": str(metadata.get("tipo") or "") == str(matrix_row.get("tipo") or ""),
            "source_url": source_url in {str(value) for value in metadata.get("fonte_oficial", [])},
        }
        local_integrity = {
            "body_nonempty": bool(body.strip()),
            "legal_marker_present": any(marker in body for marker in LEGAL_MARKERS),
            "sha256_corpo_format": len(expected_hash) == 64,
            "official_source_declared": bool(source_url),
        }
        hash_match = bool(observed_hash and expected_hash and observed_hash == expected_hash)
        source_status = str(result.get("status") or "unknown")
        conflict_resolved = False
        if source_status == "source_conflict":
            conflict_resolved = (
                resolution.get("status") == "approved"
                and bool(selected_source_id)
                and str(resolution.get("expected_source_sha256") or "") == observed_raw_hash
            )
            if not conflict_resolved:
                entry_errors.append(f"conflito de fontes sem resolução aprovada: {document_id}")
        elif source_status not in {"unchanged", "changed_candidate"}:
            entry_errors.append(f"fonte não inalterada: {document_id}:{source_status}")
        if not hash_match:
            entry_errors.append(f"hash jurídico divergente: {document_id}")
        if not all(identity.values()):
            entry_errors.append(f"identidade divergente: {document_id}")
        if not all(local_integrity.values()):
            entry_errors.append(f"integridade local incompleta: {document_id}")
        errors.extend(entry_errors)

        situation = str(metadata.get("situacao") or "desconhecida")
        status_result = (
            "parcialmente_revogada_com_dispositivos_remanescentes"
            if situation == "parcialmente_revogada"
            else "diploma_em_vigor_com_alteracoes_preservadas"
        )
        current_update_markers = [
            marker for marker in ("15.295", "15.512", "15.042", "14.026", "13.964")
            if marker in body
        ]
        entries.append({
            "document_id": document_id,
            "matrix_id": str(result.get("matrix_id") or ""),
            "path": path.relative_to(ROOT).as_posix(),
            "titulo": str(metadata.get("titulo") or ""),
            "tipo": str(metadata.get("tipo") or ""),
            "numero": str(metadata.get("numero") or ""),
            "ano": int(metadata.get("ano")),
            "prioridade": str(metadata.get("prioridade") or ""),
            "fonte_oficial": source_url,
            "autoridade_fonte": "Planalto / Casa Civil / Subchefia para Assuntos Jurídicos",
            "consulta_em": str(report.get("as_of") or date.today().isoformat()),
            "source_status": source_status,
            "source_resolution_status": "approved" if conflict_resolved else ("not_required" if source_status == "unchanged" else "unresolved"),
            "selected_source_id": selected_source_id or str(attempt.get("source_id") or ""),
            "selected_source_url": source_url,
            "hash_sha256_corpo_local": expected_hash,
            "hash_sha256_corpo_observado": observed_hash,
            "hash_match": hash_match,
            "identity": identity,
            "local_integrity": local_integrity,
            "situacao_declarada": situation,
            "situacao_resultado": status_result,
            "consolidacao_status": str(metadata.get("consolidacao_status") or ""),
            "atualizacoes_normativas_identificadas": current_update_markers,
            "relacoes_no_grafo": graph.get(document_id, 0),
            "decision": "approved_for_curated_corpus" if not entry_errors else "requires_reconciliation",
            "review_scope": "curated_corpus_inclusion_and_current_official_source",
            "review_basis": [
                "official_source_retrieved",
                "official_legal_body_hash_match",
                "identity_match_against_matrix",
                "local_body_structural_check",
            ],
            "limitations": [
                "This audit does not replace a case-specific legal opinion.",
                "Regulatory acts and jurisprudence remain separate layers.",
                "Individual provisions may be altered, repealed or subject to future effect dates.",
            ],
        })

    result = {
        "schema": "editorial-legal-audit/v1",
        "generated_at": date.today().isoformat(),
        "scope": f"{len(entries)} curated documents from the supplied official-source report",
        "method": "official current-source retrieval plus deterministic identity, integrity and legal-body hash checks",
        "authority_policy": "only official public sources are used as textual authority",
        "document_count": len(entries),
        "approved_count": sum(item["decision"] == "approved_for_curated_corpus" for item in entries),
        "reconciliation_count": sum(item["decision"] == "requires_reconciliation" for item in entries),
        "source_status": dict(Counter(str(item["source_status"]) for item in entries)),
        "situation_results": dict(Counter(str(item["situacao_resultado"]) for item in entries)),
        "errors": errors,
        "status": "pass" if not errors and len(entries) == len(report.get("results", [])) and bool(entries) else "fail",
        "documents": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-report", type=Path, default=DEFAULT_SOURCE_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit(args.source_report, args.output)
    print(json.dumps({key: result[key] for key in ("document_count", "approved_count", "reconciliation_count", "status")}, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
