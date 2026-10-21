"""Build structural diffs from private acquisition snapshots and current Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "history"))
from build_structural_diffs import article_diff  # noqa: E402
from migrate_public_corpus import parse_frontmatter  # noqa: E402


def source_text(path: Path, content_type: str = "") -> str:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    if "html" in content_type.lower() or "<html" in text[:1000].lower():
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup.find_all(("script", "style", "noscript")):
            tag.decompose()
        blocks = []
        for node in soup.find_all(("p", "div", "td", "li")):
            value = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
            if value and (not blocks or value != blocks[-1]):
                blocks.append(value)
        return "\n\n".join(blocks)
    return text


def current_document(document_id: str) -> tuple[Path, str] | None:
    for path in (ROOT / "bases/curated/legislacao").rglob("*.md"):
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if metadata.get("id") == document_id:
            return path, body
    return None


def classify_change(status: str, old_body: str, new_body: str, structure: dict[str, object]) -> list[str]:
    if status == "source_conflict":
        return ["conflito_de_fontes", "requer_reconciliacao"]
    classifications: list[str] = []
    lower = new_body.lower()
    if structure.get("alterados", 0) or structure.get("adicionados", 0) or structure.get("removidos", 0):
        classifications.append("alteracao_normativa")
    else:
        classifications.append("formatacao_ou_metadado")
    for marker, label in (
        ("revog", "possivel_revogacao"),
        ("vet", "possivel_veto"),
        ("retific", "possivel_retificacao"),
        ("vigência", "possivel_efeito_de_vigencia"),
        ("vigencia", "possivel_efeito_de_vigencia"),
        ("produção de efeitos", "possivel_efeito_de_vigencia"),
    ):
        if marker in lower and label not in classifications:
            classifications.append(label)
    classifications.append("requer_reconciliacao")
    return classifications


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.collection_report.read_text(encoding="utf-8"))
    results = report.get("results", [])
    args.output.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    for item in results:
        if item.get("status") not in {"changed_candidate", "source_conflict"}:
            continue
        current = current_document(str(item.get("document_id") or ""))
        snapshot = ROOT / str(item.get("snapshot_file") or "")
        detail: dict[str, object] = {
            "schema": "candidate-normative-diff/v1",
            "matrix_id": item.get("matrix_id"),
            "document_id": item.get("document_id"),
            "status": item.get("status"),
            "source": item.get("primary_url"),
        }
        if not current or not snapshot.is_file():
            detail["diff_status"] = "unavailable"
            detail["reason"] = "current_document_or_snapshot_missing"
        else:
            current_path, current_body = current
            attempt = next((value for value in item.get("attempts", []) if value.get("status") == "fetched"), {})
            updated_body = source_text(snapshot, str(attempt.get("content_type", "")))
            structure = article_diff(current_body, updated_body)
            detail["diff_status"] = "generated"
            detail["current_path"] = current_path.relative_to(ROOT).as_posix()
            detail["structure"] = structure
            detail["classificacao"] = classify_change(str(item.get("status")), current_body, updated_body, structure["artigos"])
        target = args.output / f"{item.get('matrix_id', 'unknown')}.json"
        target.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        structure = detail.get("structure", {}).get("artigos", {})
        entries.append({
            "matrix_id": item.get("matrix_id"),
            "status": detail["diff_status"],
            "file": target.name,
            "artigos_alterados": structure.get("alterados", 0),
            "artigos_adicionados": structure.get("adicionados", 0),
            "artigos_removidos": structure.get("removidos", 0),
            "classificacao": detail.get("classificacao", ["requer_reconciliacao"]),
        })
    index = {
        "schema": "candidate-normative-diff-index/v1",
        "documents": entries,
        "generated_count": sum(item["status"] == "generated" for item in entries),
        "unavailable_count": sum(item["status"] == "unavailable" for item in entries),
    }
    (args.output / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(index, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
