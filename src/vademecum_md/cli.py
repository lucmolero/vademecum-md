"""Single entry point for the VadeMecum MD operational commands."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

from . import __version__

COMMANDS = {
    "acquire": Path("tools/acquire/collect_legislation.py"),
    "normalize": Path("tools/normalize/official_html_to_markdown.py"),
    "audit": Path("tools/audit_fidelity.py"),
    "graph": Path("tools/build_public_indexes.py"),
    "site": Path("tools/site/build_site.py"),
    "release": Path("tools/validate_release.py"),
}


def find_workspace_root(start: Path) -> Path | None:
    """Find a checkout root from a file or directory inside that checkout."""
    location = start.resolve()
    if location.is_file():
        location = location.parent
    for candidate in (location, *location.parents):
        if (
            (candidate / "pyproject.toml").is_file()
            and (candidate / "tools" / "site" / "build_site.py").is_file()
            and (candidate / "manifests" / "corpus.csv").is_file()
        ):
            return candidate
    return None


def _workspace_root() -> Path | None:
    """Prefer the caller's checkout, then the checkout containing an editable install."""
    return find_workspace_root(Path.cwd()) or find_workspace_root(Path(__file__).resolve())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vademecum", description="Operações do VadeMecum MD")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("command", choices=sorted(COMMANDS))
    args, rest = parser.parse_known_args(argv)
    root = _workspace_root()
    if root is None:
        parser.error(
            "os comandos operacionais exigem um checkout do VadeMecum MD "
            "(pyproject.toml, tools/ e manifests/corpus.csv); execute dentro de um clone. "
            "A opção --version funciona sem checkout."
        )
    relative_target = COMMANDS[args.command]
    target = root / relative_target
    if not target.is_file():
        parser.error(f"implementação do comando ausente no checkout: {relative_target.as_posix()}")
    old_argv = sys.argv
    try:
        sys.argv = [str(target), *rest]
        runpy.run_path(str(target), run_name="__main__")
    finally:
        sys.argv = old_argv
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
