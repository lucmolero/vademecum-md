"""Build the public, non-sensitive release baseline manifest."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

import sys

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from migrate_public_corpus import CURATED, parse_frontmatter  # noqa: E402


def read_matrix() -> list[dict[str, str]]:
    with (ROOT / "manifests/corpus.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def main() -> int:
    documents = []
    statuses: Counter[str] = Counter()
    situations: Counter[str] = Counter()
    p0_total = 0
    p0_ready = 0
    for path in sorted(CURATED.rglob("*.md")):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
        documents.append((path, metadata, body))
        statuses[str(metadata.get("consolidacao_status"))] += 1
        situations[str(metadata.get("situacao"))] += 1
        if metadata.get("prioridade") == "P0":
            p0_total += 1
            if metadata.get("consolidacao_status") in {"consolidada_fonte_oficial", "consolidada_reconciliada"}:
                p0_ready += 1

    matrix = read_matrix()
    graph = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    unresolved = ROOT / "bases/derived/relacoes/unresolved.json"
    relation_count = len(graph.read_text(encoding="utf-8").splitlines()) if graph.is_file() else 0
    unresolved_items = json.loads(unresolved.read_text(encoding="utf-8")) if unresolved.is_file() else []
    queue_path = ROOT / "bases/derived/relacoes/review-queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8")) if queue_path.is_file() else {}
    expansion_rows = []
    with (ROOT / "manifests/editorial-expansion.csv").open(encoding="utf-8-sig", newline="") as stream:
        expansion_rows = list(csv.DictReader(stream, delimiter=";"))
    promotion = json.loads((ROOT / "manifests/editorial-promotions.json").read_text(encoding="utf-8"))
    workflow_count = len(list((ROOT / ".github/workflows").glob("*.yml")))
    test_count = sum(
        len(re.findall(r"^\s+def test_", path.read_text(encoding="utf-8"), re.MULTILINE))
        for path in sorted((ROOT / "tests").rglob("test_*.py"))
    )

    corpus_by_id = {str(metadata.get("id")): path.relative_to(ROOT).as_posix() for path, metadata, _ in documents}
    matrix_by_document = {str(row.get("document_id")): str(row.get("document_path")) for row in matrix}
    source_manifest_path = ROOT / "manifests/sources-official.json"
    source_manifest_ids: set[str] = set()
    if source_manifest_path.is_file():
        source_manifest_ids = {
            str(item.get("id"))
            for item in json.loads(source_manifest_path.read_text(encoding="utf-8")).get("documents", [])
        }
    divergences: list[dict[str, object]] = []
    for identifier in sorted(set(corpus_by_id) ^ set(matrix_by_document)):
        divergences.append({"type": "corpus_matrix_id_drift", "id": identifier})
    for identifier in sorted(set(corpus_by_id) & set(matrix_by_document)):
        expected_path = matrix_by_document[identifier].replace("\\", "/")
        if corpus_by_id[identifier] != expected_path:
            divergences.append({"type": "matrix_path_drift", "id": identifier, "matrix": expected_path, "actual": corpus_by_id[identifier]})
    for identifier in sorted(set(corpus_by_id) ^ source_manifest_ids):
        divergences.append({"type": "source_manifest_id_drift", "id": identifier})
    completeness_path = ROOT / "manifests/completeness.json"
    if completeness_path.is_file():
        completeness = json.loads(completeness_path.read_text(encoding="utf-8"))
        if int(completeness.get("corpus_count", -1)) != len(documents):
            divergences.append({"type": "completeness_count_drift", "expected": len(documents), "actual": completeness.get("corpus_count")})
    divergence_report = {
        "schema": "baseline-divergence/v1",
        "generated_at": date.today().isoformat(),
        "scope": "corpus_matrix_sources_and_completeness",
        "divergence_count": len(divergences),
        "status": "pass" if not divergences else "fail",
        "divergences": divergences,
    }
    divergence_target = ROOT / "bases/derived/relatorios/baseline-divergence.json"
    divergence_target.parent.mkdir(parents=True, exist_ok=True)
    divergence_target.write_text(json.dumps(divergence_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    result = {
        "schema": "vademecum-baseline/v1",
        "generated_at": date.today().isoformat(),
        "scope": "legislacao_federal_curada",
        "corpus_count": len(documents),
        "matrix_count": len(matrix),
        "integral_count": sum(bool(body.strip()) for _, _, body in documents),
        "official_source_count": sum(bool(metadata.get("fonte_oficial")) for _, metadata, _ in documents),
        "hash_count": sum(bool(metadata.get("sha256_origem")) for _, metadata, _ in documents),
        "consolidation_status": dict(statuses),
        "situations": dict(situations),
        "p0": {"ready": p0_ready, "total": p0_total},
        "relation_count": relation_count,
        "unresolved_relation_occurrences": len(unresolved_items),
        "relation_target_count": int(queue.get("unique_target_count", 0)),
        "relation_disposition": queue.get("by_disposition", {}),
        "editorial_expansion": {
            "candidate_count": len(expansion_rows),
            "promoted_count": sum(1 for item in promotion.get("decisions", {}).values() if item.get("decision") == "promote"),
            "undecided_count": sum(1 for row in expansion_rows if row.get("status_cobertura") != "promovido_corpus"),
        },
        "workflow_count": workflow_count,
        "test_count": test_count,
        "divergence_report": "bases/derived/relatorios/baseline-divergence.json",
        "divergence_count": len(divergences),
        "status": "pass" if len(documents) == len(matrix) and p0_ready == p0_total and not divergences else "fail",
    }
    target = ROOT / "manifests/baseline.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
