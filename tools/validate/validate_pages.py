"""Validate the composed homepage, official library and release metadata for Pages."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def validate(site: Path) -> list[str]:
    errors: list[str] = []
    home = site / "index.html"
    library = site / "biblioteca/index.html"
    catalog_path = site / "biblioteca/catalog.json"
    release_path = site / "vademecum-release.json"
    metadata_path = site / "biblioteca/vademecum-source.json"
    for path in (home, library, catalog_path, release_path, metadata_path, site / ".nojekyll", site / "sw.js"):
        if not path.is_file():
            errors.append(f"required Pages file missing: {path.relative_to(site).as_posix()}")
    if errors:
        return errors

    home_html = home.read_text(encoding="utf-8", errors="replace")
    library_html = library.read_text(encoding="utf-8", errors="replace")
    if '<html lang="pt-BR"' not in home_html or 'id="root"' not in home_html:
        errors.append("homepage root or Portuguese document language is missing")
    home_scripts = [site / item.removeprefix("./") for item in re.findall(r'<script[^>]+src="(\./assets/[^"]+\.js)"', home_html)]
    if not home_scripts:
        errors.append("homepage JavaScript bundle is missing")
    elif not any(("biblioteca/" in path.read_text(encoding="utf-8", errors="replace")) for path in home_scripts):
        errors.append("homepage JavaScript bundle does not link to the library")
    homepage_source = ROOT / "homepage/src/main.tsx"
    if not homepage_source.is_file() or "skip-link" not in homepage_source.read_text(encoding="utf-8", errors="replace") or '<main id="conteudo">' not in homepage_source.read_text(encoding="utf-8", errors="replace"):
        errors.append("homepage source lacks its skip link or main landmark")
    if '<html lang="pt-BR"' not in library_html or '<main id="library"' not in library_html:
        errors.append("library app shell or Portuguese document language is missing")
    if not (site / "biblioteca/sw.js").is_file():
        errors.append("library-scoped service worker is missing")

    for document, html in (("homepage", home_html), ("biblioteca", library_html)):
        for asset in re.findall(r'(?:src|href)="(\./[^\"]+)"', html):
            target = site / document / asset[2:] if document == "biblioteca" else site / asset[2:]
            if not target.is_file():
                errors.append(f"{document} asset referenced but missing: {asset}")

    try:
        release = json.loads(release_path.read_text(encoding="utf-8"))
        source = json.loads(metadata_path.read_text(encoding="utf-8"))
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [*errors, f"invalid Pages release metadata or catalog: {error}"]
    expected = release.get("documentCount")
    version = release.get("version")
    if release.get("schema") != "vademecum-pages-release/v1":
        errors.append("unsupported Pages release metadata schema")
    if not isinstance(version, str) or source.get("version") != version or source.get("release") != version:
        errors.append("homepage and library do not identify the same corpus release")
    if release.get("applications", {}).get("homepage", {}).get("version") != version or release.get("applications", {}).get("library", {}).get("version") != version:
        errors.append("application metadata diverges from the corpus version")
    if source.get("documentCount") != expected or len(catalog) != expected:
        errors.append("library document count differs from the corpus release")
    if any(item.get("collection") != "vademecum" for item in catalog):
        errors.append("test or local Markdown is present in the production catalog")
    ids = [item.get("id") for item in catalog]
    if len(set(ids)) != len(ids) or any(not value for value in ids):
        errors.append("production catalog contains duplicate or empty IDs")
    for item in catalog:
        if not item.get("sourceHash"):
            errors.append(f"source hash missing for {item.get('id', 'unknown')}")
        if not (site / "biblioteca" / str(item.get("file", ""))).is_file():
            errors.append(f"book payload missing for {item.get('id', 'unknown')}")

    catalog_docs = site / "generated/catalog/index.html"
    if not catalog_docs.is_file():
        errors.append("governance catalog route was not preserved")
    if (site / "generated/atlas").exists():
        errors.append("legacy Atlas data was included in the Pages output")
    if not (site / "reader/index.html").is_file() or "biblioteca" not in (site / "reader/index.html").read_text(encoding="utf-8", errors="replace"):
        errors.append("legacy reader route does not redirect to the official library")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    errors = validate(args.site)
    print(json.dumps({"errors": errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
