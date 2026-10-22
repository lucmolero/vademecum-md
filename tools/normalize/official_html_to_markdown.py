"""Convert an official Brazilian legislation HTML page to clean Markdown.

The converter is intentionally local-only: it never fetches URLs.  Acquisition
and legal source selection remain separate responsibilities.  It accepts the
legacy Latin-1 pages used by the official legislation portal and emits UTF-8
Markdown with one source paragraph per Markdown block.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from bs4 import BeautifulSoup


BLOCKED_TAGS = ("script", "style", "noscript", "strike", "s", "del")
START_RE = re.compile(
    r"^(?:LEI(?:\s+COMPLEMENTAR|\s+DELEGADA)?|DECRETO(?:-LEI)?|MEDIDA\s+PROVIS[ÓO]RIA|EMENDA\s+CONSTITUCIONAL|CONSTITUIÇÃO|O\s+PRESIDENTE|A\s+PRESIDENTA|O\s+CHEFE\s+DO\s+GOVERNO|DECRETA|RESOLVE|FA[ÇC]O\s+SABER|CONSIDERANDO|ART\.)\b",
    re.IGNORECASE,
)
FOOTER_RE = re.compile(r"Este texto n(?:ão|Ã£o) substitui", re.IGNORECASE)


def clean_text(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"^Art\s*\.??\s+", "Art. ", value, flags=re.IGNORECASE)
    value = re.sub(r"^§\s+", "§ ", value)
    return value


def heading_level(value: str) -> int | None:
    normalized = value.upper()
    if normalized.startswith(("O CHEFE DO GOVERNO", "DECRETA", "RESOLVE")):
        return None
    if normalized.startswith(("O PRESIDENTE", "FAÇO SABER")):
        return None
    if normalized.startswith("PARTE ") or normalized.startswith("LIVRO "):
        return 2
    if normalized.startswith("TÍTULO ") or normalized.startswith("TITULO "):
        return 3
    if normalized.startswith("CAPÍTULO ") or normalized.startswith("CAPITULO "):
        return 4
    if normalized.startswith("SEÇÃO ") or normalized.startswith("SECAO "):
        return 5
    if normalized.startswith("SUBSEÇÃO ") or normalized.startswith("SUBSECAO "):
        return 6
    if value == normalized and 3 < len(value) <= 120 and not value.startswith(("ART.", "§")):
        return 3
    return None


def format_block(value: str) -> str:
    level = heading_level(value)
    if level is not None:
        return f"{'#' * level} {value}"
    if re.match(r"^Art\.\s+[0-9A-Za-zºª.-]+\b", value):
        return re.sub(r"^(Art\.\s+[0-9A-Za-zºª.-]+)", r"**\1**", value, count=1)
    return value


def convert(source: Path, encoding: str) -> str:
    raw = source.read_bytes()
    if encoding == "auto":
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            decoded = raw.decode("windows-1252")
        soup = BeautifulSoup(decoded, "html.parser")
    else:
        soup = BeautifulSoup(raw.decode(encoding), "html.parser")
    for tag_name in BLOCKED_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    blocks: list[str] = []
    started = False
    # Legacy pages place normative annexes in tables, sometimes with nested
    # paragraphs. Preserve document order and avoid emitting nested paragraph
    # content twice when a table is handled as one normative block.
    elements = soup.find_all(["p", "table", "h1", "h2", "h3", "h4", "h5", "h6"])
    for element in elements:
        if element.name == "p" and element.find_parent("table") is not None:
            continue
        value = clean_text(element.get_text(" ", strip=True))
        if not value:
            continue
        footer = FOOTER_RE.search(value)
        if footer:
            value = value[:footer.start()].strip()
            if value:
                value = clean_text(value)
            else:
                break
        if not started:
            if START_RE.match(value):
                started = True
            else:
                continue
        if value in {"Mensagem de veto", "Promulgação partes vetadas", "Regulamento"}:
            continue
        if blocks and value == blocks[-1]:
            continue
        blocks.append(format_block(value))

    if not blocks:
        # Some legacy pages place the normative paragraphs in table cells
        # instead of <p> elements.  Retry with cells only when the normal
        # paragraph pass did not find the preamble.
        for cell in soup.find_all("td"):
            value = clean_text(cell.get_text(" ", strip=True))
            if not value:
                continue
            if not started:
                if START_RE.match(value):
                    started = True
                else:
                    continue
            footer = FOOTER_RE.search(value)
            if footer:
                value = clean_text(value[:footer.start()])
            if value and (not blocks or value != blocks[-1]):
                blocks.append(format_block(value))
            if footer:
                break

    if not blocks:
        raise ValueError(f"não foi localizado o início normativo em {source}")
    return "\n\n".join(blocks).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--encoding", default="latin-1")
    args = parser.parse_args()

    result = convert(args.source, args.encoding)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8", newline="\n")
    print(f"Convertido: {args.source} -> {args.output} ({len(result)} caracteres)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
