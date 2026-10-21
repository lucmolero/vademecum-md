"""Build structural diffs from private acquisition snapshots and current Markdown."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "history"))
from build_structural_diffs import article_diff  # noqa: E402
from migrate_public_corpus import parse_frontmatter  # noqa: E402


def source_text(path: Path, content_type: str = "") -> str:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("windows-1252")
    if "html" in content_type.lower() or "<html" in text[:1000].lower():
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup.find_all("br"):
            tag.replace_with("\n")
        for tag in soup.find_all(("script", "style", "noscript")):
            tag.decompose()
        block_nodes = soup.find_all(("p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td"))
        if not block_nodes:
            block_nodes = soup.find_all(("div", "section", "article"))
        blocks = []
        for node in block_nodes:
            value = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
            value = re.sub(r"\bArt\s+\.", "Art.", value, flags=re.IGNORECASE)
            if value and (not blocks or value != blocks[-1]):
                blocks.append(value)
        return "\n\n".join(blocks)
    return text


def digest(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def graph_relations(document_id: str) -> list[dict[str, object]]:
    graph = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    if not graph.is_file() or not document_id:
        return []
    relations: list[dict[str, object]] = []
    for line in graph.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        relation = json.loads(line)
        if document_id in {str(relation.get("source_id")), str(relation.get("target_id"))}:
            relations.append(relation)
    return relations


def risk_level(status: str, structure: dict[str, object], classifications: list[str]) -> str:
    if status in {"source_conflict", "source_unavailable", "source_invalid"}:
        return "critico"
    if any(label in classifications for label in ("possivel_revogacao", "possivel_veto", "possivel_retificacao", "possivel_efeito_de_vigencia")):
        return "alto"
    if structure.get("adicionados", 0) or structure.get("removidos", 0):
        return "alto"
    if structure.get("alterados", 0):
        return "medio"
    return "baixo"


_CURRENT_DOCUMENTS: dict[str, tuple[Path, str]] | None = None


def current_documents() -> dict[str, tuple[Path, str]]:
    global _CURRENT_DOCUMENTS
    if _CURRENT_DOCUMENTS is None:
        _CURRENT_DOCUMENTS = {}
        for path in (ROOT / "bases/curated/legislacao").rglob("*.md"):
            metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
            identifier = str(metadata.get("id") or "")
            if identifier:
                _CURRENT_DOCUMENTS[identifier] = (path, body)
    return _CURRENT_DOCUMENTS


def current_document(document_id: str) -> tuple[Path, str] | None:
    return current_documents().get(document_id)


def classify_change(status: str, old_body: str, new_body: str, structure: dict[str, object]) -> list[str]:
    if status == "source_conflict":
        return ["conflito_de_fontes", "requer_reconciliacao"]
    if status == "source_unavailable":
        return ["fonte_indisponivel", "requer_reconciliacao"]
    if status == "source_invalid":
        return ["fonte_invalida", "requer_reconciliacao"]
    classifications: list[str] = []
    lower = new_body.lower()
    semantic_text = unicodedata.normalize("NFKD", lower).encode("ascii", "ignore").decode("ascii")
    if structure.get("alterados", 0) or structure.get("adicionados", 0) or structure.get("removidos", 0):
        classifications.append("alteracao_normativa")
    else:
        classifications.append("formatacao_ou_metadado")
    for marker, label in (
        ("revog", "possivel_revogacao"),
        ("vet", "possivel_veto"),
        ("retific", "possivel_retificacao"),
        ("vigencia", "possivel_efeito_de_vigencia"),
        ("producao de efeitos", "possivel_efeito_de_vigencia"),
    ):
        if marker in semantic_text and label not in classifications:
            classifications.append(label)
    classifications.append("requer_reconciliacao")
    return classifications


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-resolution", type=Path, help="agent-reviewed official-source selections for conflicts")
    args = parser.parse_args()
    report = json.loads(args.collection_report.read_text(encoding="utf-8"))
    resolutions = {}
    if args.source_resolution and args.source_resolution.is_file():
        resolutions = json.loads(args.source_resolution.read_text(encoding="utf-8")).get("documents", {})
    results = report.get("results", [])
    args.output.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    for item in results:
        if item.get("status") not in {"changed_candidate", "source_conflict", "source_unavailable", "source_invalid"}:
            continue
        resolution = resolutions.get(str(item.get("matrix_id")))
        approved_resolution = resolution if isinstance(resolution, dict) and resolution.get("status") == "approved" else None
        selected_source_id = str((approved_resolution or {}).get("selected_source_id") or "")
        selected_attempt = next(
            (attempt for attempt in item.get("attempts", [])
             if attempt.get("status") == "fetched" and (not selected_source_id or attempt.get("source_id") == selected_source_id)),
            None,
        )
        expected_source_sha256 = str((approved_resolution or {}).get("expected_source_sha256") or "")
        if expected_source_sha256 and (not selected_attempt or selected_attempt.get("sha256_raw") != expected_source_sha256):
            selected_attempt = None
            approved_resolution = None
            selected_source_id = ""
        snapshot_name = (selected_attempt or item).get("snapshot_file")
        current = current_document(str(item.get("document_id") or ""))
        snapshot = ROOT / str(snapshot_name or "")
        detail: dict[str, object] = {
            "schema": "candidate-normative-diff/v1",
            "matrix_id": item.get("matrix_id"),
            "document_id": item.get("document_id"),
            "status": item.get("status"),
            "source": (selected_attempt or {}).get("url") or item.get("primary_url"),
        }
        if approved_resolution:
            detail["source_status_before_resolution"] = item.get("status")
        if approved_resolution:
            detail["resolution"] = approved_resolution
            detail["selected_source_id"] = selected_source_id
        if not current or not snapshot.is_file():
            detail["diff_status"] = "unavailable"
            detail["reason"] = "current_document_or_snapshot_missing"
            detail["hashes"] = {
                "current_body_sha256": None,
                "candidate_body_sha256": None,
                "source_raw_sha256": (selected_attempt or item).get("sha256_raw"),
                "source_normalized_sha256": (selected_attempt or item).get("sha256_normalized"),
                "source_legal_body_sha256": (selected_attempt or item).get("sha256_body"),
            }
            detail["risk"] = "critico"
            detail["classificacao"] = classify_change(str(item.get("status")), "", "", {})
            detail["relations_before"] = []
            detail["relation_impact_count"] = 0
        else:
            current_path, current_body = current
            attempt = next((value for value in item.get("attempts", []) if value.get("status") == "fetched"), {})
            updated_body = source_text(snapshot, str(attempt.get("content_type", "")))
            structure = article_diff(current_body, updated_body)
            detail["diff_status"] = "generated"
            detail["current_path"] = current_path.relative_to(ROOT).as_posix()
            detail["structure"] = structure
            analysis_status = "changed_candidate" if approved_resolution else str(item.get("status"))
            classifications = classify_change(analysis_status, current_body, updated_body, structure["artigos"])
            if approved_resolution:
                classifications = ["decisao_de_fonte_aprovada"] + [
                    label for label in classifications if label != "requer_reconciliacao"
                ]
            detail["classificacao"] = classifications
            detail["hashes"] = {
                "current_body_sha256": digest(current_body),
                "candidate_body_sha256": digest(updated_body),
                "source_raw_sha256": (selected_attempt or item).get("sha256_raw"),
                "source_normalized_sha256": (selected_attempt or item).get("sha256_normalized"),
                "source_legal_body_sha256": (selected_attempt or item).get("sha256_body"),
            }
            detail["risk"] = risk_level(analysis_status, structure["artigos"], classifications)
            detail["relations_before"] = graph_relations(str(item.get("document_id") or ""))
            detail["relation_impact_count"] = len(detail["relations_before"])
        detail["source_evidence"] = {
            "data_corte": item.get("data_corte"),
            "primary_url": (selected_attempt or {}).get("url") or item.get("primary_url"),
            "selected_source_id": selected_source_id or None,
            "attempts": [
                {key: value for key, value in attempt.items() if key != "snapshot_file"}
                for attempt in item.get("attempts", [])
            ],
        }
        target = args.output / f"{item.get('matrix_id', 'unknown')}.json"
        target.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        structure = detail.get("structure", {}).get("artigos", {})
        entries.append({
            "matrix_id": item.get("matrix_id"),
            "status": detail["diff_status"],
            "file": target.name,
            "artigos_alterados": structure.get("alterados", 0),
            "artigos_adicionados": structure.get("adicionados", 0),
            "artigos_removidos": structure.get("removidos", 0),
            "classificacao": detail.get("classificacao", ["requer_reconciliacao"]),
            "risco": detail.get("risk", "critico"),
            "relacoes_impactadas": detail.get("relation_impact_count", 0),
            "hashes": detail.get("hashes", {}),
        })
    index = {
        "schema": "candidate-normative-diff-index/v1",
        "documents": entries,
        "generated_count": sum(item["status"] == "generated" for item in entries),
        "unavailable_count": sum(item["status"] == "unavailable" for item in entries),
    }
    (args.output / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(index, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
