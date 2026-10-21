"""Safely collect official snapshots without mutating the curated corpus.

The default mode is a network-free dry-run. ``--fetch`` writes raw responses and
technical evidence under ``.private`` (ignored by Git) and emits a JSON report.
No option in this module writes a curated Markdown document or changes ``main``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from http.client import IncompleteRead
import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


ROOT = Path(__file__).parents[2]
MATRIX = ROOT / "manifests/corpus.csv"
REGISTRY = ROOT / "manifests/sources-registry.json"
SOURCE_MANIFEST = ROOT / "manifests/sources-official.json"
SOURCE_COMPARISON = ROOT / "manifests/source-comparison.json"
DEFAULT_PRIVATE = ROOT / ".private" / "acquisition"
sys.path.insert(0, str(ROOT / "tools"))
from pipeline_modes import load_modes, resolve_mode  # noqa: E402


def load_registry() -> dict[str, object]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def registry_sources(registry: dict[str, object]) -> list[dict[str, object]]:
    return sorted(registry.get("sources", []), key=lambda item: int(item.get("rank", 999)))


def load_rows(path: Path = MATRIX) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def load_source_manifest() -> dict[str, dict[str, object]]:
    if not SOURCE_MANIFEST.is_file():
        return {}
    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    return {str(item["id"]): item for item in payload.get("documents", [])}


def load_source_comparison() -> dict[str, str]:
    if not SOURCE_COMPARISON.is_file():
        return {}
    payload = json.loads(SOURCE_COMPARISON.read_text(encoding="utf-8"))
    return {str(key): str(value.get("mode", "same_document")) for key, value in payload.get("documents", {}).items()}


def normalize_url(raw: str) -> str:
    return raw.strip().strip('"').strip("'").rstrip(".,;)]}")


def host_allowed(url: str, registry: dict[str, object]) -> bool:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    for source in registry_sources(registry):
        for allowed in source.get("hosts", []):
            allowed = str(allowed).lower().lstrip(".")
            if host == allowed or host.endswith("." + allowed):
                return True
    return False


def source_rank(url: str, registry: dict[str, object]) -> int:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    for source in registry_sources(registry):
        if any(host == str(item).lower() or host.endswith("." + str(item).lower()) for item in source.get("hosts", [])):
            return int(source.get("rank", 999))
    return 999


def source_rate_limit(url: str, registry: dict[str, object]) -> float:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    for source in registry_sources(registry):
        if any(host == str(item).lower() or host.endswith("." + str(item).lower()) for item in source.get("hosts", [])):
            return float(source.get("rate_limit_seconds", 0.5))
    return 1.0


def source_info(url: str, registry: dict[str, object]) -> dict[str, object]:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    for source in registry_sources(registry):
        if any(host == str(item).lower() or host.endswith("." + str(item).lower()) for item in source.get("hosts", [])):
            return {"source_id": source.get("id"), "adapter": source.get("adapter"), "adapter_version": source.get("adapter_version"), "authority": source.get("authority")}
    return {"source_id": None, "adapter": None, "authority": None}


def urls_for_row(row: dict[str, str], registry: dict[str, object]) -> list[str]:
    values = [normalize_url(value) for value in row.get("fonte_oficial", "").split("|") if value.strip()]
    unique = sorted(set(values), key=lambda value: (source_rank(value, registry), value))
    return [value for value in unique if host_allowed(value, registry)]


def manifest_entries_for(urls: list[str], manifest: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    url_set = set(urls)
    return [
        item for item in manifest.values()
        if url_set.intersection(str(value) for value in item.get("fontes", []))
    ]


def exact_manifest_entries_for(urls: list[str], manifest: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    url_set = set(urls)
    return [
        item for item in manifest.values()
        if url_set == {str(value) for value in item.get("fontes", [])}
    ]


def cutoff_for(urls: list[str], manifest: dict[str, dict[str, object]]) -> date | None:
    entries = manifest_entries_for(urls, manifest)
    raw = entries[0].get("data_corte") if entries else None
    try:
        return date.fromisoformat(str(raw)) if raw else None
    except ValueError:
        return None


def stale_after_days(priority: str) -> int:
    return {"P0": 100, "P1": 100, "P2": 180}.get(priority, 180)


def build_plan(as_of: date | None = None, input_path: Path = MATRIX) -> list[dict[str, object]]:
    as_of = as_of or date.today()
    registry = load_registry()
    manifest = load_source_manifest()
    comparison = load_source_comparison()
    # The editorial expansion inventory is a discovery queue, not part of the
    # canonical corpus.  Its acquisition hashes are evidence of prior
    # discovery only and must not be treated as the current baseline for a
    # collection plan.
    is_canonical_corpus = input_path.resolve() == MATRIX.resolve()
    plan: list[dict[str, object]] = []
    for row in load_rows(input_path):
        if not is_canonical_corpus and row.get("status_cobertura") == "promovido_corpus":
            # Promoted candidates are monitored through corpus.csv, not the
            # discovery queue, so they must not be collected twice.
            continue
        urls = urls_for_row(row, registry)
        source_entries = manifest_entries_for(urls, manifest)
        exact_entries = exact_manifest_entries_for(urls, manifest)
        stable_entry = manifest.get(str(row.get("document_id") or ""), {})
        cutoff = cutoff_for(urls, manifest)
        age = (as_of - cutoff).days if cutoff else None
        current_body_hash = stable_entry.get("sha256_corpo")
        current_body_hashes_by_source = {
            str(item.get("fonte")): str(item.get("sha256_corpo"))
            for item in stable_entry.get("sha256_corpo_por_fonte", [])
            if isinstance(item, dict) and item.get("fonte") and item.get("sha256_corpo")
        }
        if is_canonical_corpus:
            current_body_hash = current_body_hash or row.get("sha256_corpo")
        current_hash_kind = (
            "per_source" if current_body_hashes_by_source and not current_body_hash
            else ("legal_body" if current_body_hash else "raw")
        )
        current_sha256 = current_body_hash
        if not current_sha256 and not current_body_hashes_by_source:
            current_sha256 = (
                row.get("sha256_origem") if is_canonical_corpus else None
            ) or (exact_entries[0].get("sha256_origem") if is_canonical_corpus and len(exact_entries) == 1 else None)
        plan.append({
            "matrix_id": row["id"],
            # The editorial matrix is the stable identity authority.  A source
            # URL may be migrated or replaced without changing the document ID.
            "document_id": row.get("document_id") or (exact_entries[0].get("id") if len(exact_entries) == 1 else None),
            "source_manifest_ids": [item.get("id") for item in source_entries],
            "current_sha256": current_sha256,
            "current_sha256_by_source": current_body_hashes_by_source,
            "current_hash_kind": current_hash_kind,
            "prioridade": row.get("prioridade", ""),
            "sensibilidade": row.get("sensibilidade_atualizacao", ""),
            "urls": urls,
            "primary_url": urls[0] if urls else None,
            "source_count": len(urls),
            "comparison_mode": comparison.get(row["id"], "same_document"),
            "data_corte": cutoff.isoformat() if cutoff else None,
            "idade_dias": age,
            "stale": age is None or age > stale_after_days(row.get("prioridade", "P2")),
            "status": "planned" if urls else "source_missing",
        })
    return plan


def select_plan(plan: list[dict[str, object]], priorities: list[str] | None = None) -> list[dict[str, object]]:
    if not priorities:
        return plan
    allowed = set(priorities)
    return [item for item in plan if item["prioridade"] in allowed]


def decode_body(data: bytes, content_type: str) -> str:
    match = re.search(r"charset=([\w-]+)", content_type, re.I)
    encodings = [match.group(1)] if match else []
    encodings.extend(["utf-8", "windows-1252", "latin-1"])
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return data.decode("utf-8", errors="replace")


def normalized_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def snapshot_display_path(path: Path) -> str:
    """Return a stable report path for workspace and isolated snapshot dirs."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def legal_body_hash(text: str, content_type: str) -> str:
    if "html" in content_type.lower() or "<html" in text[:1000].lower():
        soup = BeautifulSoup(text, "html.parser")
        for tag in soup.find_all(("script", "style", "noscript")):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
    markers = [marker for marker in ("O PRESIDENTE", "Art.", "ART.") if marker in text]
    if markers:
        text = text[min(text.find(marker) for marker in markers):]
    return normalized_hash(text)


