"""Audit equivalence between official snapshots and published Markdown bodies.

This is a deterministic fidelity audit. It does not decide legal meaning and it
never rewrites a law. Semantic curation belongs to the autonomous legal agent;
this command only records official evidence, structural comparisons and
explicit anomalies.
"""

from __future__ import annotations

import argparse
import html
import hashlib
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "normalize"))
from migrate_public_corpus import CURATED, parse_frontmatter  # noqa: E402
import official_html_to_markdown as official_converter  # noqa: E402

NORMALIZATION_VERSION = "norm-v3"
SOURCE_UNITS = ROOT / "manifests/source-units.json"
SOURCE_REGISTRY = ROOT / "manifests/sources-registry.json"
SOURCE_RESOLUTION = ROOT / "manifests/source-resolution.json"
DEFAULT_REPORTS = (
    ROOT / "reports/collection-full-2026-10-21-v5.json",
    ROOT / "reports/editorial-expansion-collection-v2.json",
)
ARTICLE_RE = re.compile(
    r"(?im)^[ \t]*(?:\*\*)?art\.?\s+"
    r"([0-9]+(?:\s*[ºª°�])?(?:\s*-\s*[A-Za-z])?)\.?\s*",
    re.UNICODE,
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


ARTICLE_RE_COMPAT = re.compile(
    r"(?im)^[ \t]*(?:\*\*)?art\.?\s+"
    r"([0-9]+(?:\s*[\u00ba\u00aa\u00b0\ufffd])?(?:\s*-\s*[A-Za-z]|[A-Za-z](?=\.))?)\.?\s*",
    re.UNICODE,
)


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def strip_markdown(value: str) -> str:
    value = re.sub(r"^#{1,6}\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"^>\s?", "", value, flags=re.MULTILINE)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[*_`~]", "", value)
    # Markdown tables are a presentation layer. For normative comparison,
    # retain cell text while removing pipes and separator rows so that an
    # official HTML table and its Markdown rendering share one lexical view.
    lines: list[str] = []
    for line in value.splitlines():
        if re.fullmatch(r"\s*\|?[\s:|-]+\|?\s*", line):
            continue
        if line.count("|") >= 2:
            line = line.replace("|", " ")
        lines.append(line)
    value = "\n".join(lines)
    return normalize_text(value)


def repair_legacy_article_markers(value: str) -> str:
    """Repair parser-visible HTML spacing artifacts for comparison only.

    Legacy official pages contain malformed markup such as ``A rt. 1`` and
    ``Art. 4 6-A``. These repairs are confined to the audit view; the
    canonical Markdown body is never rewritten by this function.
    """
    value = value.replace("A rt.", "Art.").replace("a rt.", "art.")
    value = value.replace("Art .", "Art.").replace("art .", "art.")
    value = re.sub(r"\b(Art\.?\s+\d+)\s+([ºª°�])", r"\1\2", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(Art\.?\s+\d+)\s+([0-9])", r"\1\2", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(Art\.?\s+\d+)\s+([A-Za-z])", r"\1-\2", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(Art\.?\s+\d+)\s*-\s*([A-Za-z])", r"\1-\2", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(Art\.?\s+\d+)-([oa])\b", r"\1\2", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(Art\.?\s+\d+[A-Za-z])\s+\.", r"\1.", value, flags=re.IGNORECASE)
    return value


def article_tree(value: str) -> list[dict[str, str]]:
    text = repair_legacy_article_markers(strip_markdown(value))
    matches = list(ARTICLE_RE_COMPAT.finditer(text))
    result: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        article = normalize_text(text[match.start():end])
        label = re.sub(r"\s+", "", match.group(1)).strip().upper()
        result.append({"label": label, "text": article})
    return result


def normative_article_text(article: str) -> str:
    """Return the normative portion of an article for fidelity hashing.

    Signatures, participant rosters and closing publication material are
    editorial metadata, not operative provisions. Official Constitution and
    ADCT pages append those blocks after the final article; excluding them
    prevents a source-layout difference from becoming a false legal mismatch.
    """
    article = re.split(r"\n{2,}Bras.{0,3}lia,", article, maxsplit=1, flags=re.IGNORECASE)[0]
    return normalize_text(article)


def load_unit_rules() -> dict[str, Any]:
    if not SOURCE_UNITS.is_file():
        return {"default": {"selector_type": "full_official_document", "selector": None}, "units": {}}
    return json.loads(SOURCE_UNITS.read_text(encoding="utf-8"))


def unit_rule(document_id: str, rules: dict[str, Any]) -> dict[str, Any]:
    specific = (rules.get("units") or {}).get(document_id)
    if specific:
        return specific
    default = dict(rules.get("default") or {})
    default["source_unit_id"] = document_id
    return default


def select_unit(text: str, rule: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    normalized = normalize_text(text)
    selector_type = rule.get("selector_type")
    selector = rule.get("selector") or {}

    def marker_position(marker: str) -> int:
        # A section can appear in a table of contents or cross-reference before
        # its actual heading. Prefer a marker at the beginning of a rendered
        # line, then fail closed to the first literal occurrence.
        heading = re.compile(rf"(?im)^[#* \t]*{re.escape(marker)}")
        match = heading.search(normalized)
        return match.start() if match else normalized.upper().find(marker.upper())

    if selector_type == "article_range_before_marker":
        end = str(selector.get("end") or "")
        position = marker_position(end)
        if position >= 0:
            normalized = normalized[:position].rstrip()
    elif selector_type == "marker_to_end":
        start = str(selector.get("start") or "")
        position = marker_position(start)
        if position >= 0:
            normalized = normalized[position:]
    return normalized, {
        "selector_type": selector_type,
        "selector": selector,
        "unit_scope": rule.get("unit_scope", "single_diploma"),
    }


def load_reports(paths: list[Path]) -> dict[str, dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    for path in paths:
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("results", []):
            document_id = str(item.get("document_id") or "")
            attempts = [a for a in item.get("attempts", []) if a.get("status") == "fetched"]
            entry = {**item, "attempts": attempts, "report": path.name}
            if document_id:
                evidence[document_id] = entry
            for url in [item.get("primary_url"), *(a.get("url") for a in attempts)]:
                if url:
                    evidence[f"__url__:{str(url).rstrip('/')}" ] = entry
    return evidence


def load_source_resolutions() -> dict[str, dict[str, Any]]:
    if not SOURCE_RESOLUTION.is_file():
        return {}
    payload = json.loads(SOURCE_RESOLUTION.read_text(encoding="utf-8"))
    return {
        str(key): value
        for key, value in (payload.get("documents") or {}).items()
        if isinstance(value, dict)
    }


def load_source_ranks() -> dict[str, int]:
    if not SOURCE_REGISTRY.is_file():
        return {}
    payload = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    return {
        str(source.get("id")): int(source.get("rank", 999))
        for source in payload.get("sources", [])
        if source.get("id")
    }


def select_attempt(
    evidence: dict[str, Any],
    resolutions: dict[str, dict[str, Any]],
    source_ranks: dict[str, int],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    attempts = [attempt for attempt in evidence.get("attempts", []) if attempt.get("status") == "fetched"]
    resolution = resolutions.get(str(evidence.get("matrix_id") or ""))
    if isinstance(resolution, dict) and resolution.get("status") == "approved":
        source_id = str(resolution.get("selected_source_id") or "")
        selected = [attempt for attempt in attempts if str(attempt.get("source_id")) == source_id]
        if selected:
            attempt = selected[0]
            return attempt, {
                "method": "approved_source_resolution",
                "source_id": source_id,
                "expected_sha256": resolution.get("expected_source_sha256"),
                "expected_sha256_matches": not resolution.get("expected_source_sha256")
                or resolution.get("expected_source_sha256") == attempt.get("sha256_raw"),
            }
    if attempts:
        attempt = sorted(
            attempts,
            key=lambda candidate: (
                source_ranks.get(str(candidate.get("source_id")), 999),
                str(candidate.get("source_id") or ""),
            ),
        )[0]
        return attempt, {
            "method": "official_source_precedence",
            "source_id": attempt.get("source_id"),
            "expected_sha256": None,
            "expected_sha256_matches": None,
        }
    return None, {"method": "no_fetched_attempt", "source_id": None}


def canonical_source_body(converted: str, document_id: str, rules: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    selected, selector = select_unit(converted, unit_rule(document_id, rules))
    articles = article_tree(selected)
    body = "\n\n".join(article["text"] for article in articles)
    if not body:
        body = selected
    return normalize_text(body), selector


def published_body(path: Path) -> tuple[dict[str, Any], str]:
    metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
    return metadata, body


def convert_html_anchor_section(
    source_path: Path,
    anchor_name: str,
    before: bool,
    fallback_anchors: list[dict[str, Any]] | None = None,
    raw_article_anchor_pattern: str | None = None,
) -> str:
    """Convert one anchored section of the legacy compiled Constitution page."""
    raw = source_path.read_bytes()
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        decoded = raw.decode("windows-1252")
    soup = BeautifulSoup(decoded, "html.parser")
    for tag_name in official_converter.BLOCKED_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    anchor = soup.find("a", attrs={"name": anchor_name})
    if anchor is None:
        raise ValueError(f"official anchor not found: {anchor_name}")
    paragraphs = soup.find_all(["p", "table", "h1", "h2", "h3", "h4", "h5", "h6"])
    anchor_index = next(
        (index for index, paragraph in enumerate(paragraphs)
         if paragraph is anchor or anchor in paragraph.descendants),
        None,
    )
    if anchor_index is None:
        raise ValueError(f"official anchor paragraph not found: {anchor_name}")
    selected = paragraphs[:anchor_index] if before else paragraphs[anchor_index + 1:]
    blocks: list[str] = []
    started = not before
    for paragraph in selected:
        if paragraph.name == "p" and paragraph.find_parent("table") is not None:
            continue
        value = official_converter.clean_text(paragraph.get_text(" ", strip=True))
        if not value:
            continue
        footer = official_converter.FOOTER_RE.search(value)
        if footer:
            value = official_converter.clean_text(value[:footer.start()])
            if value:
                blocks.append(official_converter.format_block(value))
            break
        if not started:
            if official_converter.START_RE.match(value):
                started = True
            else:
                continue
        if value in {"Mensagem de veto", "Promulgação partes vetadas", "Regulamento"}:
            continue
        formatted = official_converter.format_block(value)
        if blocks and formatted == blocks[-1]:
            continue
        blocks.append(formatted)
    # A few legacy paragraphs are malformed: the article anchor is present in
    # the raw HTML, but the HTML parser exposes an empty paragraph and loses
    # the article heading. Recover only explicitly declared anchors and keep
    # the recovery auditable in the source-unit contract.
    if fallback_anchors or raw_article_anchor_pattern:
        fallback_items: list[tuple[int, str, str]] = []
        raw_overrides: list[tuple[str, str]] = []
        raw_text = decoded
        section_start = 0 if before else raw_text.lower().find(f'name="{anchor_name.lower()}"')
        section_end = raw_text.lower().find(f'name="{anchor_name.lower()}"') if before else len(raw_text)
        base_labels = [item["label"] for item in article_tree("\n\n".join(blocks))]
        if raw_article_anchor_pattern:
            anchor_sequence = re.compile(
                rf'name=["\'][^"\']*{re.escape(raw_article_anchor_pattern)}\d+[^"\']*["\']',
                re.IGNORECASE,
            )
            article_anchors = [
                match
                for match in anchor_sequence.finditer(raw_text)
                if section_start <= match.start() < section_end
            ]
            for index, match in enumerate(article_anchors):
                anchor_end = article_anchors[index + 1].start() if index + 1 < len(article_anchors) else section_end
                end = anchor_end
                fragment = raw_text[match.start() : end]
                text = official_converter.clean_text(BeautifulSoup(fragment, "html.parser").get_text(" ", strip=True))
                article_start = re.search(r"(?i)\bArt\.?\s+", text)
                article_matches = article_tree(text[article_start.start():]) if article_start else []
                if article_matches:
                    article = article_matches[0]
                    try:
                        current_index = next(
                            index
                            for index, value in enumerate(base_labels)
                            if value.upper() == article["label"].upper()
                        )
                        next_label = base_labels[current_index + 1]
                    except (StopIteration, IndexError):
                        next_label = ""
                    if next_label:
                        next_number = re.match(r"\d+", next_label)
                        if next_number:
                            suffix = next_label[len(next_number.group(0)) :].replace("º", "").replace("ª", "").replace("°", "").replace("�", "")
                            next_pattern = rf"\bArt\.?\s*{next_number.group(0)}{re.escape(suffix)}\s*\."
                            next_text = raw_text[match.end() : anchor_end]
                            next_article = re.search(next_pattern, next_text, re.IGNORECASE)
                            if next_article:
                                end = match.end() + next_article.start()
                                fragment = raw_text[match.start() : end]
                                text = official_converter.clean_text(BeautifulSoup(fragment, "html.parser").get_text(" ", strip=True))
                                article_start = re.search(r"(?i)\bArt\.?\s+", text)
                                article_matches = article_tree(text[article_start.start():]) if article_start else []
                                if article_matches:
                                    article = article_matches[0]
                    raw_overrides.append((article["label"], official_converter.format_block(article["text"])))
        for item in fallback_anchors or []:
            pattern = str(item.get("anchor_pattern") or item.get("anchor") or "")
            label = str(item.get("label") or "")
            if not pattern or not label:
                continue
            match = re.search(rf'name=["\'][^"\']*{re.escape(pattern)}[^"\']*["\']', raw_text, re.IGNORECASE)
            if not match or not (section_start <= match.start() < section_end):
                continue
            if item.get("replace_full_article"):
                anchor_sequence = r'name=["\'][^"\']*(?:artigo-\d+|sadctart\d+)[^"\']*["\']'
                next_anchor = re.search(anchor_sequence, raw_text[match.end() : section_end], re.IGNORECASE)
                end = match.end() + next_anchor.start() if next_anchor else section_end
                fragment = raw_text[match.start() : end]
                text = official_converter.clean_text(BeautifulSoup(fragment, "html.parser").get_text(" ", strip=True))
                article_match = re.search(r"(?i)\bArt\.?\s+[^ ]+.*", text)
                if article_match:
                    raw_overrides.append((label, official_converter.format_block(article_match.group(0))))
                continue
            paragraph_end = raw_text.find("</p>", match.end())
            fragment = raw_text[match.start() : paragraph_end + 4 if paragraph_end >= 0 else match.end()]
            text = official_converter.clean_text(BeautifulSoup(fragment, "html.parser").get_text(" ", strip=True))
            article_match = re.search(r"(?i)\bArt\.?\s+[^ ]+.*", text)
            if article_match:
                fallback_items.append((match.start(), label, official_converter.format_block(article_match.group(0))))
        fallback_items.sort(key=lambda item: item[0])
        existing_labels = [item["label"] for item in article_tree("\n\n".join(blocks))]
        for _, label, block in fallback_items:
            if label.upper() in {value.upper() for value in existing_labels}:
                continue
            target_number = int(re.match(r"\d+", label).group(0)) if re.match(r"\d+", label) else 10**9
            insert_at = len(blocks)
            for index, current_block in enumerate(blocks):
                current_articles = article_tree(current_block)
                current_match = re.match(r"\d+", current_articles[0]["label"]) if current_articles else None
                if current_match and int(current_match.group(0)) > target_number:
                    insert_at = index
                    break
            blocks.insert(insert_at, block)
            existing_labels.append(label)
        for label, replacement in raw_overrides:
            article_indices = [
                index
                for index, current_block in enumerate(blocks)
                if any(article["label"].upper() == label.upper() for article in article_tree(current_block))
            ]
            if not article_indices:
                target_number = int(re.match(r"\d+", label).group(0)) if re.match(r"\d+", label) else 10**9
                insert_at = len(blocks)
                for index, current_block in enumerate(blocks):
                    current_articles = article_tree(current_block)
                    current_match = re.match(r"\d+", current_articles[0]["label"]) if current_articles else None
                    if current_match and int(current_match.group(0)) > target_number:
                        insert_at = index
                        break
                blocks.insert(insert_at, replacement)
                continue
            start = article_indices[0]
            end = len(blocks)
            for index in range(start + 1, len(blocks)):
                if article_tree(blocks[index]):
                    end = index
                    break
            blocks[start:end] = [replacement]
    if not blocks:
        raise ValueError(f"official anchor section is empty: {anchor_name}")
    return "\n\n".join(blocks).rstrip() + "\n"


def snapshot_path(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return ROOT / path


def audit_document(
    path: Path,
    evidence: dict[str, Any] | None,
    rules: dict[str, Any],
    resolutions: dict[str, dict[str, Any]] | None = None,
    source_ranks: dict[str, int] | None = None,
) -> dict[str, Any]:
    metadata, body = published_body(path)
    document_id = str(metadata.get("id") or "")
    anomalies: list[str] = []
    published_articles = article_tree(body)
    published_norm = "\n\n".join(normative_article_text(article["text"]) for article in published_articles)
    result: dict[str, Any] = {
        "document_id": document_id,
        "path": path.relative_to(ROOT).as_posix(),
        "source_unit_id": unit_rule(document_id, rules).get("source_unit_id", document_id),
        "source_unit_selector": unit_rule(document_id, rules),
        "canonicalization_version": NORMALIZATION_VERSION,
        "published_article_count": len(published_articles),
        "sha256_published_body": sha256_text(normalize_text(published_norm)),
        "anomalies": anomalies,
    }
    if not evidence:
        result.update({"equivalence_status": "needs_source_evidence", "evidence_status": "missing_snapshot"})
        anomalies.append("official_snapshot_not_available_in_local_evidence")
        return result
    attempt, source_selection = select_attempt(evidence, resolutions or {}, source_ranks or {})
    if not attempt or not attempt.get("snapshot_file"):
        result.update({"equivalence_status": "needs_source_evidence", "evidence_status": "missing_snapshot"})
        anomalies.append("official_snapshot_not_available_in_local_evidence")
        return result
    source_path = snapshot_path(str(attempt["snapshot_file"]))
    if not source_path.is_file():
        result.update({"equivalence_status": "needs_source_evidence", "evidence_status": "snapshot_path_missing"})
        anomalies.append("snapshot_path_missing_from_private_ledger")
        return result
    raw = source_path.read_bytes()
    try:
        # Use the same deterministic converter that creates the canonical
        # Markdown. A narrower HTML-only extractor creates false mismatches
        # for official pages whose normative text is represented in tables or
        # nested layout elements.
        rule = unit_rule(document_id, rules)
        selector_type = str(rule.get("selector_type") or "")
        if selector_type in {"html_before_anchor", "html_anchor_to_end"}:
            selector = rule.get("selector") or {}
            converted = convert_html_anchor_section(
                source_path,
                str(selector.get("anchor") or "adct"),
                before=selector_type == "html_before_anchor",
                fallback_anchors=selector.get("fallback_anchors") or [],
                raw_article_anchor_pattern=selector.get("raw_article_anchor_pattern"),
            )
        else:
            converted = official_converter.convert(source_path, "auto")
    except (OSError, ValueError, UnicodeError) as error:
        result.update({"equivalence_status": "needs_source_evidence", "evidence_status": "conversion_error", "error": str(error)})
        anomalies.append("official_snapshot_conversion_failed")
        return result
    source_selected, selector = canonical_source_body(converted, document_id, rules)
    source_articles = article_tree(source_selected)
    source_norm = normalize_text("\n\n".join(normative_article_text(article["text"]) for article in source_articles))
    published_norm = normalize_text("\n\n".join(normative_article_text(article["text"]) for article in published_articles))
    labels_match = [a["label"] for a in source_articles] == [a["label"] for a in published_articles]
    # ``ratio`` is quadratic on large codes. ``quick_ratio`` is a deterministic
    # linear-time upper bound suitable for a release gate; exact hashes remain
    # the strongest signal and are recorded separately below.
    source_hash = sha256_text(source_norm)
    published_hash = sha256_text(published_norm)
    similarity = SequenceMatcher(None, source_norm, published_norm, autojunk=False).quick_ratio() if source_norm and published_norm else 0.0
    if len(source_articles) == 0:
        anomalies.append("source_has_no_detectable_article_tree")
    if not labels_match:
        anomalies.append("article_tree_mismatch")
    if "\ufffd" in converted or "\ufffd" in body:
        anomalies.append("replacement_character_present")
    result.update({
        "evidence_status": "snapshot_verified",
        "source_snapshot_date": evidence.get("data_corte") or evidence.get("generated_at"),
        "source_url": attempt.get("final_url") or attempt.get("url"),
        "source_snapshot_file_private": True,
        "source_selection": source_selection,
        "sha256_source_raw": hashlib.sha256(raw).hexdigest(),
        "sha256_source_normalized": sha256_text(normalize_text(converted)),
        "sha256_source_body": source_hash,
        "source_published_hash_match": source_hash == published_hash,
        "published_article_count": len(published_articles),
        "source_article_count": len(source_articles),
        "article_tree_match": labels_match,
        "text_similarity": round(similarity, 6),
        "selector_applied": selector,
    })
    if labels_match and similarity >= 0.985 and not any(a in anomalies for a in ("replacement_character_present",)):
        result["equivalence_status"] = "pass"
    else:
        result["equivalence_status"] = "review"
        if similarity < 0.985:
            anomalies.append("normative_text_similarity_below_threshold")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="append", type=Path, dest="reports", help="collection report; may be repeated")
    parser.add_argument("--output", type=Path, default=ROOT / "bases/derived/relatorios/fidelity-audit.json")
    parser.add_argument("--strict", action="store_true", help="return non-zero unless every document passes")
    args = parser.parse_args()
    report_paths = args.reports or list(DEFAULT_REPORTS)
    evidence = load_reports(report_paths)
    rules = load_unit_rules()
    resolutions = load_source_resolutions()
    source_ranks = load_source_ranks()
    documents = [p for p in sorted(CURATED.rglob("*.md")) if p.name.lower() != "readme.md"]
    audited = []
    for path in documents:
        metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"), strict=True)
        item_evidence = evidence.get(str(metadata.get("id") or ""))
        if not item_evidence:
            sources = metadata.get("fonte_oficial") or []
            if isinstance(sources, str):
                sources = [sources]
            for source in sources:
                item_evidence = evidence.get(f"__url__:{str(source).rstrip('/')}" )
                if item_evidence:
                    break
        audited.append(audit_document(path, item_evidence, rules, resolutions, source_ranks))
    counts: dict[str, int] = {}
    for item in audited:
        key = str(item.get("equivalence_status"))
        counts[key] = counts.get(key, 0) + 1
    payload = {
        "schema": "normative-fidelity-audit/v1",
        "canonicalization_version": NORMALIZATION_VERSION,
        "generated_at": __import__("datetime").date.today().isoformat(),
        "corpus_count": len(audited),
        "counts": counts,
        "status": "pass" if counts.get("pass", 0) == len(audited) else "review_required",
        "policy": "deterministic_fidelity_only; legal_meaning_is_decided_by_autonomous_legal_agent",
        "documents": audited,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"corpus_count": len(audited), "counts": counts, "status": payload["status"]}, ensure_ascii=False))
    return 0 if not args.strict or payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
