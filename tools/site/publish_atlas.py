"""Install the Atlas reader shell at the Pages root after MkDocs is built."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / "tools/site/atlas-shell"
ASSETS = (
    "index.html", "style.css", "graph.css", "app.js", "engine.js", "graph.js", "icon.svg",
    "fonts/manrope.woff2", "fonts/literata.woff2", "fonts/literata-italic.woff2",
)


def publish(site: Path) -> str:
    site = site.resolve()
    if not site.is_dir():
        raise FileNotFoundError(f"MkDocs output directory does not exist: {site}")
    data_root = site / "generated/atlas"
    manifest_path = data_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "atlas-reader/1" or not manifest.get("count"):
        raise ValueError("Atlas manifest is missing or incompatible.")
    if "graph" not in manifest:
        raise ValueError("Atlas manifest has no normative graph asset.")
    for item in [manifest["catalog"], manifest["table"], *manifest["packs"], *manifest["shards"], manifest["graph"]]:
        path = data_root / item["file"]
        payload = path.read_bytes()
        if len(payload) != item["bytes"] or hashlib.sha256(payload).hexdigest() != item["sha256"]:
            raise ValueError(f"Generated Atlas asset failed integrity validation: {path.name}")

    for relative in ASSETS:
        source = SHELL / relative
        destination = site / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    digest = hashlib.sha256()
    for relative in ASSETS:
        digest.update((site / relative).read_bytes())
    digest.update(manifest_path.read_bytes())
    version = digest.hexdigest()[:16]
    snapshot = "".join(ch for ch in str(manifest["snapshot"]) if ch.isalnum() or ch in "-_")
    worker = f'''"use strict";
const VERSION = {json.dumps(version)};
const SHELL = "atlas-shell-" + VERSION;
const DATA = "atlas-data-{snapshot}";
const ASSETS = {json.dumps(list(ASSETS), ensure_ascii=False)};
const ROOT = new URL("./", self.registration.scope);
const ASSET_URLS = new Set(ASSETS.map((path) => new URL(path, ROOT).href));
self.addEventListener("install", (event) => {{
  event.waitUntil(caches.open(SHELL).then((cache) => cache.addAll([...ASSET_URLS])));
}});
self.addEventListener("activate", (event) => {{ event.waitUntil(self.clients.claim()); }});
self.addEventListener("fetch", (event) => {{
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin || !url.href.startsWith(ROOT.href)) return;
  if (url.pathname.includes("/generated/atlas/data/")) {{
    event.respondWith(caches.open(DATA).then(async (cache) => {{
      const cached = await cache.match(request);
      if (cached) return cached;
      const response = await fetch(request);
      if (response.ok) await cache.put(request, response.clone());
      return response;
    }}));
    return;
  }}
  const isRootNavigation = request.mode === "navigate" && (url.pathname === ROOT.pathname || url.pathname === new URL("index.html", ROOT).pathname);
  if (!isRootNavigation && !ASSET_URLS.has(url.href)) return;
  event.respondWith(caches.open(SHELL).then(async (cache) => {{
    const key = isRootNavigation ? new URL("index.html", ROOT).href : request;
    return (await cache.match(key)) || fetch(request);
  }}));
}});
'''
    (site / "sw.js").write_text(worker, encoding="utf-8", newline="\n")
    print(json.dumps({
        "published": str(site), "snapshot": manifest["snapshot"],
        "documents": manifest["count"], "graph_asset_bytes": manifest["graph"]["bytes"],
        "shell_version": version,
    }, ensure_ascii=False))
    return version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", nargs="?", default=str(ROOT / "site"), help="MkDocs output directory")
    args = parser.parse_args()
    publish(Path(args.site))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
