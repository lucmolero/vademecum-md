"""Build the compact Atlas reader data from the canonical corpus."""
from pathlib import Path
import collections
import gzip
import hashlib
import html
import json
import re
import sys
import unicodedata

import markdown
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "site_docs/generated/atlas"
OUT = OUTPUT / "data"
STOP = set("a o as os de da do das dos e em no na nos nas um uma que se por para com ao aos ou art".split())
ALIASES = {
    "br-federal-constituicao-1988": ("Constituição Federal", "CF", "CF88"),
    "br-federal-lei_ordinaria-10406-2002": ("Código Civil", "CC"),
    "br-federal-lei_ordinaria-13105-2015": ("Código de Processo Civil", "CPC"),
    "br-federal-decreto_lei-2848-1940": ("Código Penal", "CP"),
    "br-federal-decreto_lei-3689-1941": ("Código de Processo Penal", "CPP"),
    "br-federal-decreto_lei-5452-1943": ("Consolidação das Leis do Trabalho", "CLT"),
    "br-federal-lei_ordinaria-8078-1990": ("Código de Defesa do Consumidor", "CDC"),
    "br-federal-lei_ordinaria-5172-1966": ("Código Tributário Nacional", "CTN"),
}
ART = re.compile(r"(?m)^[ \t]*(?:\*\*)?Art\.\s*([0-9]+(?:\s*[ºª°])?(?:\s*[-–]\s*[A-Za-z])?)\.?", re.I)
ALLOWED = set("p strong em b i h1 h2 h3 h4 h5 h6 ul ol li blockquote a table thead tbody tr th td code pre hr br sup sub del".split())


def norm(value):
    return "".join(c for c in unicodedata.normalize("NFD", str(value).lower()) if not unicodedata.combining(c))


def shard(term):
    value = 0
    for c in term:
        value = (value * 31 + ord(c)) % 64
    return value


def tokens(value):
    return {t for t in re.findall(r"[a-z0-9]+", norm(value)) if len(t) > 1 and t not in STOP}


def safe_html(value):
    soup = BeautifulSoup(markdown.markdown(value, extensions=["tables", "sane_lists"]), "html.parser")
    for tag in list(soup.find_all(True)):
        if tag.name in {"script", "style", "iframe", "object"}:
            tag.decompose()
        elif tag.name not in ALLOWED:
            tag.unwrap()
        else:
            attrs = {}
            if tag.name == "a":
                href = str(tag.get("href", ""))
                if re.match(r"^https?://", href, re.I):
                    attrs = {"href": href, "target": "_blank", "rel": "noopener noreferrer"}
            tag.attrs = attrs
    return str(soup), soup.get_text(" ", strip=True)


def emit(name, value):
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str).encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    digest = hashlib.sha256(compressed).hexdigest()
    filename = f"{name}.{digest[:12]}.json.gz"
    (OUT / filename).write_bytes(compressed)
    return {"file": f"data/{filename}", "bytes": len(compressed), "rawBytes": len(raw), "sha256": digest}


RELATION_LABELS = {
    "altera": "altera", "alterada_por": "é alterada por",
    "revoga": "revoga", "revogada_por": "é revogada por",
    "regulamenta": "regulamenta", "regulamentada_por": "é regulamentada por",
    "suspende": "suspende", "suspensa_por": "tem a eficácia suspensa por",
    "retifica": "retifica", "retificada_por": "é retificada por",
}


