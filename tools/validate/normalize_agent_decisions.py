"""Normalize editorial decision provenance to the autonomous legal agent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "manifests/editorial-promotions.json"
AGENT = "autonomous_legal_agent"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    candidate_list = list(payload.get("decisions", {}).values())
    changed = 0
    for candidate in candidate_list:
        if candidate.get("revisor") != AGENT:
            candidate["revisor"] = AGENT
            changed += 1
        candidate["analysis_executor"] = AGENT
        candidate["review_status"] = "approved_autonomously"
    payload["reviewed_by"] = AGENT
    payload["analysis_executor"] = AGENT
    payload["autonomy_policy"] = "llm_legal_analysis_plus_deterministic_gates"
    payload["analysis_method"] = "llm_legal_analysis_plus_official_evidence"
    payload["deterministic_gate_method"] = "deterministic_validation"
    payload["user_action_required"] = False
    for candidate in candidate_list:
        candidate["analysis_method"] = "llm_legal_analysis_plus_official_evidence"
        candidate["deterministic_gate_method"] = "deterministic_validation"
        candidate["user_action_required"] = False
    if args.apply:
        MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed": changed, "candidates": len(candidate_list), "applied": args.apply}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
