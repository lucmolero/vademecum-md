"""Create a review queue for new official acts without adding them to the corpus.

Discovery adapters can feed a JSON array of objects containing at least ``url``.
Every accepted item remains a candidate until a curator maps it to the editorial
matrix and a human-reviewed reconciliation is merged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from collect_legislation import host_allowed, load_registry


ROOT = Path(__file__).parents[2]
DISCOVERY_REGISTRY = ROOT / "manifests/discovery-registry.json"


def load_candidates(path: Path | None) -> list[dict[str, object]]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("A entrada de descoberta deve ser uma lista JSON.")
    return [item for item in payload if isinstance(item, dict)]


def discover_from_catalogs() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    registry = load_registry()
    catalogs = json.loads(DISCOVERY_REGISTRY.read_text(encoding="utf-8")).get("catalogs", [])
    candidates: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    for catalog in catalogs:
        url = str(catalog["url"])
        request = Request(url, headers={"User-Agent": "vademecum-md-discovery/0.1", "Accept": "text/html"})
        try:
            with urlopen(request, timeout=30) as response:
                limit = int(catalog.get("max_bytes", 5 * 1024 * 1024))
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError("catalog_response_too_large")
                html = data.decode("utf-8", errors="replace")
        except Exception as error:  # network adapters must report and continue
            errors.append({"catalog": str(catalog.get("id")), "url": url, "error": str(error)})
            continue
        for href, title in re.findall(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, re.I | re.S):
            candidate_url = urljoin(url, href).split("#", 1)[0]
            normalized_title = re.sub(r"<[^>]+>", " ", title)
            normalized_title = re.sub(r"\s+", " ", normalized_title).strip()
            parsed = urlparse(candidate_url)
            path_text = candidate_url.lower()
            is_legal_candidate = (
                host_allowed(candidate_url, registry)
                and parsed.scheme in {"http", "https"}
                and ("urn=urn:lex:" in path_text or "/lei" in path_text or "/decreto" in path_text)
            )
            if is_legal_candidate:
                candidates.append({"url": candidate_url, "titulo": normalized_title, "catalog": catalog.get("id")})
        time.sleep(float(catalog.get("rate_limit_seconds", 1.0)))
    return candidates, errors


def build_queue(candidates: list[dict[str, object]]) -> dict[str, object]:
    registry = load_registry()
    accepted: dict[str, dict[str, object]] = {}
    rejected: list[dict[str, object]] = []
    for item in candidates:
        url = str(item.get("url", "")).strip()
        if not url or not host_allowed(url, registry):
            rejected.append({"url": url, "reason": "host_not_allowlisted"})
            continue
        candidate_id = "candidate-" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        accepted[candidate_id] = {
            "candidate_id": candidate_id,
            "url": url,
            "titulo": item.get("titulo"),
            "tipo": item.get("tipo"),
            "numero": item.get("numero"),
            "ano": item.get("ano"),
            "status": "candidate",
            "auto_include": False,
            "review_required": True,
        }
    return {
        "schema": "legislation-discovery-queue/v1",
        "generated_at": date.today().isoformat(),
        "policy": "discovery_never_adds_to_curated",
        "candidates": sorted(accepted.values(), key=lambda item: str(item["candidate_id"])),
        "rejected": rejected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--fetch", action="store_true", help="consultar catálogos oficiais de descoberta")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidates = load_candidates(args.input)
    catalog_errors: list[dict[str, str]] = []
    if args.fetch:
        discovered, catalog_errors = discover_from_catalogs()
        candidates.extend(discovered)
    queue = build_queue(candidates)
    queue["catalog_errors"] = catalog_errors
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidates": len(queue["candidates"]), "rejected": len(queue["rejected"]), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
