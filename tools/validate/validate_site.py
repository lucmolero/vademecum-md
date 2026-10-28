"""Validate the rendered reader site accessibility baseline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML_TAG = re.compile(r"<html\b[^>]*\blang\s*=", re.IGNORECASE)
PT_BR_HTML = re.compile(r'<html\b[^>]*\blang\s*=\s*["\']pt-BR["\']', re.IGNORECASE)
IMAGE_WITHOUT_ALT = re.compile(r"<img\b(?![^>]*\balt\s*=)[^>]*>", re.IGNORECASE)
def _relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(foreground: str, background: str) -> float:
    first, second = sorted((_relative_luminance(foreground), _relative_luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def _dark_scheme_block(css_text: str) -> str | None:
    match = re.search(r'\[data-md-color-scheme="slate"\]\s*\{([^}]*)\}', css_text)
    return match.group(1) if match else None


def validate_dark_theme_contrast(css_text: str) -> list[str]:
    block = _dark_scheme_block(css_text)
    if block is None:
        return ['site stylesheet lacks the dark theme palette']

    properties = dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;", block))
    backgrounds = (properties.get("--md-default-bg-color"), properties.get("--vmd-paper"))
    if any(background is None for background in backgrounds):
        return ['dark theme palette lacks explicit page and paper backgrounds']

    errors: list[str] = []
    for token in ("--vmd-slate", "--vmd-green", "--vmd-amber", "--vmd-red", "--vmd-gold", "--vmd-ink-soft"):
        foreground = properties.get(token)
        if foreground is None:
            errors.append(f"dark theme palette lacks {token}")
            continue
        for background in backgrounds:
            if _contrast_ratio(foreground, background) < 4.5:
                errors.append(f"dark theme {token} fails 4.5:1 text contrast on {background}")
    return errors


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
        elif not PT_BR_HTML.search(text):
            errors.append(f"{relative}: expected lang=pt-BR")
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
    else:
        css_text = css.read_text(encoding="utf-8", errors="replace")
        errors.extend(validate_dark_theme_contrast(css_text))
        if "prefers-reduced-motion" not in css_text:
            errors.append("site stylesheet lacks reduced-motion policy")
        if ".vmd-hero" not in css_text or ".law-hero" not in css_text:
            errors.append("site stylesheet lacks product and reader surfaces")
    javascript = site / "javascripts" / "portfolio.js"
    if not javascript.is_file():
        errors.append("site interaction script missing")
    elif "prefers-reduced-motion" not in javascript.read_text(encoding="utf-8", errors="replace"):
        errors.append("site interaction script lacks reduced-motion detection")
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
