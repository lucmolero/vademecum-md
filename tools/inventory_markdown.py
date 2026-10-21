"""Gera inventário determinístico de arquivos Markdown locais."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path("bases"))
    parser.add_argument("--output", type=Path, default=Path("manifests/markdown-inventory.jsonl"))
    args = parser.parse_args()

    files = sorted(path for path in args.root.rglob("*.md") if path.is_file())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for path in files:
            handle.write(
                json.dumps(
                    {
                        "path": path.as_posix(),
                        "bytes": path.stat().st_size,
                        "sha256": digest(path),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )
    print(f"Inventário gerado: {len(files)} arquivos -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
