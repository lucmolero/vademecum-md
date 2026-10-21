"""Validate and enrich the editorial matrix from the canonical Markdown corpus.

The matrix remains the editorial scope authority. Canonical document metadata is
copied into explicit machine-readable columns so the relation between an
editorial item and its Markdown document is deterministic and auditable.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from migrate_public_corpus import CURATED, ROOT, parse_frontmatter


MATRIX = ROOT / "manifests/corpus.csv"
NEW_COLUMNS = (
    "document_id", "document_path", "status_consolidacao", "status_situacao",
    "data_corte", "sha256_origem", "fonte_oficial_count",
)
CONTROLLED_COLUMNS = ("fonte_oficial", "status_atualidade", *NEW_COLUMNS)
CONSOLIDATED = {"consolidada_fonte_oficial", "consolidada_reconciliada"}


def number_key(value: object) -> str:
    return re.sub(r"\D", "", str(value or ""))


def identity_key(metadata: dict[str, object]) -> tuple[str, str, str]:
    return (str(metadata.get("tipo") or ""), number_key(metadata.get("numero")), str(metadata.get("ano") or ""))


def load_documents() -> dict[tuple[str, str, str], list[tuple[Path, dict[str, object]]]]:
    index: dict[tuple[str, str, str], list[tuple[Path, dict[str, object]]]] = defaultdict(list)
    for path in sorted(CURATED.rglob("*.md")):
        metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
        index[identity_key(metadata)].append((path, metadata))
    return index


def load_matrix() -> tuple[list[dict[str, str]], list[str]]:
    with MATRIX.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        return list(reader), list(reader.fieldnames or [])


def enrich(rows: list[dict[str, str]], index: dict[tuple[str, str, str], list[tuple[Path, dict[str, object]]]]) -> tuple[list[dict[str, str]], list[dict[str, object]], list[dict[str, object]]]:
    errors: list[dict[str, object]] = []
    drift: list[dict[str, object]] = []
    enriched: list[dict[str, str]] = []
    for row in rows:
        key = (str(row.get("tipo") or ""), number_key(row.get("numero")), str(row.get("ano") or ""))
        matches = index.get(key, [])
        if len(matches) != 1:
            errors.append({
                "matrix_id": row.get("id"), "key": key,
                "kind": "missing" if not matches else "ambiguous",
                "matches": [str(path.relative_to(ROOT)) for path, _ in matches],
            })
            enriched.append(dict(row))
            continue
        path, metadata = matches[0]
        sources = metadata.get("fonte_oficial") or []
        if isinstance(sources, str):
            sources = [sources]
        status = str(metadata.get("consolidacao_status") or "")
        item = dict(row)
        item.update({
            "fonte_oficial": "|".join(str(source) for source in sources),
            "status_atualidade": "confirmada" if status in CONSOLIDATED else "pendente",
            "document_id": str(metadata.get("id") or ""),
            "document_path": path.relative_to(ROOT).as_posix(),
            "status_consolidacao": status,
            "status_situacao": str(metadata.get("situacao") or ""),
            "data_corte": str(metadata.get("data_corte") or ""),
            "sha256_origem": str(metadata.get("sha256_origem") or ""),
            "fonte_oficial_count": str(len(sources)),
        })
        for field in CONTROLLED_COLUMNS:
            actual = str(row.get(field) or "")
            expected = str(item.get(field) or "")
            if actual != expected:
                drift.append({
                    "matrix_id": row.get("id"),
                    "field": field,
                    "actual": actual,
                    "expected": expected,
                })
        enriched.append(item)
    return enriched, errors, drift


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the enriched matrix")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/editorial-matrix-audit.json")
    args = parser.parse_args()
    rows, fields = load_matrix()
    index = load_documents()
    enriched, errors, drift = enrich(rows, index)
    output_fields = list(fields)
    for field in NEW_COLUMNS:
        if field not in output_fields:
            output_fields.append(field)
    report = {
        "schema": "editorial-matrix-audit/v1",
        "matrix_path": MATRIX.relative_to(ROOT).as_posix(),
        "matrix_rows": len(rows),
        "canonical_documents": sum(len(values) for values in index.values()),
        "matched_rows": len(rows) - len(errors),
        "missing_or_ambiguous": errors,
        "drift": drift,
        "required_columns": list(NEW_COLUMNS),
        "policy": "matrix_scope_remains_editorial; canonical metadata is synchronized without adding documents",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.apply and not errors:
        with MATRIX.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=output_fields, delimiter=";", lineterminator="\n")
            writer.writeheader()
            writer.writerows(enriched)
    applied = bool(args.apply and not errors)
    print(json.dumps({"matrix_rows": len(rows), "canonical_documents": report["canonical_documents"], "matched_rows": report["matched_rows"], "errors": len(errors), "drift": len(drift), "applied": applied}, ensure_ascii=False))
    return 1 if errors or (drift and not args.apply) else 0


if __name__ == "__main__":
    raise SystemExit(main())
