"""Generate a deterministic freshness and source-coverage report."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path

from collect_legislation import build_plan, output_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    plan = build_plan(args.as_of)
    stale = [item for item in plan if item["stale"]]
    missing = [item for item in plan if item["status"] == "source_missing"]
    report = {
        "schema": "legislation-monitor-report/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "as_of": args.as_of.isoformat(),
        "matrix_count": len(plan),
        "fresh_count": len(plan) - len(stale),
        "stale_count": len(stale),
        "source_missing_count": len(missing),
        "policy": {"P0": "daily", "P1": "weekly", "P2": "monthly"},
        "stale": stale,
        "source_missing": missing,
    }
    output_report(report, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
