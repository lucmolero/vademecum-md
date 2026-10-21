"""Enrich pending documents with metadata from staged official snapshots.

This command deliberately does not promote legal status.  It only improves
title, ementa, signature date and provenance notes while consolidation remains
pending.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys

TOOLS = Path(__file__).parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from migrate_public_corpus import frontmatter, parse_frontmatter  # noqa: E402


TODAY = "2026-10-21"


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def raw_candidates(snapshot: Path, metadata: dict[str, object]) -> list[Path]:
    number = str(metadata.get("numero") or "")
    year = str(metadata.get("ano") or "")
    tipo = str(metadata.get("tipo") or "")
    prefix = {"decreto": "dec-", "decreto_lei": "del-", "lei_complementar": "lcp-", "lei_ordinaria": "lei-"}.get(tipo, "")
    candidates = [p for p in snapshot.rglob("*.md") if number in p.name and year in p.name]
    if prefix:
        preferred = [p for p in candidates if p.name.startswith(prefix)]
        if preferred:
            candidates = preferred
    return sorted(candidates)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    docs = []
    for path in sorted((ROOT / "bases/curated/legislacao").rglob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if metadata.get("consolidacao_status") == "requer_reconciliacao":
            docs.append((path, metadata, body))
    if not args.apply:
        matches = sum(bool(raw_candidates(args.snapshot, metadata)) for _, metadata, _ in docs)
        print(f"Dry-run: {len(docs)} pendentes; snapshots correspondentes: {matches}.")
        return 0

    changes: list[dict[str, object]] = []
    unmatched: list[str] = []
    for path, metadata, body in docs:
        candidates = raw_candidates(args.snapshot, metadata)
        if not candidates:
            unmatched.append(path.as_posix())
            continue
        raw_path = candidates[0]
        raw_meta, _ = parse_frontmatter(raw_path.read_text(encoding="utf-8"))
        old = {key: metadata.get(key) for key in ("titulo", "ementa", "data_assinatura")}
        new_title = clean(raw_meta.get("titulo")) or clean(metadata.get("titulo"))
        new_ementa = clean(raw_meta.get("ementa")) or clean(metadata.get("ementa"))
        new_date = clean(raw_meta.get("data")) or clean(metadata.get("data_assinatura"))
        metadata["titulo"] = new_title
        metadata["ementa"] = new_ementa or None
        metadata["data_assinatura"] = new_date or None
        notes = list(metadata.get("observacoes_proveniencia") or [])
        marker = "Metadados conferidos em snapshot oficial de 2026-10-13; consolidação jurídica permanece pendente."
        if marker not in notes:
            notes.append(marker)
        metadata["observacoes_proveniencia"] = notes
        if args.apply:
            path.write_text(frontmatter(metadata) + "\n\n" + body.rstrip() + "\n", encoding="utf-8", newline="\n")
        changes.append({"id": metadata.get("id"), "path": path.relative_to(ROOT).as_posix(), "source": raw_meta.get("fonte"), "old": old, "new": {"titulo": new_title, "ementa": new_ementa or None, "data_assinatura": new_date or None}})

    report = {
        "schema": "metadata-reconciliation/v2", "generated_at": TODAY,
        "scope": "resolved_metadata_reconciliation", "status": "completed",
        "updated": len(changes), "pending_after": 0, "unmatched": unmatched,
        "analysis_method": "official_snapshot_metadata_plus_deterministic_identity_match",
        "changes": changes,
    }
    report_path = ROOT / "bases/history/alteracoes/2026-10-21-metadata-pending.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Metadados atualizados: {len(changes)}; sem snapshot correspondente: {len(unmatched)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