def is_unusable_official_response(text: str, content_type: str) -> str | None:
    """Reject successful HTTP responses that are only an application shell.

    Normas.leg.br currently serves its Angular shell to a plain HTTP client;
    accepting that 200 response as legislation produced one identical hash for
    hundreds of unrelated diplomas. A source is usable only when its body
    contains legal-text markers.
    """
    if "html" not in content_type.lower() and "<html" not in text[:1000].lower():
        return None
    lowered = text.lower()
    if "<app-root" in lowered and not re.search(r"\b(?:art\.?\s*\d+|lei\s+n[ºo°]?\.?\s*\d)", text, re.I):
        return "application_shell_without_legal_body"
    return None


def normas_metadata_url(url: str) -> str | None:
    parsed = urlparse(url)
    if (parsed.hostname or "").lower().rstrip(".") != "normas.leg.br":
        return None
    urn = parse_qs(parsed.query).get("urn", [None])[0]
    if not urn:
        return None
    return "https://normas.leg.br/api/public/normas?" + urlencode({"urn": urn, "tipo_documento": "maior-detalhe"})


def current_normas_content_url(metadata: dict[str, object]) -> str | None:
    encodings = metadata.get("encoding", [])
    if isinstance(encodings, dict):
        encodings = [encodings]
    if not isinstance(encodings, list):
        return None
    candidates = [item for item in encodings if isinstance(item, dict) and item.get("contentUrl")]
    candidates.sort(key=lambda item: (
        0 if str(item.get("version", "")).lower() == "current" else 1,
        0 if str(item.get("additionalType", "")).lower().startswith("compilacao") else 1,
    ))
    for item in candidates:
        raw = str(item["contentUrl"])
        parsed = urlparse(raw)
        if parsed.hostname and parsed.hostname.lower().rstrip(".") == "normas.leg.br":
            path = parsed.path.replace("/api/binario/", "/api/public/binario/", 1)
            return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))
    return None


