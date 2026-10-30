"""Compose the Vademecum homepage, official library and governance docs for Pages."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _copy_contents(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Frontend build output is missing: {source}")
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def _release_metadata(site: Path) -> dict[str, object]:
    release = json.loads((ROOT / "manifests/release.json").read_text(encoding="utf-8"))
    catalog_path = ROOT / "biblioteca/dist/catalog.json"
    source_path = ROOT / "biblioteca/dist/vademecum-source.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    official = [item for item in catalog if item.get("collection") == "vademecum"]
    expected = int(release.get("corpus_count", 0))
    ids = [str(item.get("id", "")) for item in official]
    if not expected or len(official) != expected:
        raise ValueError(f"Pages precisa publicar {expected} documentos oficiais; o catálogo tem {len(official)}")
    if len(set(ids)) != len(ids) or any(not item for item in ids):
        raise ValueError("O catálogo oficial contém IDs vazios ou duplicados")
    if len(catalog) != len(official):
        raise ValueError("O build de produção incluiu Markdown local/de teste junto ao acervo oficial")
    if source.get("version") != release.get("version") or source.get("documentCount") != expected:
        raise ValueError("A biblioteca e o manifesto não representam a mesma release do acervo")
    commit = os.environ.get("VADE_COMMIT", "")
    if commit and source.get("commit") != commit:
        raise ValueError("O commit de origem da biblioteca difere do commit que gerou o corpus")
    if not all(item.get("sourceHash") for item in official):
        raise ValueError("Há documentos sem hash de origem no catálogo oficial")
    return {
        "schema": "vademecum-pages-release/v1",
        "version": release["version"],
        "generatedAt": release.get("generated_at", ""),
        "cutoff": source.get("cutoff", ""),
        "documentCount": expected,
        "source": {
            "repository": "lucmolero/vademecum-md",
            "ref": source.get("ref", "main"),
            "commit": source.get("commit", ""),
        },
        "applications": {
            "homepage": {"path": "/", "version": release["version"]},
            "library": {"path": "/biblioteca/", "version": release["version"]},
        },
    }


def _legacy_service_worker_migration() -> str:
    return '''"use strict";
self.addEventListener("install", (event) => event.waitUntil(self.skipWaiting()));
self.addEventListener("activate", (event) => event.waitUntil((async () => {
  for (const name of await caches.keys()) {
    if (name.startsWith("atlas-shell-") || name.startsWith("atlas-data-")) await caches.delete(name);
  }
  await self.registration.unregister();
  const clients = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
  for (const client of clients) client.postMessage({ type: "VADEMECUM_LEGACY_CACHE_CLEARED" });
  await self.clients.claim();
})()));
'''


def _reader_compatibility_page() -> str:
    return '''<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>Biblioteca Vademecum</title></head>
<body><main><h1>A biblioteca do Vademecum mudou de endereço</h1><p><a id="destination" href="../biblioteca/">Abrir biblioteca e leitor</a></p></main>
<script>
const [documentId, articleId] = decodeURIComponent(location.hash.slice(1)).split('/', 2);
if (documentId) {
  const params = new URLSearchParams({documento: documentId});
  if (articleId && /^art-[a-z0-9-]+$/i.test(articleId)) params.set('artigo', articleId);
  const next = new URL('../biblioteca/', location.href);
  next.hash = params.toString();
  location.replace(next.href);
}
</script></body></html>
'''


def compose(site: Path) -> dict[str, object]:
    site = site.resolve()
    if not site.is_dir() or not (site / "generated/catalog/index.html").is_file():
        raise FileNotFoundError("MkDocs deve ser compilado antes de compor o Pages")
    homepage = ROOT / "homepage/dist"
    library = ROOT / "biblioteca/dist"
    home_html = (homepage / "index.html").read_text(encoding="utf-8")
    home_scripts = [homepage / item.removeprefix("./") for item in re.findall(r'<script[^>]+src="(\./assets/[^"]+\.js)"', home_html)]
    if not home_scripts or not any("biblioteca/" in item.read_text(encoding="utf-8", errors="replace") for item in home_scripts):
        raise ValueError("Homepage compilada não aponta para /biblioteca/")
    _release_metadata(site)

    for name in ("style.css", "graph.css", "app.js", "engine.js", "graph.js", "icon.svg", "sw.js"):
        (site / name).unlink(missing_ok=True)
    for name in ("fonts", "generated/atlas", "generated/reader-data"):
        target = site / name
        if target.is_dir():
            shutil.rmtree(target)
    _copy_contents(homepage, site)
    _copy_contents(library, site / "biblioteca")

    release = _release_metadata(site)
    payload = json.dumps(release, ensure_ascii=False, indent=2) + "\n"
    (site / "vademecum-release.json").write_text(payload, encoding="utf-8", newline="\n")
    (site / "biblioteca/vademecum-release.json").write_text(payload, encoding="utf-8", newline="\n")
    (site / "reader").mkdir(parents=True, exist_ok=True)
    (site / "reader/index.html").write_text(_reader_compatibility_page(), encoding="utf-8", newline="\n")
    (site / "sw.js").write_text(_legacy_service_worker_migration(), encoding="utf-8", newline="\n")
    (site / ".nojekyll").touch()

    if not (site / "assets").is_dir() or not (site / "biblioteca/catalog.json").is_file():
        raise ValueError("Homepage ou biblioteca não foi copiada para o Pages")
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    print(json.dumps(compose(args.site), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
