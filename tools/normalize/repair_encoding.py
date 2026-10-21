"""Repair demonstrable UTF-8/Latin-1 mojibake in public text artifacts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).parents[2]
MARKERS = ("Ã", "Â", "â€", "â€“", "â€”", "�")
EXTENSIONS = {".md", ".json", ".csv", ".toml", ".yml", ".yaml"}


def score(value: str) -> int:
    return sum(value.count(marker) for marker in MARKERS)


def candidate(value: str) -> str | None:
    pattern = re.compile(r"(?:Ã.|Â.|â..)")
    repaired = value
    for _ in range(2):
        def replace(match: re.Match[str]) -> str:
            try:
                return match.group(0).encode("latin-1").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                return match.group(0)
        updated = pattern.sub(replace, repaired)
        if updated == repaired:
            break
        repaired = updated
    return repaired if score(repaired) < score(value) else None


def public_targets() -> list[Path]:
    targets: set[Path] = set()
    for relative in ("bases/curated", "docs", "manifests"):
        directory = ROOT / relative
        targets.update(path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in EXTENSIONS)
    for relative in ("README.md", "SECURITY.md", "LICENSE.md"):
        targets.add(ROOT / relative)
    return sorted(path for path in targets if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", type=Path, default=ROOT / ".private/normalization/encoding-repair.json")
    args = parser.parse_args()
    changes: list[dict[str, object]] = []
    for path in public_targets():
        original = path.read_text(encoding="utf-8", errors="replace")
        repaired = candidate(original)
        if repaired is None:
            continue
        item = {"path": path.relative_to(ROOT).as_posix(), "markers_before": score(original), "markers_after": score(repaired)}
        changes.append(item)
        if args.apply:
            path.write_text(repaired, encoding="utf-8", newline="\n")
    report = {
        "schema": "encoding-repair-report/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "changed_files": len(changes),
        "changes": changes,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed_files": len(changes), "mode": report["mode"], "report": str(args.report)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
