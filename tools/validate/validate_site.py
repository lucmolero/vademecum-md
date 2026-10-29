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
    css_paths = [site / "stylesheets" / name for name in ("extra.css", "launch.css")]
    missing_css = [path.name for path in css_paths if not path.is_file()]
    if missing_css:
        errors.append(f"site stylesheet missing: {', '.join(missing_css)}")
    else:
        css_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in css_paths)
        if ":focus" not in css_text:
            errors.append("site stylesheet lacks visible focus styling")
        else:
            errors.extend(validate_dark_theme_contrast(css_text))
        if "prefers-reduced-motion" not in css_text:
            errors.append("site stylesheet lacks reduced-motion policy")
        if ".vmd-hero" not in css_text or ".law-hero" not in css_text or ".vmd-reader-app" not in css_text:
            errors.append("site stylesheet lacks product, legacy and integrated reader surfaces")
        for theme, foreground, background in (
            ("paper", "#272b26", "#fffefa"),
            ("sepia", "#302a21", "#f7f0e3"),
            ("night", "#e9e7de", "#202621"),
        ):
            if _contrast_ratio(foreground, background) < 7:
                errors.append(f"reader {theme} text contrast is below 7:1")
    javascript = site / "javascripts" / "portfolio.js"
    if not javascript.is_file():
        errors.append("site interaction script missing")
    elif "prefers-reduced-motion" not in javascript.read_text(encoding="utf-8", errors="replace"):
        errors.append("site interaction script lacks reduced-motion detection")
    reader_script = site / "javascripts" / "reader.js"
    if not reader_script.is_file() or "initIntegratedReader" not in reader_script.read_text(encoding="utf-8", errors="replace"):
        errors.append("integrated reader interaction script is missing")
    reader_index = site / "generated" / "reader-data" / "index.json"
    if reader_index.is_file():
        try:
            index = json.loads(reader_index.read_text(encoding="utf-8"))
            if index.get("schema") != "vademecum-reader-index/v1":
                errors.append("reader index has an unsupported schema")
            documents = index.get("documents", [])
            if len(documents) != index.get("document_count"):
                errors.append("reader index document count does not match its entries")
            if not documents:
                errors.append("reader index is empty")
            data_dir = reader_index.parent / "documents"
            if len(list(data_dir.glob("*.json"))) != len(documents):
                errors.append("reader document payload count does not match the index")
            for item in documents:
                payload_path = data_dir / f'{item.get("id", "")}.json'
                if not payload_path.is_file():
                    errors.append(f"reader payload missing for {item.get('id', 'unknown')}")
                    continue
                try:
                    payload = json.loads(payload_path.read_text(encoding="utf-8"))
                    if payload.get("id") != item.get("id") or payload.get("schema") != "vademecum-reader-document/v1":
                        errors.append(f"reader payload identity/schema mismatch: {payload_path.name}")
                    if re.search(r"<(?:script|iframe|object|svg|math)\b", payload.get("article_html", ""), re.IGNORECASE):
                        errors.append(f"reader payload contains active markup: {payload_path.name}")
                except (OSError, json.JSONDecodeError) as error:
                    errors.append(f"invalid reader payload {payload_path.name}: {error}")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid reader index: {error}")
    else:
        errors.append("integrated reader index is missing")
    reader_page = site / "reader" / "index.html"
    if not reader_page.is_file() or 'data-reader-app' not in reader_page.read_text(encoding="utf-8", errors="replace"):
        errors.append("rendered integrated reader page is missing its app shell")
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
