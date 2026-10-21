"""Audit graph completeness and relation-shape risks without changing data."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).parents[2]
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
    parser.add_argument("--strict", action="store_true", help="falha se houver conflito inverso ou duplicata")
    args = parser.parse_args()
    relations = [json.loads(line) for line in GRAPH.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_pair: dict[tuple[str, str], set[str]] = defaultdict(set)
    duplicates = Counter()
    for relation in relations:
        pair = (relation["source_id"], relation["target_id"])
        by_pair[pair].add(relation["type"])
        duplicates[json.dumps(relation, sort_keys=True)] += 1
    conflicts = []
    for pair, types in by_pair.items():
        for inverse in INVERSE_TYPES:
            if inverse.issubset(types):
                conflicts.append({"source_id": pair[0], "target_id": pair[1], "types": sorted(types)})
                break
    unresolved = json.loads(UNRESOLVED.read_text(encoding="utf-8")) if UNRESOLVED.is_file() else []
    report = {
        "schema": "normative-graph-audit/v1",
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
        "unresolved_candidates": len(unresolved),
        "policy": "audit_only; no relation is promoted without official textual evidence",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k: report[k] for k in ("relations", "without_device", "without_effect_date", "duplicate_records", "inverse_type_conflicts", "unresolved_candidates")}, ensure_ascii=False))
    if args.strict and (report["duplicate_records"] or report["inverse_type_conflicts"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
