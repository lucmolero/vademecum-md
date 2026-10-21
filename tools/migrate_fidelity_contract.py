"""Attach the v2 fidelity and explicit-nullability contract to corpus files."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from migrate_public_corpus import CURATED, frontmatter, parse_frontmatter  # noqa: E402


def status_for(metadata: dict[str, object], field: str) -> str:
    value = metadata.get(field)
    if value not in (None, "", []):
        return "presente"
    if field == "numero" and metadata.get("tipo") in {"constituicao", "ato_constitucional"}:
        return "nao_aplicavel"
    if field == "fonte_publicacao":
        return "indisponivel_na_fonte_publica"
    return f"ausente_na_publicacao:{field}"


def apply_contract(audit_path: Path, *, write: bool) -> dict[str, int]:
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    by_id = {str(item.get("document_id")): item for item in audit.get("documents", [])}
    counts: dict[str, int] = {}
    for path in sorted(CURATED.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
        item = by_id.get(str(metadata.get("id")), {})
        metadata["fonte_publicacao_status"] = status_for(metadata, "fonte_publicacao")
        metadata["numero_status"] = status_for(metadata, "numero")
        metadata["ementa_status"] = status_for(metadata, "ementa")
        metadata["data_assinatura_status"] = status_for(metadata, "data_assinatura")
        metadata["texto_classificacao"] = (
            "texto_consolidado"
            if metadata.get("consolidacao_status") in {"consolidada_fonte_oficial", "consolidada_reconciliada"}
            else "texto_original"
        )
        metadata["canonicalization_version"] = item.get("canonicalization_version", "norm-v2")
        metadata["source_unit_id"] = item.get("source_unit_id", str(metadata.get("id")))
        metadata["source_unit_selector"] = item.get("selector_applied") or item.get("source_unit_selector") or {"selector_type": "full_official_document", "selector": None}
        metadata["fidelity_status"] = item.get("equivalence_status", "needs_source_evidence")
        metadata["fidelity_anomalies"] = item.get("anomalies", [])
        metadata["hash_scope"] = {
            "sha256_source_raw": "official_snapshot_bytes",
            "sha256_source_normalized": "selected_source_text_norm_v2",
            "sha256_source_body": "selected_normative_body_norm_v2",
            "sha256_published_body": "published_normative_body_norm_v2",
        }
        for key in ("sha256_source_raw", "sha256_source_normalized", "sha256_source_body", "sha256_published_body"):
            if item.get(key):
                metadata[key] = item[key]
        if item.get("source_snapshot_date"):
            metadata["source_snapshot_date"] = item["source_snapshot_date"]
        counts[str(metadata["fidelity_status"])] = counts.get(str(metadata["fidelity_status"]), 0) + 1
        if write:
            path.write_text(frontmatter(metadata) + "\n" + body.rstrip() + "\n", encoding="utf-8", newline="\n")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=ROOT / "bases/derived/relatorios/fidelity-audit.json")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    counts = apply_contract(args.audit, write=args.apply)
    print(json.dumps({"mode": "apply" if args.apply else "dry_run", "counts": counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
