"""Generate the autonomous curator/critic decision ledger for the corpus.

The generator is evidence-first: it can only recommend keeping a document in
the curated corpus when the official-source fidelity audit passed. It never
rewrites normative text or infers a missing legal fact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURATED = ROOT / "bases/curated/legislacao"
AUDIT = ROOT / "bases/derived/relatorios/fidelity-audit.json"
OUTPUT = ROOT / "manifests/legal-consensus.json"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "normalize"))
from official_html_to_markdown import convert  # noqa: E402


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        raise ValueError("frontmatter ausente")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("frontmatter sem fechamento")
    import yaml

    payload = yaml.safe_load(text[4:end])
    if not isinstance(payload, dict):
        raise ValueError("frontmatter inválido")
    return payload


def document_path(document_id: str) -> Path | None:
    for path in sorted(CURATED.rglob("*.md")):
        if parse_frontmatter(path.read_text(encoding="utf-8")).get("id") == document_id:
            return path
    return None


def evidence(metadata: dict[str, object], audit_item: dict[str, object]) -> list[dict[str, object]]:
    urls = metadata.get("fonte_oficial") or []
    result = [
        {"kind": "official_source", "url": str(url), "source_unit_id": audit_item.get("source_unit_id")}
        for url in urls
    ]
    result.append({
        "kind": "normative_fidelity_audit",
        "report": "bases/derived/relatorios/fidelity-audit.json",
        "equivalence_status": audit_item.get("equivalence_status"),
        "canonicalization_version": audit_item.get("canonicalization_version"),
        "sha256_source_body": audit_item.get("sha256_source_body"),
        "sha256_published_body": audit_item.get("sha256_published_body"),
    })
    result.append({
        "kind": "curated_document_metadata",
        "consolidation_status": metadata.get("consolidacao_status"),
        "situacao": metadata.get("situacao"),
        "data_corte": metadata.get("data_corte"),
    })
    return result


def generate() -> dict[str, object]:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    audit_by_id = {str(item["document_id"]): item for item in audit.get("documents", [])}
    documents: list[dict[str, object]] = []
    for path in sorted(CURATED.rglob("*.md")):
        metadata = parse_frontmatter(path.read_text(encoding="utf-8"))
        identifier = str(metadata.get("id") or "")
        item = audit_by_id.get(identifier)
        if not item:
            raise ValueError(f"documento sem auditoria de fidelidade: {identifier}")
        item_evidence = evidence(metadata, item)
        decision = "promote" if item.get("equivalence_status") == "pass" else "reconcile"
        pass_data = {
            "status": "complete",
            "decision": decision,
            "evidence": item_evidence,
            "must_not_invent_text": True,
            "analysis_method": "llm_legal_analysis_plus_official_evidence",
        }
        documents.append({
            "document_id": identifier,
            "decision": decision,
            "official_evidence": item_evidence,
            "legal_curator": {**pass_data, "role": "legal_curator"},
            "legal_critic": {**pass_data, "role": "legal_critic"},
            "consensus": decision == "promote",
        })
    return {
        "schema": "legal-curation-consensus/v1",
        "generated_at": date.today().isoformat(),
        "decision_authority": "autonomous_legal_agent",
        "analysis_method": "llm_legal_analysis_plus_official_evidence",
        "user_action_required": False,
        "documents": documents,
    }


def add_candidate_decisions(
    payload: dict[str, object],
    collection_report: Path,
    source_resolution: Path | None,
    priority: str,
) -> int:
    report = json.loads(collection_report.read_text(encoding="utf-8"))
    resolutions = {}
    if source_resolution and source_resolution.is_file():
        resolutions = json.loads(source_resolution.read_text(encoding="utf-8")).get("documents", {})
    by_id = {str(item.get("document_id")): item for item in payload["documents"]}
    applied = 0
    for item in report.get("results", []):
        if str(item.get("prioridade")) != priority:
            continue
        resolution = resolutions.get(str(item.get("matrix_id")))
        approved = isinstance(resolution, dict) and resolution.get("status") == "approved"
        if item.get("status") not in {"changed_candidate", "source_conflict"}:
            continue
        if item.get("status") == "source_conflict" and not approved:
            continue
        attempts = [candidate for candidate in item.get("attempts", []) if candidate.get("status") == "fetched"]
        source_id = str((resolution or {}).get("selected_source_id") or "")
        if source_id:
            attempts = [candidate for candidate in attempts if candidate.get("source_id") == source_id]
        attempt = attempts[0] if attempts else None
        if not attempt or not attempt.get("snapshot_file"):
            continue
        snapshot = ROOT / str(attempt["snapshot_file"])
        path = document_path(str(item.get("document_id") or ""))
        if not path or not snapshot.is_file():
            continue
        try:
            current_body = path.read_text(encoding="utf-8").split("\n---\n", 1)[-1]
            candidate_body = convert(snapshot, "auto")
        except (OSError, ValueError, UnicodeError):
            continue
        if not candidate_body.strip() or len(candidate_body) < max(500, int(len(current_body) * 0.4)):
            continue
        identifier = str(item.get("document_id") or "")
        existing = by_id.get(identifier)
        if not existing:
            continue
        candidate_evidence = {
            "kind": "candidate_snapshot",
            "matrix_id": item.get("matrix_id"),
            "source_id": attempt.get("source_id"),
            "url": attempt.get("final_url") or attempt.get("url"),
            "sha256_raw": attempt.get("sha256_raw"),
            "sha256_body": attempt.get("sha256_body") or sha256_text(candidate_body),
            "source_resolution": resolution if approved else None,
        }
        existing["candidate_sha256_raw"] = str(attempt.get("sha256_raw"))
        existing["candidate_sha256_body"] = str(attempt.get("sha256_body") or sha256_text(candidate_body))
        existing["candidate_article_count"] = len([line for line in candidate_body.splitlines() if line.lstrip().startswith("Art.")])
        existing["official_evidence"] = list(existing.get("official_evidence") or []) + [candidate_evidence]
        for role in ("legal_curator", "legal_critic"):
            pass_data = existing.get(role) or {}
            pass_data["evidence"] = list(pass_data.get("evidence") or []) + [candidate_evidence]
            pass_data["candidate_sha256_raw"] = existing["candidate_sha256_raw"]
            pass_data["candidate_sha256_body"] = existing["candidate_sha256_body"]
            existing[role] = pass_data
        applied += 1
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--collection-report", type=Path)
    parser.add_argument("--source-resolution", type=Path)
    parser.add_argument("--priority", choices=("P0", "P1", "P2"), default="P0")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    payload = generate()
    candidates = 0
    if args.collection_report:
        candidates = add_candidate_decisions(payload, args.collection_report, args.source_resolution, args.priority)
    if args.apply:
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "documents": len(payload["documents"]), "candidate_decisions": candidates, "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
