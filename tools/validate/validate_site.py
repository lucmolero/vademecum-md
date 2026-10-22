"""Validate the rendered reader site accessibility baseline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML_TAG = re.compile(r"<html\b[^>]*\blang\s*=", re.IGNORECASE)
IMAGE_WITHOUT_ALT = re.compile(r"<img\b(?![^>]*\balt\s*=)[^>]*>", re.IGNORECASE)


def validate(site: Path) -> list[str]:
    errors: list[str] = []
    files = sorted(site.rglob("*.html")) if site.is_dir() else []
    if not files:
        return ["rendered site has no HTML files"]
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(site).as_posix()
        if not HTML_TAG.search(text):
            errors.append(f"{relative}: missing lang attribute")
        if 'data-md-component="skip"' not in text:
            errors.append(f"{relative}: missing skip link")
        if not re.search(r"<main\b", text, re.IGNORECASE):
            errors.append(f"{relative}: missing main landmark")
        if not re.search(r"<h1\b", text, re.IGNORECASE):
            errors.append(f"{relative}: missing primary heading")
        if IMAGE_WITHOUT_ALT.search(text):
            errors.append(f"{relative}: image without alt attribute")
    css = site / "stylesheets" / "extra.css"
    if not css.is_file():
        errors.append("site stylesheet missing")
    elif ":focus" not in css.read_text(encoding="utf-8", errors="replace"):
        errors.append("site stylesheet lacks visible focus styling")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    errors = validate(args.site)
    print(json.dumps({"html_files": len(list(args.site.rglob("*.html"))) if args.site.is_dir() else 0, "errors": errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
