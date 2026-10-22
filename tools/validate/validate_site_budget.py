"""Enforce compressed transfer budgets for the homepage and legal pages."""

from __future__ import annotations

import argparse
import gzip
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parents[2]
MAX_HOME_GZIP_BYTES = 120 * 1024
MAX_SEARCH_INDEX_GZIP_BYTES = 80 * 1024
MAX_SINGLE_LAW_GZIP_BYTES = 300 * 1024


class _ResourceCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.resources: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "script" and values.get("src"):
            self.resources.add(str(values["src"]))
        elif tag == "link" and values.get("href"):
            rel = set(str(values.get("rel") or "").lower().split())
            if "stylesheet" in rel or "icon" in rel:
                self.resources.add(str(values["href"]))
        elif tag in {"img", "source"} and values.get("src"):
            self.resources.add(str(values["src"]))
        if values.get("srcset"):
            for candidate in str(values["srcset"]).split(","):
                source = candidate.strip().split()
                if source:
                    self.resources.add(source[0])


def _gzip_size(payload: bytes) -> int:
    return len(gzip.compress(payload, compresslevel=9, mtime=0))


def _site_base(site_url: str) -> tuple[str, str]:
    parsed = urlparse(site_url)
    return parsed.netloc.lower(), parsed.path.rstrip("/") + "/"


def _homepage_resources(site: Path, site_url: str, homepage: Path) -> tuple[list[Path], list[str]]:
    parser = _ResourceCollector()
    parser.feed(homepage.read_text(encoding="utf-8", errors="replace"))
    base_host, base_path = _site_base(site_url)
    paths: set[Path] = set()
    errors: list[str] = []
    for reference in parser.resources:
        target = urlparse(urljoin(site_url.rstrip("/") + "/", reference))
        if target.scheme not in {"http", "https"} or target.netloc.lower() != base_host:
            continue
        if not target.path.startswith(base_path):
            continue
        relative = unquote(target.path[len(base_path):]).lstrip("/")
        asset = (site / relative).resolve()
        if not asset.is_relative_to(site.resolve()):
            errors.append(f"homepage resource escapes site root: {reference}")
        elif not asset.is_file():
            errors.append(f"homepage resource missing: {reference}")
        else:
            paths.add(asset)
    return sorted(paths), errors


def _site_url() -> str:
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    match = re.search(r"^site_url:\s*['\"]?([^'\"\r\n]+)", config, re.MULTILINE)
    return match.group(1).strip() if match else ""


def validate(site: Path) -> dict[str, object]:
    errors: list[str] = []
    homepage = site / "index.html"
    search_index = site / "generated" / "search-index.json"
    if not homepage.is_file():
        return {"errors": ["homepage is missing"], "ok": False}
    if not search_index.is_file():
        errors.append("deferred search index is missing")

    site_url = _site_url()
    if not site_url.startswith("https://"):
        return {"errors": errors + ["performance validation requires an HTTPS site_url"], "ok": False}

    resources, resource_errors = _homepage_resources(site, site_url, homepage)
    errors.extend(resource_errors)
    home_bytes = homepage.read_bytes()
    initial_gzip_bytes = _gzip_size(home_bytes) + sum(_gzip_size(path.read_bytes()) for path in resources)
    search_gzip_bytes = _gzip_size(search_index.read_bytes()) if search_index.is_file() else 0

    law_pages = [
        path for path in (site / "generated" / "laws").rglob("index.html")
        if "federal" in path.relative_to(site).parts
    ]
    if not law_pages:
        errors.append("no generated federal law pages found")
    law_sizes = [( _gzip_size(path.read_bytes()), path.relative_to(site).as_posix()) for path in law_pages]
    max_law_gzip_bytes, max_law_page = max(law_sizes, default=(0, ""))

    if initial_gzip_bytes > MAX_HOME_GZIP_BYTES:
        errors.append(
            f"homepage initial resources exceed {MAX_HOME_GZIP_BYTES} gzip bytes "
            f"({initial_gzip_bytes})"
        )
    if search_gzip_bytes > MAX_SEARCH_INDEX_GZIP_BYTES:
        errors.append(
            f"deferred search index exceeds {MAX_SEARCH_INDEX_GZIP_BYTES} gzip bytes "
            f"({search_gzip_bytes})"
        )
    if max_law_gzip_bytes > MAX_SINGLE_LAW_GZIP_BYTES:
        errors.append(
            f"largest law page exceeds {MAX_SINGLE_LAW_GZIP_BYTES} gzip bytes "
            f"({max_law_gzip_bytes}: {max_law_page})"
        )

    return {
        "ok": not errors,
        "errors": errors,
        "budgets_gzip_bytes": {
            "homepage_initial_resources": MAX_HOME_GZIP_BYTES,
            "deferred_search_index": MAX_SEARCH_INDEX_GZIP_BYTES,
            "largest_single_law_page": MAX_SINGLE_LAW_GZIP_BYTES,
        },
        "measurements_gzip_bytes": {
            "homepage_html": _gzip_size(home_bytes),
            "homepage_initial_resources": initial_gzip_bytes,
            "deferred_search_index": search_gzip_bytes,
            "largest_single_law_page": max_law_gzip_bytes,
        },
        "homepage_resources": [path.relative_to(site).as_posix() for path in resources],
        "largest_law_page": max_law_page,
        "federal_law_pages": len(law_pages),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    result = validate(args.site)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
