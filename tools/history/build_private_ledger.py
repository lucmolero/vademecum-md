"""Export acquisition evidence to a separate private history directory.

This tool deliberately has no public-repository destination. The caller must
provide a private directory or a checked-out private history repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).parents[2]


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / ".private/acquisition")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.source.is_dir():
        raise SystemExit(f"Fonte privada ausente: {args.source}")
    args.output.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, object]] = []
    for source_path in sorted(args.source.rglob("*")):
        if not source_path.is_file():
            continue
        relative = source_path.relative_to(args.source)
        target = args.output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target)
        files.append({"path": relative.as_posix(), "bytes": target.stat().st_size, "sha256": digest(target)})
    manifest = {
        "schema": "private-acquisition-ledger/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(args.source),
        "files": files,
        "reproducibility": "raw snapshots and execution evidence copied without public publication",
    }
    (args.output / "ledger-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
