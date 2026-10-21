"""Build an autonomous disposition queue for unresolved relation targets.

The queue aggregates repeated citations without expanding the curated matrix.
The agent makes the disposition: altering/regulating acts remain historical;
targets without a unique official identity remain graph-only. No user action
is required and no unresolved citation is promoted as current law by inference.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from migrate_public_corpus import CURATED, parse_frontmatter  # noqa: E402


ROOT = Path(__file__).parents[2]
UNRESOLVED = ROOT / "bases/derived/relacoes/unresolved.json"
EXPANSION = ROOT / "manifests/editorial-expansion.csv"
PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2}
RELATION_RISK = {
    "revoga": "alto",
    "revogada_por": "alto",
    "retifica": "medio",
    "retificada_por": "medio",
    "altera": "medio",
    "alterada_por": "medio",
    "regulamenta": "baixo",
    "regulamentada_por": "baixo",
    "suspende": "alto",
    "suspensa_por": "alto",
    "relacionada_a": "baixo",
}
INVERSE_RELATIONS = {"alterada_por", "revogada_por", "retificada_por", "regulamentada_por", "suspensa_por"}
DIRECT_RELATIONS = {"altera", "revoga", "retifica", "regulamenta", "suspende", "relacionada_a"}


def load_priorities() -> dict[str, str]:
    priorities: dict[str, str] = {}
    for path in CURATED.rglob("*.md"):
        metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        if metadata.get("id"):
            priorities[str(metadata["id"])] = str(metadata.get("prioridade") or "P2")
    return priorities


def load_expansion_candidates() -> dict[str, dict[str, str]]:
    if not EXPANSION.is_file():
        return {}
    candidates: dict[str, dict[str, str]] = {}
    with EXPANSION.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter=";"):
            kind = str(row.get("tipo") or "")
            number = "".join(character for character in str(row.get("numero") or "") if character.isdigit())
            candidates[f"{kind}:{number}"] = row
    return candidates


def normalize_kind(value: object) -> str:
    return " ".join(str(value or "").lower().split())


def normalize_number(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def risk_for(relation_types: set[str]) -> str:
    levels = {"baixo": 0, "medio": 1, "alto": 2}
    risks = [RELATION_RISK.get(relation, "medio") for relation in relation_types]
    return max(risks, key=lambda risk: levels[risk]) if risks else "medio"


def role_for(relation_types: set[str]) -> str:
    if relation_types and relation_types <= INVERSE_RELATIONS:
        return "ato_alterador_ou_regulamentador"
    if relation_types and relation_types <= DIRECT_RELATIONS:
        return "diploma_referenciado"
    return "ambiguo"


def next_action_for(role: str) -> str:
    if role == "ato_alterador_ou_regulamentador":
        return "no_manual_action; preserve_as_historical_relation"
    if role == "diploma_referenciado":
        return "no_manual_action; preserve_in_graph_without_corpus_promotion"
    return "no_manual_action; preserve_in_graph_without_corpus_promotion"


def editorial_disposition_for(role: str) -> tuple[str, str, list[str], str]:
    if role == "ato_alterador_ou_regulamentador":
        return (
            "historico",
            "inverse relation indicates an altering, repealing or regulating act; no autonomous corpus promotion is implied",
            ["official_source_relation_in_curated_document", "historical_layer_default_for_altering_act"],
            "approved",
        )
    if role == "diploma_referenciado":
        return (
            "grafo",
            "direct reference lacks a unique official target snapshot; graph-only disposition prevents inferred current-law promotion",
            ["direct_relation_detected", "no_unique_official_target_snapshot", "corpus_promotion_rejected_by_agent"],
            "approved",
        )
    return (
        "grafo",
        "mixed or ambiguous relation language is retained as graph evidence without inferred corpus promotion",
        ["ambiguous_relation_language", "no_inferred_legal_effect", "corpus_promotion_rejected_by_agent"],
        "approved",
    )


def build_queue(unresolved: list[dict[str, object]], output: Path) -> dict[str, object]:
    priorities = load_priorities()
    expansion_candidates = load_expansion_candidates()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in unresolved:
        kind = normalize_kind(item.get("kind"))
        number = normalize_number(item.get("numero"))
        grouped[f"{kind}:{number}"].append(item)

    targets: list[dict[str, object]] = []
    for target_key, occurrences in grouped.items():
        relation_types = {str(item.get("tipo") or "") for item in occurrences}
        referenced_role = role_for(relation_types)
        source_ids = sorted({str(item.get("source_id") or "") for item in occurrences})
        source_priorities = sorted(
            {priorities.get(source_id, "P2") for source_id in source_ids},
            key=lambda value: PRIORITY_RANK.get(value, 9),
        )
        kind, number = target_key.split(":", 1)
        expansion_kind = {
            "lei": "lei_ordinaria",
            "lei complementar": "lei_complementar",
            "decreto-lei": "decreto_lei",
            "decreto": "decreto",
        }.get(kind, kind.replace(" ", "_"))
        expansion = expansion_candidates.get(f"{expansion_kind}:{''.join(character for character in number if character.isdigit())}")
        disposition, decision_reason, evidence, review_status = editorial_disposition_for(referenced_role)
        source_priority = source_priorities[0] if source_priorities else "P2"
        assessment = {
            "frequency": {
                "status": "observed",
                "occurrence_count": len(occurrences),
            },
            "p0_impact": {
                "status": "high" if source_priority == "P0" else "not_p0",
                "source_priority": source_priority,
            },
            "professional_relevance": "high_priority_source" if source_priority == "P0" else "contextual_reference",
            "official_source": (
                "source_document_relation"
                if referenced_role == "ato_alterador_ou_regulamentador"
                else "source_document_only_target_unresolved"
            ),
            "autonomy": (
                "not_applicable"
                if referenced_role == "ato_alterador_ou_regulamentador"
                else "not_demonstrated"
            ),
            "duplication_risk": "controlled_by_target_key",
            "actuality": "not_determined_without_target_snapshot",
            "legal_situation": "not_determined_without_target_snapshot",
        }
        targets.append({
            "target_id": "relation-target-" + hashlib.sha256(target_key.encode("utf-8")).hexdigest()[:16],
            "target_key": target_key,
            "referenced_kind": kind,
            "referenced_number": number,
            "occurrence_count": len(occurrences),
            "source_ids": source_ids,
            "source_priority": source_priority,
            "priority": source_priority,
            "relation_types": sorted(relation_types),
            "referenced_role": referenced_role,
            "risk": risk_for(relation_types),
            "requires_editorial_decision": False,
            "next_action": next_action_for(referenced_role),
            "expansion_candidate_id": expansion.get("id") if expansion else None,
            "expansion_status": expansion.get("status_aquisicao") if expansion else None,
            "expansion_source": expansion.get("fonte_oficial") if expansion else None,
            "disposition": disposition,
            "decision": disposition,
            "review_status": review_status,
            "decision_scope": "autonomous_agent_legal_curation",
            "analysis_method": "llm_legal_analysis_plus_deterministic_gates",
            "decision_reason": decision_reason,
            "evidence": evidence,
            "assessment": assessment,
            "occurrences": [
                {
                    "source_id": str(item.get("source_id") or ""),
                    "relation_type": str(item.get("tipo") or ""),
                    "referenced_kind": str(item.get("kind") or ""),
                    "referenced_number": str(item.get("numero") or ""),
                }
                for item in sorted(occurrences, key=lambda value: (str(value.get("source_id") or ""), str(value.get("tipo") or "")))
            ],
        })

    targets.sort(key=lambda item: (
        PRIORITY_RANK.get(str(item["source_priority"]), 9),
        {"alto": 0, "medio": 1, "baixo": 2}.get(str(item["risk"]), 9),
        -int(item["occurrence_count"]),
        str(item["target_key"]),
    ))
    result = {
        "schema": "unresolved-relation-review-queue/v1",
        "generated_at": date.today().isoformat(),
        "occurrence_count": len(unresolved),
        "unique_target_count": len(targets),
        "policy": "autonomous_disposition; no unresolved citation is promoted to the curated matrix by inference",
        "by_priority": dict(Counter(str(item["source_priority"]) for item in targets)),
        "by_risk": dict(Counter(str(item["risk"]) for item in targets)),
        "by_referenced_role": dict(Counter(str(item["referenced_role"]) for item in targets)),
        "by_expansion_status": dict(Counter(str(item["expansion_status"] or "sem_candidato_expansao") for item in targets)),
        "by_disposition": dict(Counter(str(item["disposition"]) for item in targets)),
        "decision_policy": "altering_or_regulating_acts are approved for history; direct or ambiguous references are approved for graph-only retention when unique official target evidence is absent; no manual decision is required",
        "targets": targets,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=UNRESOLVED)
    parser.add_argument("--output", type=Path, default=ROOT / "bases/derived/relacoes/review-queue.json")
    args = parser.parse_args()
    unresolved = json.loads(args.input.read_text(encoding="utf-8")) if args.input.is_file() else []
    result = build_queue(unresolved, args.output)
    print(json.dumps({key: result[key] for key in ("occurrence_count", "unique_target_count", "by_priority", "by_risk")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
