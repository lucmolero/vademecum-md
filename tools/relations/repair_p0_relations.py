"""Remove relations disproved during the P0 source reconciliation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
GRAPH = ROOT / "bases/derived/relacoes/normative-graph.jsonl"


INVALID = {
    ("br-federal-lei_complementar-225-2026", "revogada_por", "br-federal-lei_ordinaria-10637-2002"),
    ("br-federal-lei_complementar-225-2026", "revogada_por", "br-federal-lei_ordinaria-13105-2015"),
    ("br-federal-lei_ordinaria-10637-2002", "revoga", "br-federal-lei_complementar-225-2026"),
    ("br-federal-lei_ordinaria-10637-2002", "revogada_por", "br-federal-lei_complementar-225-2026"),
    ("br-federal-lei_ordinaria-13105-2015", "revoga", "br-federal-lei_complementar-225-2026"),
}


def main() -> int:
    lines = GRAPH.read_text(encoding="utf-8").splitlines()
    kept = []
    removed = []
    for line in lines:
        relation = json.loads(line)
        key = (relation["source_id"], relation["type"], relation["target_id"])
        if key in INVALID:
            removed.append(relation)
        else:
            kept.append(line)
    GRAPH.write_text("\n".join(kept) + "\n", encoding="utf-8", newline="\n")
    print(f"Relações removidas: {len(removed)}; restantes: {len(kept)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
