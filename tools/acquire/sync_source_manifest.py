"""Synchronize official acquisition hashes into the public source manifest.

The collection report is the evidence ledger for a completed official fetch.
This command updates only hashes and consultation dates; it never changes the
curated Markdown.  Conflicts require an approved source-resolution manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parents[2]
MANIFEST = ROOT / "manifests/sources-official.json"


def selected_attempt(item: dict[str, object], resolutions: dict[str, object]) -> dict[str, object] | None:
    attempts = [attempt for attempt in item.get("attempts", []) if attempt.get("status") == "fetched"]
    resolution = resolutions.get(str(item.get("matrix_id")))
    if isinstance(resolution, dict) and resolution.get("status") == "approved":
        source_id = str(resolution.get("selected_source_id") or "")
        expected = str(resolution.get("expected_source_sha256") or "")
        return next((attempt for attempt in attempts if attempt.get("source_id") == source_id and attempt.get("sha256_raw") == expected), None)
    if len(attempts) == 1:
        return attempts[0]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-report", type=Path, required=True)
    parser.add_argument("--source-resolution", type=Path, required=True)
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(args.collection_report.read_text(encoding="utf-8"))
    resolution_payload = json.loads(args.source_resolution.read_text(encoding="utf-8"))
    resolutions = resolution_payload.get("documents", {})
    entries = {str(item.get("id")): item for item in manifest.get("documents", [])}
    updated: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for item in report.get("results", []):
        document_id = str(item.get("document_id") or "")
        if not document_id or document_id not in entries:
            skipped.append({"matrix_id": item.get("matrix_id"), "reason": "manifest_entry_missing"})
            continue
        attempt = selected_attempt(item, resolutions)
        if not attempt:
            if item.get("comparison_mode") == "complementary_sources":
                attempts = [candidate for candidate in item.get("attempts", []) if candidate.get("status") == "fetched"]
                if attempts and all(
                    all(re.fullmatch(r"[0-9a-f]{64}", str(candidate.get(field) or "")) for field in ("sha256_raw", "sha256_normalized", "sha256_body"))
                    for candidate in attempts
                ):
                    entry = entries[document_id]
                    entry["hash_scope"] = "per_source"
                    entry["sha256_origem_por_fonte"] = [
                        {"fonte": candidate.get("url"), "sha256": candidate.get("sha256_raw")}
                        for candidate in attempts
                    ]
                    entry["sha256_corpo_por_fonte"] = [
                        {
                            "fonte": candidate.get("url"),
                            "sha256_normalizado": candidate.get("sha256_normalized"),
                            "sha256_corpo": candidate.get("sha256_body"),
                        }
                        for candidate in attempts
                    ]
                    updated.append({
                        "matrix_id": item.get("matrix_id"),
                        "document_id": document_id,
                        "source_scope": "per_source",
                        "source_count": len(attempts),
                    })
                    continue
            reason = "complementary_sources_require_composite_baseline" if item.get("comparison_mode") == "complementary_sources" else "unresolved_source_selection"
            skipped.append({"matrix_id": item.get("matrix_id"), "document_id": document_id, "reason": reason})
            continue
        raw_hash = str(attempt.get("sha256_raw") or "")
        normalized_hash = str(attempt.get("sha256_normalized") or "")
        body_hash = str(attempt.get("sha256_body") or "")
        if not all(re.fullmatch(r"[0-9a-f]{64}", value) for value in (raw_hash, normalized_hash, body_hash)):
            skipped.append({"matrix_id": item.get("matrix_id"), "document_id": document_id, "reason": "invalid_acquisition_hash"})
            continue
        entry = entries[document_id]
        entry.update({
            "data_consulta": args.as_of,
            "data_corte": str(report.get("as_of") or args.as_of),
            "sha256_origem": raw_hash,
            "sha256_normalizado": normalized_hash,
            "sha256_corpo": body_hash,
        })
        updated.append({
            "matrix_id": item.get("matrix_id"),
            "document_id": document_id,
            "source_id": attempt.get("source_id"),
            "sha256_origem": raw_hash,
            "sha256_corpo": body_hash,
        })

    body_count = sum(bool(item.get("sha256_corpo")) for item in entries.values())
    result = {
        "schema": "official-source-manifest-sync/v1",
        "mode": "apply" if args.apply else "dry_run",
        "collection_report": str(args.collection_report.relative_to(ROOT)) if args.collection_report.is_relative_to(ROOT) else str(args.collection_report),
        "updated_count": len(updated),
        "skipped_count": len(skipped),
        "body_hash_count_after": body_count,
        "updated": updated,
        "skipped": skipped,
        "policy": "official_fetch_evidence_only; curated_text_immutable; conflicts_require_resolution",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    strict_skips = [item for item in skipped if item.get("reason") != "complementary_sources_require_composite_baseline"]
    if args.strict and strict_skips:
        print(json.dumps({"mode": result["mode"], "updated_count": len(updated), "skipped_count": len(skipped)}, ensure_ascii=False))
        return 1
    if args.apply:
        ordered = [entries[str(item.get("id"))] for item in manifest.get("documents", [])]
        manifest["generated_at"] = args.as_of
        manifest["documents"] = ordered
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"mode": result["mode"], "updated_count": len(updated), "skipped_count": len(skipped), "body_hash_count_after": body_count}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
