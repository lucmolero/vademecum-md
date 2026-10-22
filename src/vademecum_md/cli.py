"""Single entry point for the VadeMecum MD operational commands."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

from . import __version__

ROOT = Path(__file__).resolve().parents[2]
COMMANDS = {
    "acquire": ROOT / "tools/acquire/collect_legislation.py",
    "normalize": ROOT / "tools/normalize/official_html_to_markdown.py",
    "audit": ROOT / "tools/audit_fidelity.py",
    "graph": ROOT / "tools/build_public_indexes.py",
    "site": ROOT / "tools/site/build_site.py",
    "release": ROOT / "tools/validate_release.py",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vademecum", description="Operações do VadeMecum MD")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("command", choices=sorted(COMMANDS))
    args, rest = parser.parse_known_args(argv)
    target = COMMANDS[args.command]
    if not target.is_file():
        parser.error(f"comando não disponível: {target}")
    old_argv = sys.argv
    try:
        sys.argv = [str(target), *rest]
        runpy.run_path(str(target), run_name="__main__")
    finally:
        sys.argv = old_argv
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
