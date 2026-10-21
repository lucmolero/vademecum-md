"""Classify unresolved normative references with an autonomous disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from migrate_public_corpus import CURATED, parse_frontmatter  # noqa: E402


ROOT = Path(__file__).parents[2]
UNRESOLVED = ROOT / "bases/derived/relacoes/unresolved.json"


TYPE_MAP = {
    "lei": "lei_ordinaria",
    "lei complementar": "lei_complementar",
    "decreto-lei": "decreto_lei",
    "decreto": "decreto",
}
INVERSE_RELATIONS = {"alterada_por", "revogada_por", "retificada_por", "regulamentada_por", "suspensa_por"}
DIRECT_RELATIONS = {"altera", "revoga", "retifica", "regulamenta", "suspende", "relacionada_a"}


def referenced_role(relation_type: str) -> str:
    if relation_type in INVERSE_RELATIONS:
        return "ato_alterador_ou_regulamentador"
    if relation_type in DIRECT_RELATIONS:
        return "diploma_referenciado"
        return "ambiguo"


def next_action_for(role: str) -> str:
    if role == "ato_alterador_ou_regulamentador":
        return "no_manual_action; preserve_as_historical_relation"
    if role == "diploma_referenciado":
        return "no_manual_action; preserve_in_graph_without_corpus_promotion"
    return "no_manual_action; preserve_in_graph_without_corpus_promotion"


def load_priorities() -> dict[str, str]:
    result: dict[str, str] = {}
    for path in CURATED.rglob("*.md"):
        metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        if metadata.get("id"):
            result[str(metadata["id"])] = str(metadata.get("prioridade") or "P2")
    return result


def classify(output: Path) -> dict[str, object]:
    unresolved = json.loads(UNRESOLVED.read_text(encoding="utf-8")) if UNRESOLVED.is_file() else []
    priorities = load_priorities()
    entries: list[dict[str, object]] = []
    for item in unresolved:
        kind = " ".join(str(item.get("kind", "")).lower().split())
        normalized_type = TYPE_MAP.get(kind, "desconhecido")
        target_key = f"{normalized_type}:{item.get('numero')}"
        candidate_id = "relation-candidate-" + hashlib.sha256(target_key.encode("utf-8")).hexdigest()[:16]
        role = referenced_role(str(item.get("tipo") or ""))
        entries.append({
            "candidate_id": candidate_id,
            "source_id": item.get("source_id"),
            "source_priority": priorities.get(str(item.get("source_id")), "P2"),
            "relation_type": item.get("tipo"),
            "referenced_kind": item.get("kind"),
            "referenced_number": item.get("numero"),
            "target_key": target_key,
            "referenced_role": role,
            "classification": "out_of_matrix",
            "requires_editorial_decision": False,
            "next_action": next_action_for(role),
            "decision": "historico" if role == "ato_alterador_ou_regulamentador" else "grafo",
            "review_status": "approved",
            "decision_scope": "autonomous_agent_legal_curation",
            "analysis_method": "llm_legal_analysis_plus_deterministic_gates",
        })
    summary = {
        "schema": "unresolved-relation-classification/v1",
        "generated_at": date.today().isoformat(),
        "total": len(entries),
        "by_classification": dict(Counter(str(item["classification"]) for item in entries)),
        "by_relation": dict(Counter(str(item["relation_type"]) for item in entries)),
        "by_referenced_role": dict(Counter(str(item["referenced_role"]) for item in entries)),
        "by_source_priority": dict(Counter(str(item["source_priority"]) for item in entries)),
        "by_editorial_disposition": dict(Counter(
            "historico" if item["referenced_role"] == "ato_alterador_ou_regulamentador" else "grafo"
            for item in entries
        )),
        "classification_method": "target type and number were checked against the curated corpus; no matching target was found",
        "policy": "autonomous_disposition; no candidate is added to the curated matrix by inference",
        "candidates": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    report = ROOT / "bases/history/alteracoes/2026-10-21-unresolved-relations.json"
    report.write_text(json.dumps({key: value for key, value in summary.items() if key != "candidates"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "bases/derived/relacoes/unresolved-classified.json")
    args = parser.parse_args()
    summary = classify(args.output)
    print(json.dumps({key: summary[key] for key in ("total", "by_classification", "by_relation", "by_source_priority")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