def request_bytes(url: str, registry: dict[str, object], accept: str) -> dict[str, object]:
    policy = registry["policy"]
    timeout = int(policy.get("request_timeout_seconds", 30))
    max_bytes = int(policy.get("max_response_bytes", 20 * 1024 * 1024))
    request = Request(url, headers={
        "User-Agent": str(policy.get("user_agent", "Mozilla/5.0 (compatible; vademecum-md-monitor/0.1)")),
        "Accept": accept,
        "Accept-Encoding": "identity",
        "Connection": "close",
    })
    info = source_info(url, registry)
    try:
        with urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            if not host_allowed(final_url, registry):
                return {**info, "status": "redirect_blocked", "url": url, "final_url": final_url}
            length = response.headers.get("Content-Length")
            if length and int(length) > max_bytes:
                return {**info, "status": "response_too_large", "url": url, "bytes": int(length)}
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                return {**info, "status": "response_too_large", "url": url, "bytes": len(data)}
            return {
                **info,
                "status": "fetched",
                "url": url,
                "final_url": final_url,
                "http_status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "bytes": len(data),
                "_data": data,
            }
    except HTTPError as error:
        return {**info, "status": "http_error", "url": url, "http_status": error.code, "reason": str(error.reason)}
    except (URLError, TimeoutError, OSError, IncompleteRead) as error:
        return {**info, "status": "network_error", "url": url, "reason": str(error)}


