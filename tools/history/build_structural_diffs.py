"""Build machine-readable structural diffs for preserved legal snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
import sys

TOOLS = Path(__file__).parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from migrate_public_corpus import parse_frontmatter  # noqa: E402


ARTICLE_RE = re.compile(r"(?im)^\s*(?:\*\*)?Art\.?\s+([0-9]+(?:-[A-Z])?)\b")
PARAGRAPH_RE = re.compile(r"(?im)^\s*(?:\*\*)?(?:§|Â§)\s*([0-9]+(?:º|o)?|único|unico)\b")
INCISO_RE = re.compile(r"(?im)^\s*(?:\*\*)?([IVXLCDM]+)\s*[-–—]")
ALINEA_RE = re.compile(r"(?im)^\s*(?:\*\*)?([a-z])\s*[-–—]")


def digest(text: str) -> str:
    return hashlib.sha256(re.sub(r"\s+", " ", text).strip().encode("utf-8")).hexdigest()


def sections(body: str, pattern: re.Pattern[str]) -> dict[str, str]:
    matches = list(pattern.finditer(body))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result[match.group(1)] = body[match.start():end].strip()
    return result


def element_summary(old: str, new: str, pattern: re.Pattern[str]) -> dict[str, int]:
    old_parts, new_parts = sections(old, pattern), sections(new, pattern)
    old_keys, new_keys = set(old_parts), set(new_parts)
    return {
        "added": len(new_keys - old_keys),
        "removed": len(old_keys - new_keys),
        "changed": sum(1 for key in old_keys & new_keys if digest(old_parts[key]) != digest(new_parts[key])),
        "unchanged": sum(1 for key in old_keys & new_keys if digest(old_parts[key]) == digest(new_parts[key])),
    }


def article_diff(old_body: str, new_body: str) -> dict[str, object]:
    old_articles, new_articles = sections(old_body, ARTICLE_RE), sections(new_body, ARTICLE_RE)
    old_keys, new_keys = set(old_articles), set(new_articles)
    changed = []
    for key in sorted(old_keys | new_keys, key=lambda value: (int(re.match(r"\d+", value).group()), value)):
        old_article, new_article = old_articles.get(key), new_articles.get(key)
        if old_article is None:
            status = "adicionado"
        elif new_article is None:
            status = "removido"
        elif digest(old_article) != digest(new_article):
            status = "alterado"
        else:
            status = "inalterado"
        if status != "inalterado":
            changed.append({
                "artigo": key,
                "status": status,
                "hash_anterior": digest(old_article) if old_article is not None else None,
                "hash_atual": digest(new_article) if new_article is not None else None,
                "paragrafos": element_summary(old_article or "", new_article or "", PARAGRAPH_RE),
                "incisos": element_summary(old_article or "", new_article or "", INCISO_RE),
                "alineas": element_summary(old_article or "", new_article or "", ALINEA_RE),
            })
    return {
        "artigos": {
            "total_anterior": len(old_articles), "total_atual": len(new_articles),
            "adicionados": len(new_keys - old_keys), "removidos": len(old_keys - new_keys),
            "alterados": sum(1 for key in old_keys & new_keys if digest(old_articles[key]) != digest(new_articles[key])),
            "inalterados": sum(1 for key in old_keys & new_keys if digest(old_articles[key]) == digest(new_articles[key])),
        },
        "detalhes": changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot_dir", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "bases/history/versoes/2026-10-21-diffs")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    generated = []
    for old_path in sorted(args.snapshot_dir.glob("*.md")):
        current_matches = list((ROOT / "bases/curated/legislacao/federal").rglob(old_path.name))
        if not current_matches:
            continue
        current_path = current_matches[0]
        old_meta, old_body = parse_frontmatter(old_path.read_text(encoding="utf-8"))
        new_meta, new_body = parse_frontmatter(current_path.read_text(encoding="utf-8"))
        metadata_changes = {}
        for key in sorted(set(old_meta) | set(new_meta)):
            if old_meta.get(key) != new_meta.get(key):
                metadata_changes[key] = {"anterior": old_meta.get(key), "atual": new_meta.get(key)}
        report = {
            "schema": "normative-diff/v1", "id": new_meta.get("id"), "generated_at": "2026-10-21",
            "anterior": old_path.as_posix(), "atual": current_path.relative_to(ROOT).as_posix(),
            "metadados": metadata_changes, "estrutura": article_diff(old_body, new_body),
        }
        target = args.output / f"{new_meta.get('id', old_path.stem)}.json"
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        generated.append(target.name)
    index = {"schema": "normative-diff-index/v1", "generated_at": "2026-10-21", "documents": generated}
    (args.output / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Diffs estruturais gerados: {len(generated)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
