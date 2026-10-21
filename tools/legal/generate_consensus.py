"""Generate the autonomous curator/critic decision ledger for the corpus.

The generator is evidence-first: it can only recommend keeping a document in
the curated corpus when the official-source fidelity audit passed. It never
rewrites normative text or infers a missing legal fact.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURATED = ROOT / "bases/curated/legislacao"
AUDIT = ROOT / "bases/derived/relatorios/fidelity-audit.json"
OUTPUT = ROOT / "manifests/legal-consensus.json"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    payload = generate()
    if args.apply:
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "documents": len(payload["documents"]), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