def fetch_one(url: str, registry: dict[str, object]) -> dict[str, object]:
    metadata_url = normas_metadata_url(url)
    if metadata_url:
        metadata_result = request_bytes(metadata_url, registry, "application/json")
        if metadata_result.get("status") != "fetched":
            return {**metadata_result, "url": url, "fetch_url": metadata_url}
        try:
            metadata = json.loads(decode_body(metadata_result["_data"], str(metadata_result.get("content_type", ""))))
        except (TypeError, json.JSONDecodeError):
            return {
                **source_info(url, registry),
                "status": "invalid_source",
                "url": url,
                "fetch_url": metadata_url,
                "reason": "normas_metadata_is_not_json",
            }
        content_url = current_normas_content_url(metadata)
        if not content_url:
            return {
                **source_info(url, registry),
                "status": "invalid_source",
                "url": url,
                "fetch_url": metadata_url,
                "reason": "current_compilation_not_available",
            }
        content_result = request_bytes(content_url, registry, "text/html, text/plain, application/xhtml+xml")
        if content_result.get("status") != "fetched":
            return {**content_result, "url": url, "fetch_url": content_url, "metadata_url": metadata_url}
        data = content_result["_data"]
        content_type = str(content_result.get("content_type", ""))
        text = decode_body(data, content_type)
        unusable_reason = is_unusable_official_response(text, content_type)
        if unusable_reason:
            return {
                **source_info(url, registry),
                "status": "invalid_source",
                "url": url,
                "fetch_url": content_url,
                "metadata_url": metadata_url,
                "reason": unusable_reason,
            }
        return {
            **source_info(url, registry),
            "status": "fetched",
            "url": url,
            "fetch_url": content_url,
            "metadata_url": metadata_url,
            "final_url": content_result.get("final_url"),
            "http_status": content_result.get("http_status"),
            "content_type": content_type,
            "bytes": len(data),
            "sha256_raw": hashlib.sha256(data).hexdigest(),
            "sha256_normalized": normalized_hash(text),
            "sha256_body": legal_body_hash(text, content_type),
            "_data": data,
        }

    result = request_bytes(url, registry, "text/html, text/plain, application/xhtml+xml, application/json")
    if result.get("status") != "fetched":
        return result
    data = result["_data"]
    content_type = str(result.get("content_type", ""))
    text = decode_body(data, content_type)
    unusable_reason = is_unusable_official_response(text, content_type)
    if unusable_reason:
        return {**result, "status": "invalid_source", "reason": unusable_reason}
    return {
        **result,
        "sha256_raw": hashlib.sha256(data).hexdigest(),
        "sha256_normalized": normalized_hash(text),
        "sha256_body": legal_body_hash(text, content_type),
    }


def output_report(report: dict[str, object], path: Path | None) -> None:
    serializable = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serializable, encoding="utf-8")
    print(serializable, end="")


