"""Deterministically normalize HTML, XML, PDF or plain text locally."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from pypdf import PdfReader


def normalize_bytes(data: bytes, source_format: str, encoding: str = "utf-8") -> str:
    source_format = source_format.lower()
    if source_format == "pdf":
        raise ValueError("PDF requer normalize_pdf_path para preservar a ordem das páginas")
    text = data.decode(encoding, errors="replace")
    if source_format in {"html", "xhtml"}:
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup.find_all(("script", "style", "noscript")):
            tag.decompose()
        blocks = [re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip() for node in soup.find_all(("p", "div", "td", "li"))]
        blocks = [value for index, value in enumerate(blocks) if value and (index == 0 or value != blocks[index - 1])]
        return "\n\n".join(blocks).strip() + "\n"
    if source_format == "xml":
        root = ElementTree.fromstring(text)
        blocks = [re.sub(r"\s+", " ", value).strip() for value in root.itertext()]
        return "\n\n".join(value for value in blocks if value) + "\n"
    return re.sub(r"\s+", " ", text).strip() + "\n"


def normalize_pdf_path(source: Path) -> str:
    reader = PdfReader(str(source))
    pages = [re.sub(r"\s+", " ", page.extract_text() or "").strip() for page in reader.pages]
    return "\n\n".join(page for page in pages if page) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--format", choices=("html", "xml", "pdf", "text"), default="text")
    parser.add_argument("--encoding", default="utf-8")
    args = parser.parse_args()
    result = normalize_pdf_path(args.source) if args.format == "pdf" else normalize_bytes(args.source.read_bytes(), args.format, args.encoding)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8", newline="\n")
    print(f"Normalizado: {args.source} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