def graph_asset(documents):
    """Keep the graph directional and preserve published evidence fields."""
    graph_path = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    if not graph_path.is_file():
        return {"schema": "atlas-relations/1", "edges": []}
    known = {row["id"] for row in documents}
    edges = []
    for line_number, line in enumerate(graph_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        source, target = str(row.get("source_id") or ""), str(row.get("target_id") or "")
        if source not in known or target not in known:
            continue
        kind = str(row.get("type") or "")
        edges.append({
            "id": f"relation-{line_number}", "source": source, "target": target,
            "type": kind, "label": RELATION_LABELS.get(kind, kind.replace("_", " ")),
            "device": row.get("dispositivo"), "effect": row.get("data_efeito"),
            "confidence": row.get("confianca"), "review": row.get("status_revisao"),
            "source_url": row.get("fonte"), "evidence": row.get("evidencia_textual"),
            "evidence_sha256": row.get("evidencia_sha256"),
        })
    return {"schema": "atlas-relations/1", "edges": edges}


def build(root):
    global OUT
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        for old in OUT.glob("*.json.gz"):
            old.unlink()
    OUT.mkdir(exist_ok=True)
    paths = sorted(root.rglob("*.md"))
    docs, table = [], []
    packs = [{} for _ in range(16)]
    postings = [collections.defaultdict(list) for _ in range(64)]
    source_bytes, source_segments, articles = 0, 0, 0
    for path in paths:
        original = path.read_bytes()
        text = original.decode("utf-8-sig")
        if not text.startswith("---"):
            continue
        _, header, body = text.split("---", 2)
        meta = yaml.safe_load(header)
        if not meta.get("id"):
            continue
        source_bytes += len(original)
        identifier = meta["id"]
        alias = ALIASES.get(identifier, ())
        title = alias[0] if alias else str(meta["titulo"])
        pack_no = int(hashlib.sha256(identifier.encode()).hexdigest()[:8], 16) % 16
        matches = list(ART.finditer(body))
        segments = []
        if not matches:
            segments = [("abertura", "Texto da norma", body)]
        else:
            if body[:matches[0].start()].strip():
                segments.append(("abertura", "Abertura", body[:matches[0].start()]))
            seen = collections.Counter()
            for i, match in enumerate(matches):
                number = re.sub(r"\s|[ºª°]", "", match.group(1)).lower().replace("–", "-")
                anchor = f"art-{number}"
                seen[anchor] += 1
                if seen[anchor] > 1:
                    anchor += f"-{seen[anchor]}"
                segment = body[match.start(): matches[i + 1].start() if i + 1 < len(matches) else len(body)]
                segments.append((anchor, f"Art. {match.group(1).strip()}", segment))
                articles += 1
            reconstructed = "".join(segment for _, _, segment in segments)
            # Only a whitespace-only preamble is permitted to be omitted.
            assert reconstructed.lstrip() == body.lstrip(), path
        blocks = []
        di = len(docs)
        for anchor, label, segment in segments:
            rendered, plain = safe_html(segment)
            bi = len(blocks)
            blocks.append({"id": anchor, "label": label, "html": rendered, "text": plain})
            rowid = len(table)
            table.append([di, bi, plain[:100]])
            for term in tokens(plain):
                postings[shard(term)][term].append(rowid)
            source_segments += len(segment.encode())
        info = {
            "id": identifier, "title": title, "canonicalTitle": meta["titulo"],
            "aliases": list(alias[1:]), "domain": str(meta.get("dominio", "Federal")).replace("_", " ").capitalize(),
            "type": str(meta.get("tipo", "Norma")).replace("_", " "), "number": str(meta.get("numero") or ""),
            "year": meta.get("ano"), "cutoff": str(meta.get("data_corte", "")),
            "source": next(iter(meta.get("fonte_oficial") or []), ""), "status": str(meta.get("situacao", "não informado")).replace("_", " "),
            "hash": meta.get("sha256_published_body", ""), "fileHash": hashlib.sha256(original).hexdigest(),
            "path": path.relative_to(root).as_posix(), "pack": pack_no,
            "outline": [[b["id"], b["label"]] for b in blocks], "articles": len(matches),
        }
        docs.append(info)
        packs[pack_no][identifier] = {"id": identifier, "blocks": blocks}
    assert len({d["id"] for d in docs}) == len(docs)
    # Delta encoding exploits sorted article IDs without a WASM runtime.
    for index in postings:
        for term, values in index.items():
            previous = 0
            deltas = []
            for value in values:
                deltas.append(value - previous)
                previous = value
            index[term] = deltas
    release_path = ROOT / "manifests/release.json"
    version = json.loads(release_path.read_text(encoding="utf-8")).get("version", "snapshot") if release_path.is_file() else "snapshot"
    cutoff = max(d["cutoff"] for d in docs)
    graph_data = graph_asset(docs)
    graph = emit("graph", graph_data)
    manifest = {
        "schema": "atlas-reader/1", "snapshot": f"v{version}-{cutoff}", "count": len(docs),
        "cutoff": max(d["cutoff"] for d in docs), "sourceBytes": source_bytes,
        "articleCount": articles, "blockCount": len(table), "catalog": emit("catalog", docs),
        "table": emit("results", table), "packs": [emit(f"pack-{i:02}", pack) for i, pack in enumerate(packs)],
        "shards": [emit(f"terms-{i:02}", index) for i, index in enumerate(postings)],
        "graph": graph,
        "graphEdgeCount": len(graph_data["edges"]),
    }
    manifest["offlineBytes"] = sum(item["bytes"] for item in [manifest["catalog"], manifest["table"], *manifest["packs"], *manifest["shards"], manifest["graph"]])
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {
        "documents": len(docs), "articles": articles, "blocks": len(table), "markdownBytes": source_bytes,
        "catalogGzipBytes": manifest["catalog"]["bytes"], "documentPacksGzipBytes": sum(p["bytes"] for p in manifest["packs"]),
        "searchGzipBytes": sum(p["bytes"] for p in manifest["shards"]) + manifest["table"]["bytes"],
        "maxPackGzipBytes": max(p["bytes"] for p in manifest["packs"]),
        "offlineDataGzipBytes": manifest["offlineBytes"], "uniqueTerms": sum(len(p) for p in postings),
        "validation": "All IDs unique; all source article segments retained; all pack references generated from same build.",
    }
    (OUTPUT / "build-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    build(Path(sys.argv[1]).resolve())
