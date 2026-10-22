"""Validate the rendered reader site accessibility baseline."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parents[2]
HTML_TAG = re.compile(r"<html\b[^>]*\blang\s*=", re.IGNORECASE)
PT_BR_HTML = re.compile(r'<html\b[^>]*\blang\s*=\s*["\']pt-BR["\']', re.IGNORECASE)
IMAGE_WITHOUT_ALT = re.compile(r"<img\b(?![^>]*\balt\s*=)[^>]*>", re.IGNORECASE)
SOCIAL_CARD_PAGES = (
    "index.html",
    "generated/catalog/index.html",
    "audiences/index.html",
    "methodology/index.html",
    "architecture/index.html",
    "graph/index.html",
    "sources/index.html",
    "quality/index.html",
    "faq/index.html",
    "portfolio/index.html",
    "updates/index.html",
)


class _LinkCollector(HTMLParser):
    """Collect IDs and link destinations in one pass without building a DOM tree."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: Counter[str] = Counter()
        self.hrefs: list[str] = []
        self.interactive: list[dict[str, object]] = []
        self.unnamed_interactive: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        identifier = values.get("id")
        if identifier:
            self.ids[identifier] += 1
        href = values.get("href")
        if href is not None:
            self.hrefs.append(href)
        if tag in {"a", "button"}:
            self.interactive.append({"tag": tag, "attrs": values, "text": ""})
        elif tag == "img" and values.get("alt") is not None:
            for item in self.interactive:
                item["text"] = str(item["text"]) + " " + str(values["alt"])

    def handle_data(self, data: str) -> None:
        for item in self.interactive:
            item["text"] = str(item["text"]) + data

    def handle_endtag(self, tag: str) -> None:
        if tag not in {"a", "button"}:
            return
        for index in range(len(self.interactive) - 1, -1, -1):
            item = self.interactive[index]
            if item["tag"] != tag:
                continue
            self.interactive.pop(index)
            attrs = item["attrs"]
            accessible_text = " ".join(str(item["text"]).split())
            labels = (attrs.get("aria-label"), attrs.get("title"))
            if not accessible_text and not any(str(label or "").strip() for label in labels):
                self.unnamed_interactive.append(tag)
            break


def validate_internal_links(site: Path, site_url: str) -> list[str]:
    """Check local href destinations and HTML fragments across the rendered site."""
    errors: list[str] = []
    base_url = site_url.rstrip("/") + "/"
    base = urlparse(base_url)
    base_path = base.path.rstrip("/") + "/"
    pages = sorted(site.rglob("*.html"))
    records: dict[Path, tuple[Counter[str], list[str]]] = {}

    for page in pages:
        parser = _LinkCollector()
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        relative = page.relative_to(site).as_posix()
        for identifier, occurrences in parser.ids.items():
            if occurrences > 1:
                errors.append(f"{relative}: duplicate HTML id ({identifier})")
        for tag in parser.unnamed_interactive:
            errors.append(f"{relative}: {tag} missing accessible name")
        records[page.resolve()] = (parser.ids, parser.hrefs)

    target_cache: dict[str, Path | None] = {}
    for page in pages:
        relative = page.relative_to(site).as_posix()
        current_url = urljoin(base_url, relative)
        _, hrefs = records[page.resolve()]
        for href in hrefs:
            href = href.strip()
            if not href:
                continue
            target_url = urlparse(urljoin(current_url, href))
            if target_url.scheme not in ("http", "https"):
                continue
            if target_url.netloc and target_url.netloc.lower() != base.netloc.lower():
                continue
            if not target_url.path.startswith(base_path):
                errors.append(f"{relative}: internal link escapes site base ({href})")
                continue

            target_key = unquote(target_url.path[len(base_path):])
            if not target_key:
                target_key = "index.html"
            candidate = target_cache.get(target_key)
            if candidate is None and target_key not in target_cache:
                normalized = target_key.rstrip("/") or "index.html"
                possible = site / normalized
                if target_key.endswith("/") or not Path(target_key).suffix:
                    possible = site / normalized / "index.html"
                candidate = possible if possible.is_file() else None
                target_cache[target_key] = candidate
            if candidate is None:
                errors.append(f"{relative}: missing internal link target ({href})")
                continue
            if target_url.fragment and candidate.suffix.lower() == ".html":
                target_ids = records.get(candidate.resolve(), (set(), []))[0]
                if unquote(target_url.fragment) not in target_ids:
                    errors.append(f"{relative}: missing internal link fragment ({href})")
    return errors


def validate_social_cards(site: Path, site_url: str) -> list[str]:
    errors: list[str] = []
    base_path = urlparse(site_url).path.rstrip("/") + "/"
    for page_name in SOCIAL_CARD_PAGES:
        page = site / page_name
        if not page.is_file():
            errors.append(f"{page_name}: social-card page missing")
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        image_match = re.search(
            r'<meta\s+property="og:image"\s+content="([^"]+)"', text, re.IGNORECASE
        )
        if not image_match:
            errors.append(f"{page_name}: missing Open Graph image")
            continue
        image_url = image_match.group(1)
        image_path = urlparse(image_url).path
        if not image_path.startswith(base_path):
            errors.append(f"{page_name}: social image URL is outside the configured site path")
            continue
        card = site / unquote(image_path[len(base_path):])
        if not card.is_file():
            errors.append(f"{page_name}: social image file missing ({card.relative_to(site).as_posix()})")
        elif not card.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append(f"{page_name}: social image is not a valid PNG")
        if not re.search(r'<meta\s+property="twitter:card"\s+content="summary_large_image"', text, re.IGNORECASE):
            errors.append(f"{page_name}: missing large-image Twitter card metadata")
        for property_name in ("og:title", "og:description", "og:url"):
            if not re.search(rf'<meta\s+property="{re.escape(property_name)}"\s+content="[^"]+"', text, re.IGNORECASE):
                errors.append(f"{page_name}: missing {property_name} metadata")
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
        if "prefers-reduced-motion" not in css_text:
            errors.append("site stylesheet lacks reduced-motion policy")
        if ".vmd-hero" not in css_text or ".law-hero" not in css_text:
            errors.append("site stylesheet lacks product and reader surfaces")
    javascript = site / "javascripts" / "portfolio.js"
    if not javascript.is_file():
        errors.append("site interaction script missing")
    elif "prefers-reduced-motion" not in javascript.read_text(encoding="utf-8", errors="replace"):
        errors.append("site interaction script lacks reduced-motion detection")
    config_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    site_url_match = re.search(r"^site_url:\s*['\"]?([^'\"\r\n]+)", config_text, re.MULTILINE)
    site_url = site_url_match.group(1).strip() if site_url_match else ""
    if site_url.startswith("https://"):
        errors.extend(validate_internal_links(site, site_url))
    else:
        errors.append("internal-link validation requires an HTTPS site_url")
    if os.environ.get("VMD_REQUIRE_SOCIAL_CARDS") == "1":
        if not site_url.startswith("https://"):
            errors.append("social-card validation requires an HTTPS site_url")
        else:
            errors.extend(validate_social_cards(site, site_url))
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
