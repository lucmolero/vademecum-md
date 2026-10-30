"""Validate the composed homepage, official library and release metadata for Pages."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _parse_gray_color(value: str) -> tuple[int, int, int] | None:
    value = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))
    match = re.fullmatch(r"oklch\(\s*([0-9.]+)\s+0(?:\.0+)?\s+0(?:deg)?\s*\)", value)
    if not match:
        return None
    linear = float(match.group(1)) ** 3
    channel = 12.92 * linear if linear <= 0.0031308 else 1.055 * linear ** (1 / 2.4) - 0.055
    value8 = round(max(0, min(1, channel)) * 255)
    return (value8, value8, value8)


def _contrast_ratio(left: tuple[int, int, int], right: tuple[int, int, int]) -> float:
    def luminance(color: tuple[int, int, int]) -> float:
        channels = [channel / 255 for channel in color]
        linear = [item / 12.92 if item <= 0.04045 else ((item + 0.055) / 1.055) ** 2.4 for item in channels]
        return sum(weight * item for weight, item in zip((0.2126, 0.7152, 0.0722), linear, strict=True))

    a, b = sorted((luminance(left), luminance(right)), reverse=True)
    return (a + 0.05) / (b + 0.05)


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
    homepage_css = (ROOT / "homepage/src/global.css").read_text(encoding="utf-8", errors="replace")
    muted_match = re.search(r"--muted:\s*([^;]+);", homepage_css)
    muted_foreground_match = re.search(r"--muted-foreground:\s*([^;]+);", homepage_css)
    muted = _parse_gray_color(muted_match.group(1)) if muted_match else None
    muted_foreground = _parse_gray_color(muted_foreground_match.group(1)) if muted_foreground_match else None
    if muted is None or muted_foreground is None or _contrast_ratio(muted_foreground, muted) < 4.5:
        errors.append("homepage muted text fails the WCAG AA contrast threshold on its muted surface")
    hero_title = (ROOT / "homepage/src/components/hero-title.tsx").read_text(encoding="utf-8", errors="replace")
    if "initial: { opacity: 1" not in hero_title or "animate: { opacity: 1" not in hero_title:
        errors.append("homepage hero heading fades through low-contrast states during its entrance animation")
    hero_source = (ROOT / "homepage/src/components/hero.tsx").read_text(encoding="utf-8", errors="replace")
    if "initial:{opacity:1,y:20" not in hero_source or "animate:done?{opacity:1" not in hero_source:
        errors.append("homepage hero copy fades through low-contrast states during its entrance animation")
    if '<html lang="pt-BR"' not in library_html or '<main id="library"' not in library_html:
        errors.append("library app shell or Portuguese document language is missing")
    if not (site / "biblioteca/sw.js").is_file():
        errors.append("library-scoped service worker is missing")
    library_source = (ROOT / "biblioteca/src/library.js").read_text(encoding="utf-8", errors="replace")
    if "cover.setAttribute('aria-hidden','true')" not in library_source or "role','progressbar'" not in library_source:
        errors.append("library book controls expose decorative cover text or omit semantic reading progress")

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
