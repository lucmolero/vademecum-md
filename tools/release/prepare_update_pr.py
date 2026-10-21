"""Prepare an auditable update proposal; never writes curated documents."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from pipeline_modes import load_modes, resolve_mode  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--proposal-markdown", type=Path)
    parser.add_argument("--diff-index", type=Path)
    parser.add_argument("--diff-dir", type=Path)
    parser.add_argument("--source-resolution", type=Path, help="agent-reviewed official-source selections for conflicts")
    parser.add_argument("--mode", choices=("dry_run", "proposal"), default="proposal")
    args = parser.parse_args()
    load_modes()
    mode = resolve_mode(args.mode)
    report = json.loads(args.collection_report.read_text(encoding="utf-8"))
    diff_index = json.loads(args.diff_index.read_text(encoding="utf-8")) if args.diff_index and args.diff_index.is_file() else {}
    diff_by_matrix = {str(item.get("matrix_id")): item for item in diff_index.get("documents", [])}
    resolutions = {}
    if args.source_resolution and args.source_resolution.is_file():
        resolutions = json.loads(args.source_resolution.read_text(encoding="utf-8")).get("documents", {})
    results = report.get("results", [])
    changed = [item for item in results if item.get("status") == "changed_candidate" and item.get("sha256_raw")]
    conflicts = [item for item in results if item.get("status") == "source_conflict"]
    resolved_conflicts = [
        item for item in conflicts
        if isinstance(resolutions.get(str(item.get("matrix_id"))), dict)
        and resolutions[str(item.get("matrix_id"))].get("status") == "approved"
    ]
    unresolved_conflicts = [item for item in conflicts if item not in resolved_conflicts]
    unavailable = [item for item in results if item.get("status") == "source_unavailable"]
    invalid_sources = [item for item in results if item.get("status") == "source_invalid"]
    evidence = []
    for item in changed + resolved_conflicts + unresolved_conflicts + unavailable + invalid_sources:
        diff = diff_by_matrix.get(str(item.get("matrix_id")), {})
        evidence.append({
            **item,
            "diff": diff,
            "risk": diff.get("risco", "critico"),
            "relations_impacted": diff.get("relacoes_impactadas", 0),
        })
    blockers = []
    if unresolved_conflicts:
        blockers.append("source_conflict")
    if unavailable:
        blockers.append("source_unavailable")
    if invalid_sources:
        blockers.append("source_invalid")
    if any(not diff_by_matrix.get(str(item.get("matrix_id"))) for item in changed + resolved_conflicts):
        blockers.append("missing_structural_diff")
    proposal = {
        "schema": "legislation-update-proposal/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "autonomous_agent_review_and_deterministic_gates",
        "mode": mode,
        "curated_mutation": False,
        "eligible_for_autonomous_update": len(changed) + len(resolved_conflicts) > 0 and not blockers,
        "release_blockers": blockers,
        "risk_summary": dict(Counter(str(item["risk"]) for item in evidence)),
        "changed_candidates": [item for item in evidence if item.get("status") == "changed_candidate"],
        "resolved_conflicts": [item for item in evidence if item.get("matrix_id") in {str(value.get("matrix_id")) for value in resolved_conflicts}],
        "conflicts": unresolved_conflicts,
        "unavailable": unavailable,
        "invalid_sources": invalid_sources,
        "next_step": "apply autonomous source decisions and deterministic gates, then create the reproducible update PR",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.proposal_markdown and (changed or conflicts or unavailable or invalid_sources):
        args.proposal_markdown.parent.mkdir(parents=True, exist_ok=True)
        public_diff_dir = args.proposal_markdown.parent / "diffs"
        if args.diff_dir and args.diff_dir.is_dir():
            public_diff_dir.mkdir(parents=True, exist_ok=True)
            for diff_file in args.diff_dir.glob("*.json"):
                shutil.copy2(diff_file, public_diff_dir / diff_file.name)
        lines = [
            "# Proposta de atualização normativa",
            "",
            "Esta proposta foi gerada automaticamente, analisada pelo agente e validada pelos gates determinísticos. Ela não altera o corpus curado por si só.",
            "",
            f"- Candidatos com hash diferente: **{len(changed)}**",
            f"- Conflitos entre fontes sem resolução: **{len(unresolved_conflicts)}**",
            f"- Conflitos com decisão de fonte registrada: **{len(resolved_conflicts)}**",
            f"- Fontes indisponíveis: **{len(unavailable)}**",
            "",
            "## Candidatos",
            "",
            "| Matriz | Status | Risco | Hash atual | Novo hash | Diff | Artigos | Relações | Fonte principal |",
            "| --- | --- | --- | --- | --- | --- | ---: | ---: | --- |",
        ]
        for item in changed + resolved_conflicts + unresolved_conflicts + unavailable + invalid_sources:
            diff = diff_by_matrix.get(str(item.get("matrix_id")), {})
            diff_label = diff.get("status", "n/a")
            if diff.get("status") == "generated":
                diff_label = f"generated; artigos alterados={diff.get('artigos_alterados', 0)}; {', '.join(diff.get('classificacao', []))}"
            diff_cell = f"[{diff_label}](diffs/{item.get('matrix_id')}.json)" if diff else diff_label
            lines.append(
                f"| `{item.get('matrix_id')}` | `{item.get('status')}` | `{diff.get('risco', 'critico')}` | "
                f"`{item.get('current_sha256') or 'n/a'}` | `{item.get('sha256_raw') or 'n/a'}` | "
                f"{diff_cell} | "
                f"{diff.get('artigos_alterados', 0) + diff.get('artigos_adicionados', 0) + diff.get('artigos_removidos', 0)} | "
                f"{diff.get('relacoes_impactadas', 0)} | "
                f"{item.get('primary_url') or 'n/a'} |"
            )
        lines.extend([
            "",
            "## Checklist de revisão",
            "",
            "- [ ] Confirmar a fonte oficial e a data de corte.",
            "- [ ] Confirmar hash bruto e hash normalizado.",
            "- [ ] Gerar e revisar diff por artigo, parágrafo, inciso e alínea.",
            "- [ ] Confirmar vigência, veto, retificação, revogação e efeitos.",
            "- [ ] Atualizar relações normativas e manifests derivados.",
            "- [ ] Executar os gates de release antes do merge.",
        ])
        args.proposal_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"changed_candidates": len(changed), "unavailable": len(unavailable), "invalid_sources": len(invalid_sources), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
