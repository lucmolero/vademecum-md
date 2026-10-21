"""Audit graph completeness and relation-shape risks without changing data."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from migrate_public_corpus import CURATED, parse_frontmatter  # noqa: E402
GRAPH = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
UNRESOLVED = ROOT / "bases/derived/relacoes/unresolved.json"
REPORT = ROOT / "bases/history/alteracoes/2026-10-21-graph-audit.json"

INVERSE_TYPES = {
    frozenset(("altera", "alterada_por")),
    frozenset(("revoga", "revogada_por")),
    frozenset(("regulamenta", "regulamentada_por")),
    frozenset(("retifica", "retificada_por")),
    frozenset(("suspende", "suspensa_por")),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="falha se houver qualquer inconsistência estrutural")
    args = parser.parse_args()
    relations = [json.loads(line) for line in GRAPH.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_pair: dict[tuple[str, str], set[str]] = defaultdict(set)
    edge_keys: set[tuple[str, str, str]] = set()
    duplicates = Counter()
    for relation in relations:
        pair = (relation["source_id"], relation["target_id"])
        by_pair[pair].add(relation["type"])
        edge_keys.add((relation["source_id"], relation["type"], relation["target_id"]))
        duplicates[json.dumps(relation, sort_keys=True)] += 1
    conflicts = []
    for pair, types in by_pair.items():
        for inverse in INVERSE_TYPES:
            if inverse.issubset(types):
                conflicts.append({"source_id": pair[0], "target_id": pair[1], "types": sorted(types)})
                break
    unresolved = json.loads(UNRESOLVED.read_text(encoding="utf-8")) if UNRESOLVED.is_file() else []
    missing_inverse = []
    for relation in relations:
        inverse = None
        for pair in INVERSE_TYPES:
            if relation.get("type") in pair:
                inverse = next((item for item in pair if item != relation.get("type")), None)
                break
        if inverse and relation.get("status_relacao_inversa") == "excluded_by_policy":
            continue
        if inverse and (relation.get("target_id"), inverse, relation.get("source_id")) not in edge_keys:
            missing_inverse.append({
                "source_id": relation.get("source_id"),
                "type": relation.get("type"),
                "target_id": relation.get("target_id"),
            })
    corpus_ids = set()
    for path in CURATED.rglob("*.md"):
        try:
            metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
            if metadata.get("id"):
                corpus_ids.add(str(metadata["id"]))
        except (OSError, ValueError):
            continue
    missing_ids = [
        {"source_id": r.get("source_id"), "target_id": r.get("target_id")}
        for r in relations
        if r.get("source_id") not in corpus_ids or r.get("target_id") not in corpus_ids
    ]
    confidence_mismatches = [
        {"source_id": r.get("source_id"), "target_id": r.get("target_id"), "type": r.get("type")}
        for r in relations
        if (r.get("confianca") == "alta" and (not r.get("dispositivo") or not r.get("data_efeito")))
        or (r.get("confianca") == "media" and not r.get("evidencia_textual"))
    ]
    report = {
        "schema": "normative-graph-audit/v2",
        "generated_at": "2026-10-21",
        "relations": len(relations),
        "relation_types": dict(Counter(r["type"] for r in relations)),
        "without_device": sum(r.get("dispositivo") is None for r in relations),
        "without_effect_date": sum(r.get("data_efeito") is None for r in relations),
        "without_evidence": sum(not r.get("evidencia_textual") or not r.get("evidencia_sha256") for r in relations),
        "confidence": dict(Counter(str(r.get("confianca") or "desconhecida") for r in relations)),
        "review_status": dict(Counter(str(r.get("status_revisao") or "ausente") for r in relations)),
        "duplicate_records": sum(count - 1 for count in duplicates.values() if count > 1),
        "inverse_type_conflicts": len(conflicts),
        "inverse_type_conflict_examples": conflicts[:100],
        "missing_inverse_relations": len(missing_inverse),
        "missing_inverse_examples": missing_inverse[:100],
        "missing_document_ids": len(missing_ids),
        "missing_document_id_examples": missing_ids[:100],
        "confidence_mismatches": len(confidence_mismatches),
        "confidence_mismatch_examples": confidence_mismatches[:100],
        "unresolved_candidates": len(unresolved),
        "policy": "deterministic_shape_audit; legal meaning remains under autonomous legal curation",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k: report[k] for k in ("relations", "without_device", "without_effect_date", "duplicate_records", "inverse_type_conflicts", "unresolved_candidates")}, ensure_ascii=False))
    if args.strict and any(report[key] for key in (
        "duplicate_records", "inverse_type_conflicts", "missing_inverse_relations",
        "missing_document_ids", "confidence_mismatches",
    )):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