def fetch_plan(plan: list[dict[str, object]], registry: dict[str, object], snapshot_dir: Path) -> dict[str, object]:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    max_retries = int(registry["policy"].get("max_retries", 2))
    results: list[dict[str, object]] = []
    for item in plan:
        result: dict[str, object] = {key: value for key, value in item.items() if key != "urls"}
        result["attempts"] = []
        successful: list[dict[str, object]] = []
        snapshot_files: list[str] = []
        for url_index, url in enumerate(item["urls"]):
            fetched: dict[str, object] = {"status": "network_error", "url": str(url), "reason": "not attempted"}
            for attempt in range(max_retries + 1):
                fetched = fetch_one(str(url), registry)
                if fetched.get("status") in {"fetched", "invalid_source", "redirect_blocked", "response_too_large"} or attempt == max_retries:
                    break
                time.sleep(0.5 * (attempt + 1))
            public_result = {key: value for key, value in fetched.items() if key != "_data"}
            if fetched.get("status") == "fetched":
                filename = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(item["matrix_id"])) + f"-{url_index}.source"
                target = snapshot_dir / filename
                target.write_bytes(fetched["_data"])
                public_result["snapshot_file"] = snapshot_display_path(target)
                snapshot_files.append(snapshot_display_path(target))
                successful.append(fetched)
            result["attempts"].append(public_result)
        invalid_attempts = [item for item in result["attempts"] if item.get("status") == "invalid_source"]
        if invalid_attempts:
            result["invalid_attempt_count"] = len(invalid_attempts)
        if not successful:
            result["status"] = "source_invalid" if invalid_attempts else "source_unavailable"
        else:
            normalized = {str(item["sha256_body"]) for item in successful}
            raw = {str(item["sha256_raw"]) for item in successful}
            if len(normalized) > 1 and result.get("comparison_mode") != "complementary_sources":
                result["status"] = "source_conflict"
            elif result.get("current_hash_kind") == "per_source" and result.get("current_sha256_by_source"):
                current_by_source = result["current_sha256_by_source"]
                fetched_by_source = {
                    str(item["url"]): str(item["sha256_body"])
                    for item in successful
                }
                result["status"] = "unchanged" if fetched_by_source == current_by_source else "changed_candidate"
            elif result.get("current_sha256") and (
                (result.get("current_hash_kind") == "legal_body" and successful[0]["sha256_body"] == result["current_sha256"])
                or (result.get("current_hash_kind") != "legal_body" and successful[0]["sha256_raw"] == result["current_sha256"])
            ):
                result["status"] = "unchanged"
            else:
                result["status"] = "changed_candidate"
            result["source_hashes"] = {"normalized": sorted(normalized), "raw": sorted(raw)}
            result["snapshot_files"] = snapshot_files
            result["snapshot_file"] = snapshot_files[0]
            result["sha256_raw"] = successful[0]["sha256_raw"]
            result["sha256_normalized"] = successful[0]["sha256_normalized"]
            result["sha256_body"] = successful[0]["sha256_body"]
        results.append(result)
        if item["urls"]:
            time.sleep(max(0.05, max(source_rate_limit(str(url), registry) for url in item["urls"])))
    return {
        "results": results,
        "fetched_count": sum(item["status"] in {"unchanged", "changed_candidate"} for item in results),
        "changed_candidate_count": sum(item["status"] == "changed_candidate" for item in results),
        "conflict_count": sum(item["status"] == "source_conflict" for item in results),
        "unavailable_count": sum(item["status"] == "source_unavailable" for item in results),
        "invalid_source_count": sum(item["status"] == "source_invalid" for item in results),
        "invalid_attempt_count": sum(int(item.get("invalid_attempt_count", 0)) for item in results),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="fetch official sources into .private; default is network-free")
    parser.add_argument("--mode", choices=("dry_run", "proposal"), help="explicit acquisition mode; --fetch is a compatibility alias for proposal")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--priority", action="append", choices=("P0", "P1", "P2"), help="restrict the run to one or more matrix priorities")
    parser.add_argument("--matrix-id", action="append", help="restrict the run to explicit matrix IDs")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--input", type=Path, default=MATRIX, help="CSV de escopo; por padrão, a matriz curada")
    args = parser.parse_args()
    load_modes()
    try:
        mode = resolve_mode(args.mode, legacy_fetch=args.fetch)
    except ValueError as error:
        parser.error(str(error))
    if mode == "dry_run" and args.fetch:
        parser.error("--fetch is incompatible with --mode dry_run")
    registry = load_registry()
    all_plan = build_plan(args.as_of, args.input)
    plan = select_plan(all_plan, args.priority)
    if args.matrix_id:
        selected_ids = set(args.matrix_id)
        plan = [item for item in plan if item["matrix_id"] in selected_ids]
    if args.limit:
        plan = plan[:args.limit]
    report: dict[str, object] = {"schema": "legislation-collection-report/v1", "generated_at": datetime.now(timezone.utc).isoformat(), "mode": mode, "command": " ".join(sys.argv), "python": sys.version.split()[0], "as_of": args.as_of.isoformat(), "input_path": args.input.relative_to(ROOT).as_posix() if args.input.is_relative_to(ROOT) else str(args.input), "matrix_count": len(all_plan), "planned_count": len(plan), "priority_filter": args.priority or ["P0", "P1", "P2"], "source_registry": REGISTRY.relative_to(ROOT).as_posix(), "source_registry_sha256": hashlib.sha256(REGISTRY.read_bytes()).hexdigest(), "plan": plan}
    if mode == "proposal":
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fetched = fetch_plan(plan, registry, DEFAULT_PRIVATE / "snapshots" / stamp)
        report.update(fetched)
        private_manifest = DEFAULT_PRIVATE / "manifests" / f"{stamp}.json"
        report["private_manifest"] = str(private_manifest.relative_to(ROOT))
        private_manifest.parent.mkdir(parents=True, exist_ok=True)
        private_manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_report(report, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
