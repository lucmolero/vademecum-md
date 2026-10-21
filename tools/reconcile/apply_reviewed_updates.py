"""Apply an agent-reviewed batch of official current compilations to the corpus.

This tool only promotes candidates that have a successful official snapshot and
an autonomous source decision. Ambiguous candidates are classified and left in
their safe current layer; no item is marked blocked for user action.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "history"))
sys.path.insert(0, str(ROOT / "tools" / "normalize"))

from build_candidate_diffs import current_document  # noqa: E402
from build_structural_diffs import article_diff  # noqa: E402
from migrate_public_corpus import frontmatter, parse_frontmatter  # noqa: E402
from official_html_to_markdown import convert  # noqa: E402
from pipeline_modes import load_modes, resolve_mode  # noqa: E402


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_matrix() -> list[dict[str, str]]:
    with (ROOT / "manifests/corpus.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def document_path(document_id: str) -> Path | None:
    found = current_document(document_id)
    return found[0] if found else None


def reviewed_candidate(item: dict[str, object], priority: str, as_of: str) -> tuple[bool, str]:
    if str(item.get("prioridade")) != priority:
        return False, "priority_out_of_scope"
    if item.get("status") == "source_conflict":
        return False, "source_conflict"
    if item.get("status") != "changed_candidate":
        return False, f"status_{item.get('status', 'unknown')}"
    if not item.get("snapshot_file") or not item.get("sha256_raw"):
        return False, "snapshot_or_hash_missing"
    return True, "official_current_compilation_without_source_conflict"


def selected_attempt(item: dict[str, object], resolution: dict[str, object] | None) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    """Return the reviewed official attempt and its resolution, if any."""
    selected_source_id = str((resolution or {}).get("selected_source_id") or "")
    attempts = [attempt for attempt in item.get("attempts", []) if attempt.get("status") == "fetched"]
    if selected_source_id:
        return next((attempt for attempt in attempts if attempt.get("source_id") == selected_source_id), None), resolution
    return (attempts[0] if attempts else None), resolution


def usable_resolution(item: dict[str, object], resolution: object) -> dict[str, object] | None:
    if not isinstance(resolution, dict) or resolution.get("status") != "approved":
        return None
    selected_source_id = str(resolution.get("selected_source_id") or "")
    expected_hash = str(resolution.get("expected_source_sha256") or "")
    for attempt in item.get("attempts", []):
        if attempt.get("status") != "fetched":
            continue
        if selected_source_id and attempt.get("source_id") != selected_source_id:
            continue
        if expected_hash and attempt.get("sha256_raw") != expected_hash:
            continue
        return resolution
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--priority", choices=("P0", "P1", "P2"), default="P0")
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--apply", action="store_true", help="write reviewed documents and synchronize the matrix")
    parser.add_argument("--mark-blocked", action="store_true", help="deprecated compatibility flag; preserve the current document and record the source issue")
    parser.add_argument("--source-resolution", type=Path, help="agent-reviewed official-source selections for conflicts")
    parser.add_argument("--only-pending", action="store_true", help="process only matrix rows marked requer_reconciliacao")
    parser.add_argument("--matrix-id", action="append", dest="matrix_ids", help="limit the reviewed application to one or more matrix IDs")
    parser.add_argument("--legal-consensus", type=Path, help="autonomous curator/critic consensus ledger")
    parser.add_argument("--mode", choices=("dry_run", "apply_reviewed"), help="explicit application mode; --apply is a compatibility alias")
    args = parser.parse_args()
    load_modes()
    try:
        mode = resolve_mode(args.mode, legacy_mutation=args.apply)
    except ValueError as error:
        parser.error(str(error))
    if mode == "apply_reviewed":
        args.apply = True

    consensus: dict[str, object] = {}
    if args.legal_consensus and args.legal_consensus.is_file():
        consensus = json.loads(args.legal_consensus.read_text(encoding="utf-8"))
    consensus_by_id = {str(item.get("document_id")): item for item in consensus.get("documents", [])}

    report = json.loads(args.collection_report.read_text(encoding="utf-8"))
    matrix = load_matrix()
    by_matrix = {row["id"]: row for row in matrix}
    resolutions = {}
    if args.source_resolution and args.source_resolution.is_file():
        payload = json.loads(args.source_resolution.read_text(encoding="utf-8"))
        resolutions = payload.get("documents", {})
    applied: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []

    for item in report.get("results", []):
        matrix_id = str(item.get("matrix_id", ""))
        if args.matrix_ids and matrix_id not in set(args.matrix_ids):
            continue
        row = by_matrix.get(matrix_id)
        if args.only_pending and (not row or row.get("status_consolidacao") != "requer_reconciliacao"):
            continue
        resolution = resolutions.get(matrix_id)
        legal_decision = consensus_by_id.get(str(item.get("document_id") or ""))
        if args.apply and (not legal_decision or legal_decision.get("consensus") is not True or legal_decision.get("decision") != "promote"):
            skipped.append({"matrix_id": matrix_id, "reason": "legal_curator_critic_consensus_missing"})
            continue
        approved_resolution = usable_resolution(item, resolution)
        if args.mark_blocked and not approved_resolution and str(item.get("prioridade")) == args.priority and item.get("status") in {"source_conflict", "source_unavailable", "source_invalid"}:
            skipped.append({"matrix_id": matrix_id, "reason": "source_issue_preserved_current_document"})
            continue
        accepted, reason = reviewed_candidate(item, args.priority, args.as_of)
        if approved_resolution and str(item.get("status")) == "source_conflict" and str(item.get("prioridade")) == args.priority:
            accepted, reason = True, "approved_source_resolution"
        if not accepted:
            if str(item.get("prioridade")) == args.priority:
                if isinstance(resolution, dict) and resolution.get("status") == "approved" and str(item.get("status")) == "source_conflict":
                    reason = "source_resolution_hash_mismatch"
                skipped.append({"matrix_id": matrix_id, "reason": reason})
            continue
        document_id = str(item.get("document_id") or "")
        path = document_path(document_id)
        attempt, _ = selected_attempt(item, approved_resolution)
        if not attempt or not attempt.get("snapshot_file"):
            skipped.append({"matrix_id": matrix_id, "reason": "selected_source_snapshot_missing"})
            continue
        snapshot = ROOT / str(attempt["snapshot_file"])
        if not path or not snapshot.is_file():
            skipped.append({"matrix_id": matrix_id, "reason": "document_or_snapshot_missing"})
            continue
        metadata, old_body = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
        try:
            candidate_body = convert(snapshot, "auto")
        except (OSError, ValueError, UnicodeError) as error:
            skipped.append({"matrix_id": matrix_id, "reason": "conversion_failed", "detail": str(error)})
            continue
        structure = article_diff(old_body, candidate_body)["artigos"]
        if int(structure["total_atual"]) == 0 or len(candidate_body) < max(500, int(len(old_body) * 0.4)):
            skipped.append({"matrix_id": matrix_id, "reason": "candidate_truncation_guard", "structure": structure})
            continue
        metadata["data_corte"] = args.as_of
        metadata["baixado_em"] = args.as_of
        metadata["origem_formato"] = "html"
        metadata["sha256_origem"] = attempt.get("sha256_raw") or item.get("sha256_raw")
        metadata["sha256_normalizado"] = attempt.get("sha256_normalized")
        metadata["sha256_corpo"] = attempt.get("sha256_body")
        metadata["canonicalization_version"] = "norm-v2"
        metadata["source_unit_id"] = str(metadata.get("source_unit_id") or document_id)
        metadata["source_unit_selector"] = metadata.get("source_unit_selector") or {
            "selector_type": "full_official_document",
            "selector": {},
            "unit_scope": "single_diploma",
        }
        metadata["fidelity_status"] = "review"
        metadata["fidelity_anomalies"] = ["post_update_fidelity_audit_required"]
        metadata["hash_scope"] = {
            "sha256_source_raw": "official_snapshot_bytes",
            "sha256_source_normalized": "selected_source_text_norm_v2",
            "sha256_source_body": "selected_normative_body_norm_v2",
            "sha256_published_body": "published_normative_body_norm_v2",
        }
        metadata["sha256_source_raw"] = str(attempt.get("sha256_raw") or item.get("sha256_raw") or "")
        metadata["sha256_source_normalized"] = str(attempt.get("sha256_normalized") or sha256_text(candidate_body))
        metadata["sha256_source_body"] = str(attempt.get("sha256_body") or sha256_text(candidate_body))
        metadata["sha256_published_body"] = sha256_text(candidate_body)
        metadata["consolidacao_status"] = "consolidada_fonte_oficial"
        title = str(metadata.get("titulo") or path.stem)
        new_text = frontmatter(metadata) + "\n\n# " + title + "\n\n" + candidate_body
        entry = {
            "matrix_id": matrix_id,
            "document_id": document_id,
            "path": path.relative_to(ROOT).as_posix(),
            "source": attempt.get("url") or item.get("primary_url"),
            "source_id": attempt.get("source_id"),
            "sha256_raw": attempt.get("sha256_raw") or item.get("sha256_raw"),
            "structure": structure,
            "review": reason,
        }
        if approved_resolution:
            entry["resolution"] = approved_resolution
        applied.append(entry)
        if args.apply:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            if row:
                row["data_corte"] = args.as_of
                row["sha256_origem"] = str(attempt.get("sha256_raw") or item.get("sha256_raw"))
                row["status_consolidacao"] = "consolidada_fonte_oficial"
                row["status_atualidade"] = "confirmada"
                row["status_situacao"] = str(metadata.get("situacao") or row.get("status_situacao") or "desconhecida")

    if args.apply:
        matrix_path = ROOT / "manifests/corpus.csv"
        with matrix_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(matrix[0]), delimiter=";", lineterminator="\n")
            writer.writeheader()
            writer.writerows(matrix)

    result = {
        "schema": "reviewed-update-application/v1",
        "mode": mode,
        "priority": args.priority,
        "as_of": args.as_of,
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "applied": applied,
        "skipped": skipped,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("mode", "priority", "applied_count", "skipped_count")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
