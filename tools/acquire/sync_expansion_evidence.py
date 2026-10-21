"""Synchronize private acquisition evidence into the public expansion inventory.

Only official-source hashes and acquisition status are published. Raw snapshots
remain private; explicit promotions remain marked as corpus entries.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
INVENTORY = ROOT / "manifests/editorial-expansion.csv"
DEFAULT_REPORT = ROOT / "reports/editorial-expansion-collection.json"
EVIDENCE_COLUMNS = (
    "status_aquisicao", "data_aquisicao", "sha256_origem", "sha256_corpo", "fonte_oficial_count",
)
HASH_FIELDS = ("sha256_origem", "sha256_corpo")


def load_rows() -> tuple[list[dict[str, str]], list[str]]:
    with INVENTORY.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        return list(reader), list(reader.fieldnames or [])


def enrich(rows: list[dict[str, str]], report: dict[str, object]) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    results = {str(item.get("matrix_id")): item for item in report.get("results", [])}
    drift: list[dict[str, object]] = []
    enriched: list[dict[str, str]] = []
    acquired_at = str(report.get("generated_at") or "")[:10]
    for row in rows:
        if row.get("status_aquisicao") == "promovido_corpus":
            enriched.append(dict(row))
            continue
        result = results.get(str(row.get("id")))
        if not result:
            drift.append({"id": row.get("id"), "kind": "missing_collection_result"})
            enriched.append(dict(row))
            continue
        status = str(result.get("status") or "")
        if status == "changed_candidate":
            acquisition_status = "adquirido_pendente_reconciliacao"
            integrity_status = "texto_oficial_adquirido"
            raw_hash = str(result.get("sha256_raw") or "")
            body_hash = str(result.get("sha256_body") or "")
        else:
            acquisition_status = status or "desconhecido"
            integrity_status = row.get("status_integridade", "nao_adquirido")
            raw_hash = ""
            body_hash = ""
        item = dict(row)
        item.update({
            "status_aquisicao": acquisition_status,
            "data_aquisicao": acquired_at,
            "sha256_origem": raw_hash,
            "sha256_corpo": body_hash,
            "fonte_oficial_count": str(result.get("source_count") or "0"),
            "status_integridade": integrity_status,
            "status_atualidade": "pendente_reconciliacao",
        })
        for field in (*EVIDENCE_COLUMNS, "status_integridade", "status_atualidade"):
            if str(row.get(field) or "") != str(item.get(field) or ""):
                drift.append({"id": row.get("id"), "field": field, "actual": row.get(field, ""), "expected": item.get(field, "")})
        enriched.append(item)
    return enriched, drift


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--apply", action="store_true", help="write evidence into the public inventory")
    args = parser.parse_args()
    rows, fields = load_rows()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    enriched, drift = enrich(rows, report)
    output_fields = list(fields)
    for field in EVIDENCE_COLUMNS:
        if field not in output_fields:
            output_fields.append(field)
    errors: list[str] = []
    for row in enriched:
        if row.get("status_aquisicao") == "adquirido_pendente_reconciliacao":
            for field in HASH_FIELDS:
                if not re.fullmatch(r"[0-9a-f]{64}", row.get(field, "")):
                    errors.append(f"{row.get('id')}: hash inválido em {field}")
    applied = bool(args.apply and not errors)
    if applied:
        with INVENTORY.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=output_fields, delimiter=";", lineterminator="\n")
            writer.writeheader()
            writer.writerows(enriched)
    payload = {
        "schema": "editorial-expansion-evidence/v1",
        "inventory_path": INVENTORY.relative_to(ROOT).as_posix(),
        "collection_report": args.report.relative_to(ROOT).as_posix() if args.report.is_relative_to(ROOT) else str(args.report),
        "rows": len(rows),
        "drift": drift,
        "errors": errors,
        "applied": applied,
        "policy": "official_hashes_public; raw_snapshots_private; candidate_texts_not_curated",
    }
    print(json.dumps({"rows": len(rows), "drift": len(drift), "errors": len(errors), "applied": applied}, ensure_ascii=False))
    return 1 if errors or (drift and not args.apply) else 0


if __name__ == "__main__":
    raise SystemExit(main())
