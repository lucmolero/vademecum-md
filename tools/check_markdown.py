"""Validação básica, sem dependências externas, das bases Markdown locais."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path("bases"))
    args = parser.parse_args()

    files = sorted(args.root.rglob("*.md"))
    errors: list[str] = []
    for path in files:
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{path}: UTF-8 inválido ({exc})")

    print(f"Arquivos Markdown: {len(files)}")
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Validação UTF-8: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
