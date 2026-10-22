"""Generate the editorial site layer from the canonical Markdown corpus.

The site is deliberately derived: it may add navigation, metadata panels and
article anchors, but it never rewrites the canonical corpus under bases/.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
import shutil
import sys
import textwrap
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from migrate_public_corpus import CURATED, parse_frontmatter  # noqa: E402

SITE = ROOT / "site_docs"
GENERATED = SITE / "generated"
ARTICLE_LINE = re.compile(
    r"^\s*(?:\*\*)?(Art\.\s+[0-9]+(?:\s*[ºª°])?(?:\s*-\s*[A-Za-z])?\.?)"
    r"(?:\*\*)?(.*)$",
    re.IGNORECASE,
)


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def metadata_text(value: object, fallback: str = "") -> str:
    """Normalize nullable front-matter values before publishing them as labels."""
    if value is None:
        return fallback
    text = str(value).strip()
    return fallback if text.casefold() in {"none", "null"} else text


@lru_cache(maxsize=1)
def official_source_hosts() -> frozenset[str]:
    registry = ROOT / "manifests/sources-registry.json"
    payload = json.loads(registry.read_text(encoding="utf-8")) if registry.is_file() else {}
    return frozenset(
        str(host).lower().lstrip(".").rstrip(".")
        for source in payload.get("sources", [])
        for host in source.get("hosts", [])
    )


def safe_official_url(value: object) -> str:
    url = str(value or "").strip()
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower().rstrip(".")
        trusted_host = any(
            hostname == allowed or hostname.endswith("." + allowed)
            for allowed in official_source_hosts()
        )
        if (
            parsed.scheme == "https"
            and trusted_host
            and not parsed.username
            and not parsed.password
            and parsed.port in (None, 443)
        ):
            return url
    except ValueError:
        pass
    return ""


def slugify(value: str) -> str:
    plain = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-") or "especializado"


DOMAIN_LABELS = {
    "direitos_digitais": "Direitos digitais",
    "direitos_sociais": "Direitos sociais",
    "eleitoral_constitucional": "Eleitoral constitucional",
    "empresarial_civil": "Empresarial civil",
    "introducao": "Introdução",
    "legislacao_complementar": "Legislação complementar",
    "mineracao": "Mineração",
    "normas_complementares": "Normas complementares",
    "previdenciario": "Previdenciário",
    "processo_civil": "Processo civil",
    "processo_penal": "Processo penal",
    "seguranca_publica": "Segurança pública",
}

POPULAR_TITLES: dict[str, str] = {
    "br-federal-constituicao-1988": "Constituição da República Federativa do Brasil de 1988",
    "br-federal-lei_ordinaria-10406-2002": "Código Civil",
    "br-federal-lei_ordinaria-13105-2015": "Código de Processo Civil",
    "br-federal-decreto_lei-2848-1940": "Código Penal",
    "br-federal-decreto_lei-3689-1941": "Código de Processo Penal",
    "br-federal-decreto_lei-5452-1943": "Consolidação das Leis do Trabalho (CLT)",
    "br-federal-lei_ordinaria-8078-1990": "Código de Defesa do Consumidor",
    "br-federal-lei_ordinaria-14133-2021": "Nova Lei de Licitações e Contratos",
    "br-federal-lei_ordinaria-8906-1994": "Estatuto da Advocacia e da OAB",
    "br-federal-lei_ordinaria-5172-1966": "Código Tributário Nacional",
    "br-federal-lei_ordinaria-12846-2013": "Lei Anticorrupção (Lei nº 12.846/2013)",
    "br-federal-lei_ordinaria-11445-2007": "Marco Legal do Saneamento Básico (Lei nº 11.445/2007)",
    "br-federal-lei_ordinaria-13726-2018": "Lei da Desburocratização (Lei nº 13.726/2018)",
    "br-federal-lei_ordinaria-13022-2014": "Estatuto das Guardas Municipais (Lei nº 13.022/2014)",
    "br-federal-lei_ordinaria-8625-1993": "Lei Orgânica do Ministério Público (Lei nº 8.625/1993)",
    "br-federal-lei_ordinaria-14478-2022": "Marco dos Criptoativos (Lei nº 14.478/2022)",
    "br-federal-lei_ordinaria-12187-2009": "Política sobre Mudança do Clima (Lei nº 12.187/2009)",
    "br-federal-lei_ordinaria-14119-2021": "Pagamento por Serviços Ambientais (Lei nº 14.119/2021)",
    "br-federal-lei_ordinaria-15190-2025": "Política de Linguagem Simples (Lei nº 15.190/2025)",
    "br-federal-lei_ordinaria-9784-1999": "Processo Administrativo Federal (Lei nº 9.784/1999)",
    "br-federal-lei_ordinaria-8429-1992": "Lei de Improbidade Administrativa",
    "br-federal-lei_ordinaria-12527-2011": "Lei de Acesso à Informação (LAI)",
    "br-federal-lei_ordinaria-13709-2018": "Lei Geral de Proteção de Dados (LGPD)",
    "br-federal-lei_ordinaria-13874-2019": "Declaração de Direitos de Liberdade Econômica",
}


FEATURED_LAW_IDS = (
    "br-federal-constituicao-1988", "br-federal-lei_ordinaria-10406-2002",
    "br-federal-lei_ordinaria-13105-2015", "br-federal-decreto_lei-2848-1940",
    "br-federal-decreto_lei-3689-1941", "br-federal-decreto_lei-5452-1943",
    "br-federal-lei_ordinaria-8078-1990", "br-federal-lei_ordinaria-8906-1994",
    "br-federal-lei_ordinaria-5172-1966", "br-federal-lei_ordinaria-14133-2021",
)
DOCUMENT_TYPE_LABELS = {
    "ato_constitucional": "Ato constitucional",
    "constituicao": "Constituição",
    "decreto": "Decreto",
    "decreto_lei": "Decreto-Lei",
    "lei_complementar": "Lei complementar",
    "lei_ordinaria": "Lei ordinária",
}


def domain_key(value: str) -> str:
    return re.sub(r"\s+", "_", value.strip().lower().replace("-", "_"))


def domain_label(value: str) -> str:
    key = domain_key(value)
    if key in DOMAIN_LABELS:
        return DOMAIN_LABELS[key]
    return value.replace("_", " ").replace("-", " ").strip().title() or "Especializado"


def article_anchors(body: str) -> str:
    """Add site-only headings before article lines without changing their text."""
    output: list[str] = []
    for line in body.strip().splitlines():
        match = ARTICLE_LINE.match(line) if line.lstrip().startswith(("**Art.", "Art.")) else None
        if match:
            label = re.sub(r"\s+", " ", match.group(1)).strip()
            output.extend([f"## {label}", "", line])
        else:
            output.append(line)
    return "\n".join(output).strip() + "\n"


def article_search_records(metadata: dict[str, object], body: str, relative: str) -> list[dict[str, str]]:
    document_id = str(metadata.get("id") or "")
    title = str(metadata.get("titulo") or "Diploma normativo")
    popular_title = POPULAR_TITLES.get(document_id, title)
    number = str(metadata.get("numero") or "")
    year = str(metadata.get("ano") or "")
    kind = str(metadata.get("tipo") or "")
    domain = str(metadata.get("dominio") or "")
    status = str(metadata.get("situacao") or "desconhecida")
    href = "generated/laws/" + relative.removesuffix(".md").rstrip("/") + "/"
    records = [{
        "kind": "document",
        "id": document_id,
        "title": title,
        "popular_title": popular_title,
        "type": kind,
        "number": number,
        "year": year,
        "domain": domain,
        "status": status,
        "href": href,
    }]
    used_ids: Counter[str] = Counter()
    for line in body.strip().splitlines():
        match = ARTICLE_LINE.match(line) if line.lstrip().startswith(("**Art.", "Art.")) else None
        if not match:
            continue
        label = re.sub(r"\s+", " ", match.group(1)).strip()
        base_id = slugify(label)
        duplicate = used_ids[base_id]
        used_ids[base_id] += 1
        article_id = base_id if duplicate == 0 else f"{base_id}_{duplicate}"
        records.append({
            "kind": "article",
            "id": document_id,
            "title": title,
            "popular_title": popular_title,
            "type": kind,
            "number": number,
            "year": year,
            "domain": domain,
            "status": status,
            "article": label,
            "href": href + "#" + article_id,
        })
    return records


RELATION_LABELS = {
    "altera": "altera",
    "alterada_por": "é alterada por",
    "revoga": "revoga",
    "revogada_por": "é revogada por",
    "regulamenta": "regulamenta",
    "regulamentada_por": "é regulamentada por",
    "suspende": "suspende",
    "suspensa_por": "tem a eficácia suspensa por",
    "retifica": "retifica",
    "retificada_por": "é retificada por",
}
DEVICE_TARGET_TYPES = {"altera", "revoga", "regulamenta", "suspende", "retifica"}
DEVICE_SOURCE_TYPES = {"alterada_por", "revogada_por", "regulamentada_por", "suspensa_por", "retificada_por"}
INVERSE_RELATIONS = {
    "alterada_por": "altera",
    "revogada_por": "revoga",
    "regulamentada_por": "regulamenta",
    "suspensa_por": "suspende",
    "retificada_por": "retifica",
}


def article_key(value: object) -> str | None:
    """Return an article identifier only when the relation names one."""
    match = re.search(r"\bart\.?\s*(\d+)(?:\s*[º°ª])?\s*(?:-\s*)?([a-z])?", str(value or ""), re.IGNORECASE)
    return f"{int(match.group(1))}{(match.group(2) or '').lower()}" if match else None


def deduplicate_relation_mirrors(relations: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates: dict[tuple[object, ...], dict[str, object]] = {}
    for relation in relations:
        kind = str(relation.get("type") or "")
        canonical_type = INVERSE_RELATIONS.get(kind, kind)
        source, target = str(relation.get("source_id") or ""), str(relation.get("target_id") or "")
        canonical_source, canonical_target = (
            (target, source) if kind in INVERSE_RELATIONS else (source, target)
        )
        key = (
            canonical_type,
            canonical_source,
            canonical_target,
            str(relation.get("dispositivo") or ""),
            str(relation.get("data_efeito") or ""),
            str(relation.get("evidencia_sha256") or ""),
        )
        current = candidates.get(key)
        if current is None or (kind == canonical_type and current.get("type") != canonical_type):
            candidates[key] = relation
    return list(candidates.values())


def relation_index(rows: list[dict[str, str]]) -> dict[str, list[dict[str, object]]]:
    graph = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    if not graph.is_file():
        return {}
    titles = {row["id"]: row["title"] for row in rows}
    relations: list[dict[str, object]] = []
    for relation_number, line in enumerate(graph.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        relation = json.loads(line)
        source, target = str(relation.get("source_id") or ""), str(relation.get("target_id") or "")
        if source not in titles or target not in titles:
            continue
        relation["source_title"] = titles[source]
        relation["target_title"] = titles[target]
        relation["_site_id"] = f"normative-relation-{relation_number}"
        relation["_site_device_document_id"] = (
            target if relation.get("type") in DEVICE_TARGET_TYPES
            else source if relation.get("type") in DEVICE_SOURCE_TYPES
            else None
        )
        relations.append(relation)

    index: dict[str, list[dict[str, object]]] = {}
    # Keep the graph's original active edge when its inverse mirror exists.
    for relation in deduplicate_relation_mirrors(relations):
        for document_id in {str(relation["source_id"]), str(relation["target_id"])}:
            index.setdefault(document_id, []).append(relation)
    return index


def graph_index_data(rows: list[dict[str, str]], metrics: dict[str, object]) -> dict[str, object]:
    """Build a compact, exact topology index from the published JSONL graph."""
    by_id = {row["id"]: row for row in rows}
    graph_path = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    edges: list[dict[str, str]] = []
    neighbors: dict[str, set[str]] = {}
    representatives: dict[tuple[str, str], dict[str, str]] = {}
    if graph_path.is_file():
        for line in graph_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            relation = json.loads(line)
            source = str(relation.get("source_id") or "")
            target = str(relation.get("target_id") or "")
            if source not in by_id or target not in by_id or source == target:
                continue
            edge = {
                "source_id": source,
                "target_id": target,
                "type": str(relation.get("type") or "related_to"),
            }
            edges.append(edge)
            neighbors.setdefault(source, set()).add(target)
            neighbors.setdefault(target, set()).add(source)
            pair = tuple(sorted((source, target)))
            current = representatives.get(pair)
            if current is None or (
                edge["type"] in DEVICE_TARGET_TYPES
                and current["type"] not in DEVICE_TARGET_TYPES
            ):
                representatives[pair] = edge

    nodes = []
    for identifier, row in sorted(by_id.items(), key=lambda item: item[1]["title"].casefold()):
        site_path = row["path"].removeprefix("laws/").removesuffix(".md")
        canonical_path = row["path"].removeprefix("laws/federal/")
        nodes.append({
            "id": identifier,
            "title": row["title"],
            "label": POPULAR_TITLES.get(identifier, row["title"]),
            "type": row["type"],
            "number": row["number"],
            "year": row["year"],
            "degree": len(neighbors.get(identifier, set())),
            "href": f"../generated/laws/{site_path}/",
            "canonical_href": f"bases/curated/legislacao/federal/{canonical_path}",
        })

    featured: dict[str, object] = {"center_id": None, "node_ids": [], "edges": []}
    if neighbors:
        center = max(neighbors, key=lambda identifier: (len(neighbors[identifier]), identifier))
        ranked = sorted(
            neighbors[center],
            key=lambda identifier: (
                -len(neighbors[identifier]), by_id[identifier]["title"].casefold(), identifier
            ),
        )[:6]
        selected = {center, *ranked}
        featured = {
            "center_id": center,
            "node_ids": [center, *ranked],
            "edges": [
                edge for _, edge in sorted(representatives.items())
                if edge["source_id"] in selected and edge["target_id"] in selected
            ],
        }

    return {
        "schema": "vademecum-graph/v1",
        "release": str(metrics["version"]),
        "cutoff": str(metrics["cutoff"]),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "featured": featured,
    }


def graph_preview_svg(graph: dict[str, object]) -> str:
    """Render a GitHub-safe, static preview from the same graph subnetwork."""
    node_rows = {node["id"]: node for node in graph["nodes"]}
    featured = graph["featured"]
    identifiers = featured["node_ids"]
    if not identifiers:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 140"><text x="20" y="70">Grafo indisponível</text></svg>\n'
    coordinates = [(260, 205), (92, 92), (260, 64), (428, 92), (428, 318), (260, 348), (92, 318)]
    positions = {identifier: coordinates[index] for index, identifier in enumerate(identifiers)}
    edge_markup = []
    for edge in featured["edges"]:
        x1, y1 = positions[edge["source_id"]]
        x2, y2 = positions[edge["target_id"]]
        source = html.escape(node_rows[edge["source_id"]]["label"])
        target = html.escape(node_rows[edge["target_id"]]["label"])
        relation = html.escape(RELATION_LABELS.get(edge["type"], edge["type"].replace("_", " ")))
        edge_markup.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#b48a3c" stroke-width="2" marker-end="url(#arrow)">'
            f'<title>{source} — {relation} → {target}</title></line>'
        )
    node_markup = []
    for index, identifier in enumerate(identifiers):
        x, y = positions[identifier]
        node = node_rows[identifier]
        title = html.escape(node["label"])
        short = html.escape(textwrap.shorten(node["label"], width=25, placeholder="…"))
        fill = "#b48a3c" if index == 0 else "#2d7659"
        radius = 15 if index == 0 else 10
        node_markup.append(
            f'<g><title>{title} · {html.escape(identifier)}</title><circle cx="{x}" cy="{y}" '
            f'r="{radius}" fill="{fill}" stroke="#13243a" stroke-width="3"/>'
            f'<text x="{x}" y="{y + 31}" text-anchor="middle" fill="#13243a" '
            f'font-family="Arial,sans-serif" font-size="13">{short}</text></g>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 420" role="img" '
        'aria-labelledby="title desc"><title id="title">Recorte do grafo normativo</title>'
        '<desc id="desc">Sete diplomas conectados por relações direcionais do grafo publicado.</desc>'
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" '
        'orient="auto"><path d="M0 0L8 4L0 8Z" fill="#b48a3c"/></marker></defs>'
        '<rect width="520" height="420" rx="24" fill="#fbf8f0"/>'
        f'<g>{"".join(edge_markup)}</g><g>{"".join(node_markup)}</g></svg>\n'
    )


def markdown_link_text(value: object) -> str:
    """Escape user-facing labels for links embedded in a Markdown table."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>~])", r"\\\1", str(value))


def readme_graph_section(graph: dict[str, object]) -> str:
    """Provide useful, link-based graph navigation in GitHub's static README."""
    nodes = {node["id"]: node for node in graph["nodes"]}
    featured = graph["featured"]
    center = nodes.get(featured["center_id"])
    if not center:
        return (
            "## Explore relações entre as normas\n\n"
            "O grafo navegável está indisponível nesta geração. "
            "Consulte o [grafo normativo no GitHub Pages](https://lucmolero.github.io/vademecum-md/graph/)."
        )
    edges = featured["edges"]
    edge_count = f"{graph['edge_count']:,}".replace(",", ".")
    rows = [
        "## Explore relações entre as normas", "",
        f"O recorte abaixo parte de **{center['label']}** e reflete relações tipadas do grafo publicado "
        f"(**{graph['node_count']} diplomas · {edge_count} registros**, incluindo inversas). "
        "No README, use os links da tabela para abrir cada texto canônico; para buscar e percorrer "
        "vizinhos no grafo completo, abra o [explorador interativo no GitHub Pages](https://lucmolero.github.io/vademecum-md/graph/).", "",
        "[![Recorte navegável por links do grafo normativo; clique para abrir o explorador completo](site_docs/assets/normative-graph-preview.svg)](https://lucmolero.github.io/vademecum-md/graph/)", "",
        "| Origem | Relação registrada | Destino |", "| --- | --- | --- |",
    ]
    for edge in edges:
        source = nodes[edge["source_id"]]
        target = nodes[edge["target_id"]]
        relation = RELATION_LABELS.get(edge["type"], edge["type"].replace("_", " "))
        rows.append(
            f"| [{markdown_link_text(source['label'])}]({source['canonical_href']}) | {relation} → "
            f"| [{markdown_link_text(target['label'])}]({target['canonical_href']}) |"
        )
    rows.extend([
        "", "*O README do GitHub é estático: o diagrama é uma prévia. Cada nó da tabela abre o Markdown da lei; "
        "o Pages oferece busca, filtros por tipo/direção e navegação de vizinhos.*",
    ])
    return "\n".join(rows)


def update_readme_graph(graph: dict[str, object]) -> None:
    """Replace only the generated graph section, preserving the authored README."""
    path = ROOT / "README.md"
    content = path.read_text(encoding="utf-8")
    start_marker = "<!-- BEGIN GENERATED NORMATIVE GRAPH -->"
    end_marker = "<!-- END GENERATED NORMATIVE GRAPH -->"
    if content.count(start_marker) != 1 or content.count(end_marker) != 1:
        raise ValueError("README must contain exactly one pair of normative graph markers")
    start = content.index(start_marker) + len(start_marker)
    end = content.index(end_marker)
    if end <= start:
        raise ValueError("README normative graph markers are out of order")
    updated = content[:start] + "\n\n" + readme_graph_section(graph) + "\n\n" + content[end:]
    path.write_text(updated, encoding="utf-8", newline="\n")


def relation_markup(relation: dict[str, object], include_evidence: bool = True) -> str:
    kind = str(relation.get("type") or "relação não classificada")
    label = RELATION_LABELS.get(kind, kind.replace("_", " "))
    source = esc(relation.get("source_title") or relation.get("source_id"))
    target = esc(relation.get("target_title") or relation.get("target_id"))
    confidence = {
        "alta": "alta", "media": "média", "baixa": "baixa",
    }.get(str(relation.get("confianca") or ""), "não informada")
    review = str(relation.get("status_revisao") or "não informado").replace("_", " ")
    inverse_status = {
        "complete": "par inverso registrado",
        "excluded_by_policy": "par inverso excluído por política",
        "missing_inverse": "par inverso ausente",
    }.get(str(relation.get("status_relacao_inversa") or ""), "estado do par inverso não informado")
    device = str(relation.get("dispositivo") or "")
    effect = str(relation.get("data_efeito") or "")
    evidence = str(relation.get("evidencia_textual") or "")
    evidence_hash = str(relation.get("evidencia_sha256") or "")
    source_link = str(relation.get("fonte") or "")
    source_html = f'<a href="{esc(source_link)}" rel="noreferrer">fonte indicada no grafo</a>' if source_link else "fonte não informada"
    details = (
        f'<span class="relation-meta">Confiança: {esc(confidence)} · Revisão: {esc(review)}'
        f'{f" · Dispositivo: {esc(device)}" if device else " · Dispositivo não identificado"}'
        f'{f" · Efeito: {esc(effect)}" if effect else ""} · {esc(inverse_status)} · {source_html}</span>'
    )
    evidence_hash_html = f'<p>SHA-256: <code>{esc(evidence_hash)}</code></p>' if evidence_hash else ""
    evidence_html = (
        f'<details class="relation-evidence"><summary>Consultar evidência textual</summary>'
        f'<blockquote>{esc(evidence)}</blockquote>{evidence_hash_html}</details>'
        if include_evidence and evidence else ""
    )
    record = f'<span class="relation-prefix">Relação registrada:</span> <strong>{source}</strong> <span class="relation-verb">{esc(label)}</span> <strong>{target}</strong>{details}{evidence_html}'
    if not include_evidence:
        return f'<span class="relation-inline">{record}</span>'
    return f'<div class="relation-record" id="{esc(relation.get("_site_id"))}">{record}</div>'


def contextualize_articles(
    body: str, relations: list[dict[str, object]], document_id: str | None = None
) -> str:
    by_article: dict[str, list[dict[str, object]]] = {}
    for relation in relations:
        if document_id and relation.get("_site_device_document_id") != document_id:
            continue
        key = article_key(relation.get("dispositivo"))
        if key:
            by_article.setdefault(key, []).append(relation)
    if not by_article:
        return body
    output: list[str] = []
    for line in body.splitlines():
        match = ARTICLE_LINE.match(line) if line.lstrip().startswith(("**Art.", "Art.")) else None
        key = article_key(match.group(1)) if match else None
        if key in by_article:
            notes = "".join(
                f'<a class="relation-margin-note" href="#{esc(rel.get("_site_id"))}">Ver relação no grafo</a>'
                for rel in by_article[key]
            )
            output.append(line[:match.start(2)] + notes + line[match.start(2):])
        else:
            output.append(line)
    return "\n".join(output)


def status_label(status: str) -> str:
    return {
        "em_vigor": "Em vigor",
        "parcialmente_revogada": "Parcialmente revogada",
        "revogada": "Revogada",
        "transitoria": "Transitória",
        "desconhecida": "Situação desconhecida",
    }.get(status, status.replace("_", " ").title())


def law_page(
    metadata: dict[str, object],
    body: str,
    relations: list[dict[str, object]] | None = None,
    release_version: str = "",
) -> str:
    title = str(metadata.get("titulo") or "Diploma normativo")
    ementa = str(metadata.get("ementa") or "Ementa não disponível na publicação pública.")
    source = next(
        (
            safe_url
            for candidate in metadata.get("fonte_oficial", [])
            if (safe_url := safe_official_url(candidate))
        ),
        "",
    )
    status = str(metadata.get("situacao") or "desconhecida")
    consolidation = str(metadata.get("consolidacao_status") or "desconhecida")
    fidelity = str(metadata.get("fidelity_status") or "não informado")
    document_id = str(metadata.get("id") or "")
    cutoff = str(metadata.get("data_corte") or "não informado")
    relations = relations or []
    article_body = article_anchors(contextualize_articles(body, relations, document_id))
    # The canonical title is retained in the body. The generated page uses a
    # richer header and removes only the first identical H1 for presentation.
    article_body = re.sub(rf"^#\s+{re.escape(title)}\s*\n+", "", article_body, count=1, flags=re.IGNORECASE)
    source_link = f'<a href="{esc(source)}" rel="noreferrer">Fonte oficial</a>' if source else "Fonte oficial indisponível"
    source_btn = f'<a href="{esc(source)}" class="btn-official-source" target="_blank" rel="noopener noreferrer">Fonte oficial ↗</a>' if source else ""
    reader_toolbar = f'''<div class="reader-toolbar" role="toolbar" aria-label="Ferramentas de leitura forense">
  <div class="reader-toolbar-group">
    <button type="button" class="btn-quick-jump" id="btn-quick-jump" aria-label="Buscar texto ou ir para um dispositivo (atalho Ctrl ou Command mais K)">
      Ir para dispositivo <kbd>Ctrl K</kbd>
    </button>
    <button type="button" class="btn-focus-mode" id="btn-focus-mode" aria-pressed="false">
      Modo de leitura
    </button>
  </div>
  <div class="reader-toolbar-group">
    <button type="button" class="btn-font-size" id="btn-font-decrease" aria-label="Diminuir o tamanho do texto">A−</button>
    <button type="button" class="btn-font-size" id="btn-font-increase" aria-label="Aumentar o tamanho do texto">A+</button>
    {source_btn}
  </div>
</div>'''
    relation_cards = ''.join(relation_markup(rel) for rel in relations)
    relation_listing = (
        f'<details class="relation-list"><summary>Exibir {len(relations)} relações registradas</summary>{relation_cards}</details>'
        if len(relations) > 12 else relation_cards
    )
    return f'''---
search:
  exclude: true
---

<div class="law-hero" data-law-id="{esc(document_id)}" data-release="{esc(release_version)}">
<p class="eyebrow law-eyebrow"><span>{esc(metadata.get("tipo"))}</span><span class="law-eyebrow-number">· {esc(metadata.get("numero"))}/{esc(metadata.get("ano"))}</span></p>
<h1>{esc(title)}</h1>
<p class="law-ementa">{esc(ementa)}</p>
<div class="law-status-row">
  <span class="status-chip status-{esc(status)}">{esc(status_label(status))}</span>
  <span class="status-chip status-neutral">Corte {esc(cutoff)}</span>
  <span class="status-chip status-neutral">{esc(consolidation.replace("_", " "))}</span>
</div>
</div>

<div class="law-tools">
<div><strong>Fonte:</strong> {source_link}</div>
<div><strong>ID:</strong> <code>{esc(document_id)}</code> <button class="copy-id" type="button" data-copy-id="{esc(document_id)}">Copiar ID</button></div>
</div>

{reader_toolbar}

<details class="law-technical">
<summary>Proveniência e validação técnica</summary>
<dl class="technical-grid">
  <dt>Fidelidade</dt><dd>{esc(fidelity)}</dd>
  <dt>Hash de origem</dt><dd><code>{esc(metadata.get("sha256_source_raw"))}</code></dd>
  <dt>Hash do corpo</dt><dd><code>{esc(metadata.get("sha256_published_body"))}</code></dd>
  <dt>Unidade de fonte</dt><dd><code>{esc(metadata.get("source_unit_id"))}</code></dd>
</dl>
</details>

{article_body}

<section class="law-relations" aria-labelledby="law-relations-title">
<h2 id="law-relations-title">Relações normativas contextualizadas</h2>
<p>Estas relações são metadados derivados do grafo publicado. Elas não integram o texto da norma; confira a evidência e a fonte antes de interpretá-las.</p>
{relation_listing if relations else '<p>Não há relações publicadas para este diploma no grafo desta versão.</p>'}
</section>

<div class="law-footer-note">
<strong>Nota editorial.</strong> Esta página é uma camada de leitura derivada.
Consulte sempre a fonte oficial e considere a data de corte antes de utilizar o texto.
</div>
'''


def load_metrics(rows: list[dict[str, str]]) -> dict[str, object]:
    release_path = ROOT / "manifests/release.json"
    baseline_path = ROOT / "manifests/baseline.json"
    release = json.loads(release_path.read_text(encoding="utf-8")) if release_path.is_file() else {}
    baseline = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.is_file() else {}
    tests = sum(
        len(re.findall(r"^\s+def test_", path.read_text(encoding="utf-8"), re.MULTILINE))
        for path in sorted((ROOT / "tests").rglob("test_*.py"))
    )
    graph_path = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    relations = len(graph_path.read_text(encoding="utf-8").splitlines()) if graph_path.is_file() else 0
    cutoff = max((str(row.get("cutoff") or "") for row in rows), default=str(release.get("generated_at", "")))
    return {
        "corpus_count": len(rows),
        "p0_count": sum(row.get("priority") == "P0" for row in rows),
        "p0_ready": int((baseline.get("p0") or {}).get("ready", 0)),
        "p0_total": int((baseline.get("p0") or {}).get("total", 0)),
        "official_source_count": sum(bool(row.get("source")) for row in rows),
        "relations": relations,
        "tests": tests,
        "cutoff": cutoff,
        "version": str(release.get("version", "1.1.2")),
        "quality": str(baseline.get("status", "unknown")),
    }


def hero_graph_markup(rows: list[dict[str, str]]) -> str:
    """Render a small, keyboard-navigable sample from the published relation graph."""
    by_id = {row["id"]: row for row in rows}
    graph = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
    if not graph.is_file():
        return '<div class="hero-graph-fallback"><p>Grafo indisponível nesta versão.</p><a href="graph/">Consultar a página do grafo</a></div>'

    candidates: dict[tuple[str, str], dict[str, object]] = {}
    neighbors: dict[str, set[str]] = {}
    for line in graph.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        relation = json.loads(line)
        source = str(relation.get("source_id") or "")
        target = str(relation.get("target_id") or "")
        if source not in by_id or target not in by_id or source == target:
            continue
        neighbors.setdefault(source, set()).add(target)
        neighbors.setdefault(target, set()).add(source)
        pair = tuple(sorted((source, target)))
        current = candidates.get(pair)
        # Keep one actual directed, typed record per pair for a readable overview.
        if current is None or (relation.get("type") in DEVICE_TARGET_TYPES and current.get("type") not in DEVICE_TARGET_TYPES):
            candidates[pair] = relation

    if not neighbors:
        return '<div class="hero-graph-fallback"><p>O grafo desta versão não tem relações entre diplomas do corpus.</p><a href="graph/">Consultar a página do grafo</a></div>'

    center = max(neighbors, key=lambda identifier: (len(neighbors[identifier]), identifier))
    selected = [center]
    ranked_neighbors = sorted(
        neighbors[center],
        key=lambda identifier: (-len(neighbors[identifier]), by_id[identifier]["title"].casefold(), identifier),
    )[:4]
    selected.extend(ranked_neighbors)
    coordinates = [(260, 150), (90, 55), (430, 55), (90, 245), (430, 245)]
    positions = {identifier: coordinates[index] for index, identifier in enumerate(selected)}
    radii = {identifier: (12 if index == 0 else 8) for index, identifier in enumerate(selected)}

    edge_markup: list[str] = []
    relation_links: list[str] = []

    def law_href(identifier: str) -> str:
        return "generated/laws/" + by_id[identifier]["path"].removeprefix("laws/").removesuffix(".md") + "/"

    for pair, relation in sorted(candidates.items()):
        source = str(relation.get("source_id") or pair[0])
        target = str(relation.get("target_id") or pair[1])
        if source not in positions or target not in positions:
            continue
        sx, sy = positions[source]
        tx, ty = positions[target]
        length = math.hypot(tx - sx, ty - sy) or 1
        ux, uy = (tx - sx) / length, (ty - sy) / length
        x1 = round(sx + ux * (radii[source] + 1), 2)
        y1 = round(sy + uy * (radii[source] + 1), 2)
        x2 = round(tx - ux * (radii[target] + 7), 2)
        y2 = round(ty - uy * (radii[target] + 7), 2)
        raw_type = str(relation.get("type") or "relação registrada")
        edge_type = esc(RELATION_LABELS.get(raw_type, raw_type.replace("_", " ")))
        edge_markup.append(
            f'<line class="hero-graph-edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'data-source-id="{esc(source)}" data-target-id="{esc(target)}" data-relation="{esc(raw_type)}" '
            f'role="img" aria-label="{esc(by_id[source]["title"])} — {edge_type} — {esc(by_id[target]["title"])}" '
            f'marker-end="url(#hero-graph-arrow)"><title>{esc(by_id[source]["title"])} — {edge_type} — {esc(by_id[target]["title"])}</title></line>'
        )
        relation_links.append(
            f'<li data-source-id="{esc(source)}" data-target-id="{esc(target)}" data-relation="{esc(raw_type)}">'
            f'<a href="{esc(law_href(source))}">{esc(POPULAR_TITLES.get(source, by_id[source]["title"]))}</a> '
            f'<span>{edge_type} →</span> '
            f'<a href="{esc(law_href(target))}">{esc(POPULAR_TITLES.get(target, by_id[target]["title"]))}</a></li>'
        )

    node_markup: list[str] = []
    for index, identifier in enumerate(selected):
        row = by_id[identifier]
        x, y = positions[identifier]
        href = law_href(identifier)
        title = POPULAR_TITLES.get(identifier, row["title"])
        if index == 0:
            short = textwrap.shorten(POPULAR_TITLES.get(identifier, title), width=18, placeholder="…")
        else:
            kind = row.get("type", "").casefold()
            prefix = {
                "ato_constitucional": "EC",
                "constituicao": "CF",
                "decreto": "Dec.",
                "decreto_lei": "DL",
                "lei_complementar": "LC",
                "lei_ordinaria": "Lei",
            }.get(kind, "Norma")
            number = row.get("number", "").strip()
            year = row.get("year", "").strip()
            short = f"{prefix} {number}/{year}" if number and year else textwrap.shorten(title, width=18, placeholder="…")
        radius = radii[identifier]
        label_x = x + (radius + 5 if x < 260 else -(radius + 5)) if x != 260 else x
        label_anchor = "start" if x < 260 else ("end" if x > 260 else "middle")
        label_y = y + radius + 16
        node_markup.append(
            f'<a class="hero-graph-node{" is-central" if index == 0 else ""}" href="{esc(href)}" aria-label="Abrir {esc(title)}">'
            f'<title>Abrir {esc(title)} · {esc(identifier)}</title><circle cx="{x}" cy="{y}" r="{radius}" />'
            f'<text x="{label_x}" y="{label_y}" text-anchor="{label_anchor}">{esc(short)}</text></a>'
        )

    return f'''<div class="hero-graph-heading"><span>Grafo normativo</span><span>{len(selected)} diplomas · {len(relation_links)} relações</span></div>
    <figure class="hero-graph-figure">
    <svg class="normative-constellation" viewBox="0 0 520 300" role="group" aria-labelledby="hero-graph-title hero-graph-description">
      <title id="hero-graph-title">Recorte navegável do grafo normativo</title>
      <desc id="hero-graph-description">{len(selected)} diplomas conectados por relações tipadas presentes no grafo publicado. Selecione um nó para abrir o respectivo texto.</desc>
      <defs><marker id="hero-graph-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" /></marker></defs>
      <g class="hero-graph-edges">{"".join(edge_markup)}</g>
      <g class="hero-graph-nodes">{"".join(node_markup)}</g>
    </svg>
    <figcaption class="hero-visual-caption"><span>Selecione um diploma para abrir o texto.</span><a href="graph/">Abrir explorador completo</a></figcaption>
    <details class="hero-graph-relation-list"><summary>Ver {len(relation_links)} relações e seus sentidos</summary><ul>{"".join(relation_links)}</ul></details>
  </figure>'''


def home_page(rows: list[dict[str, str]], metrics: dict[str, object]) -> str:
    by_id = {row["id"]: row for row in rows}
    quick_access: list[str] = []
    for identifier in FEATURED_LAW_IDS[:6]:
        row = by_id.get(identifier)
        if not row:
            continue
        title = POPULAR_TITLES.get(identifier, row["title"])
        relative = row["path"].removeprefix("laws/").removesuffix(".md")
        descriptor = f'{row["type"]} · {row["number"]}/{row["year"]}'
        href = "generated/laws/" + relative + "/"
        quick_access.append(
            f'<li><a href="{esc(href)}"><strong>{esc(title)}</strong>'
            f'<span>{esc(descriptor)}</span></a></li>'
        )

    return f'''<section class="vmd-hero" aria-labelledby="home-title">
  <div class="hero-copy">
    <p class="eyebrow"><span>Índice de legislação federal</span><span class="eyebrow-release">Release {esc(metrics["version"])}</span></p>
    <h1 id="home-title">Encontre a lei.<br><em>Leia com clareza.</em></h1>
    <p class="hero-lede">Leis federais em Markdown, com acesso direto ao texto e informações de fonte e corte.</p>
    <div class="hero-actions">
      <a class="md-button md-button--primary" href="#home-search">Buscar uma lei</a>
      <a class="md-button" href="generated/catalog/">Abrir catálogo</a>
    </div>
    <p class="hero-disclaimer">Projeto independente. A publicação oficial é a referência jurídica primária.</p>
  </div>
  <div class="hero-visual">{hero_graph_markup(rows)}</div>
</section>

<section id="home-search" class="home-search-section" aria-labelledby="home-search-title">
  <div class="home-search-heading">
    <p class="eyebrow">Busca no corpus</p>
    <h2 id="home-search-title">Qual diploma você procura?</h2>
  </div>
  <form id="vmd-global-search" class="home-search-form" action="generated/catalog/" method="get" role="search">
    <label class="vmd-sr-only" for="vmd-global-search-input">Buscar por nome, número, identificador ou artigo</label>
    <input id="vmd-global-search-input" name="q" type="search" autocomplete="off" spellcheck="false"
      placeholder="Ex.: Constituição, Lei 10.406, Art. 186"
      aria-controls="vmd-global-search-results" aria-expanded="false"
      data-index-url="generated/search-index.json" />
    <button type="submit" class="md-button md-button--primary">Buscar</button>
  </form>
  <div id="vmd-global-search-results" class="home-search-results" hidden>
    <p id="vmd-global-search-status" class="home-search-status" role="status" aria-live="polite"></p>
    <div id="vmd-global-search-list" class="home-search-list"></div>
    <a id="vmd-global-search-all" class="home-search-all" href="generated/catalog/" hidden>Ver catálogo completo</a>
  </div>
  <p class="home-search-scope">Busca títulos, números e rótulos de artigos. No leitor, use a busca para localizar dispositivos no texto aberto.</p>
</section>

<section class="home-quick-access" aria-labelledby="quick-access-title">
  <div class="home-section-heading">
    <div><p class="eyebrow">Acesso direto</p><h2 id="quick-access-title">Leis de consulta frequente</h2></div>
    <a href="generated/catalog/">Ver todos os {metrics["corpus_count"]} diplomas</a>
  </div>
  <ul class="home-law-list">{"".join(quick_access)}</ul>
</section>

<section class="home-data-strip" aria-label="Identificação desta coleção">
  <p><strong>{metrics["corpus_count"]}</strong><span>diplomas</span></p>
  <p><strong>{metrics["relations"]:,}</strong><span>relações publicadas</span></p>
  <p><strong>{esc(metrics["cutoff"])}</strong><span>corte do corpus</span></p>
</section>

<footer class="home-trust-note">
  <p>O corpus organiza textos de fontes públicas e não é publicação oficial, parecer ou aconselhamento jurídico.</p>
  <nav aria-label="Informações sobre o projeto"><a href="sources/">Fontes</a><a href="methodology/">Metodologia</a><a href="quality/">Qualidade e limites</a><a href="legal-limits/">Escopo jurídico</a></nav>
</footer>
'''


def corpus_markdown_index(rows: list[dict[str, str]], cutoff: str) -> str:
    """Create a GitHub-friendly directory guide linking every canonical law file."""
    type_labels = {
        "ato_constitucional": "Ato constitucional", "constituicao": "Constituição",
        "decreto": "Decreto", "decreto_lei": "Decreto-Lei",
        "lei_complementar": "Lei complementar", "lei_ordinaria": "Lei ordinária",
    }
    grouped: dict[str, dict[str, list[dict[str, str]]]] = {}
    for row in rows:
        grouped.setdefault(row["type"] or "outro", {}).setdefault(
            row["year"] or "Sem ano", []
        ).append(row)

    lines = [
        "# Índice da legislação federal", "",
        "> Índice navegável dos arquivos Markdown canônicos. Cada link abre o texto da lei no GitHub.", "",
        (
            f"**{len(rows)} {'diploma' if len(rows) == 1 else 'diplomas'}** · Corte dos dados: "
            f"**{cutoff or 'não informado'}** · [Abrir leitor no navegador](https://lucmolero.github.io/vademecum-md/) · "
            "[Pesquisar no catálogo web](https://lucmolero.github.io/vademecum-md/generated/catalog/)"
        ), "",
        "## Acesso rápido", "",
    ]
    by_id = {row["id"]: row for row in rows}
    for identifier in FEATURED_LAW_IDS:
        row = by_id.get(identifier)
        if row:
            title = POPULAR_TITLES.get(identifier, row["title"])
            canonical_path = row["path"].removeprefix("laws/")
            lines.append(f'- [{title}](../bases/curated/legislacao/{canonical_path})')

    lines.extend([
        "", "## Navegue por tipo e ano", "",
        "Expanda o tipo de ato e procure o ano. Para localizar rapidamente um nome ou número nesta página, use a busca do navegador (Ctrl+F ou ⌘F).", "",
    ])
    for document_type in sorted(grouped, key=lambda item: type_labels.get(item, item).casefold()):
        type_rows = grouped[document_type]
        label = type_labels.get(document_type, document_type.replace("_", " ").title())
        count = sum(len(items) for items in type_rows.values())
        document_word = "diploma" if count == 1 else "diplomas"
        lines.extend(["<details>", f"<summary><strong>{label}</strong> · {count} {document_word}</summary>", ""])
        for year in sorted(type_rows, key=lambda value: (value == "Sem ano", value), reverse=True):
            lines.extend([f"**{year}**", ""])
            for row in sorted(type_rows[year], key=lambda item: (item["number"].zfill(12), item["title"].casefold())):
                identifier = row["id"]
                title = POPULAR_TITLES.get(identifier, row["title"])
                number = row["number"].strip()
                year_value = row["year"].strip()
                if number and number.casefold() not in {"none", "null"} and year_value and year_value.casefold() not in {"none", "null"}:
                    descriptor = f"{label} nº {number}/{year_value}"
                    if title.casefold() != descriptor.casefold():
                        title = f"{title} ({descriptor})"
                relative = f"../bases/curated/legislacao/{row['path'].removeprefix('laws/')}"
                lines.append(f'- [{title}]({relative})')
            lines.append("")
        lines.extend(["</details>", ""])
    lines.extend([
        "---", "", "## Como os arquivos estão organizados", "",
        "O caminho segue **tipo do ato / ano / arquivo**. O nome do arquivo contém tipo, número e ano; o front matter de cada Markdown preserva ID estável, fonte, corte, hash e metadados. Este índice serve à navegação. Para pesquisa por assunto e leitura confortável, use o leitor web; para citação e auditoria, confira também a fonte oficial indicada no documento.", "",
        "[Voltar ao README do projeto](../README.md) · [Ver metodologia e limites](https://lucmolero.github.io/vademecum-md/methodology/)", "",
    ])
    return "\n".join(lines)


def build() -> dict[str, int]:
    laws = GENERATED / "laws"
    if GENERATED.exists():
        for child in GENERATED.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    laws.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    search_records: list[dict[str, str]] = []
    for source in sorted((CURATED / "federal").rglob("*.md")):
        metadata, body = parse_frontmatter(source.read_text(encoding="utf-8"), strict=True)
        relative = source.relative_to(CURATED).as_posix()
        target = laws / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        rows.append({
            "id": metadata_text(metadata.get("id")),
            "title": metadata_text(metadata.get("titulo"), source.stem),
            "type": metadata_text(metadata.get("tipo")),
            "number": metadata_text(metadata.get("numero")),
            "year": metadata_text(metadata.get("ano")),
            "domain": metadata_text(metadata.get("dominio")),
            "status": metadata_text(metadata.get("situacao"), "desconhecida"),
            "priority": metadata_text(metadata.get("prioridade"), "P2"),
            "source": next(iter(metadata.get("fonte_oficial") or []), ""),
            "cutoff": str(metadata.get("data_corte", "")),
            "path": f"laws/{relative}",
        })
        search_records.extend(article_search_records(metadata, body, relative))
    graph_relations = relation_index(rows)
    metrics = load_metrics(rows)
    # Re-render after the full corpus index is known so both endpoints use their
    # canonical titles and every relation is represented with its original direction.
    for source in sorted((CURATED / "federal").rglob("*.md")):
        metadata, body = parse_frontmatter(source.read_text(encoding="utf-8"), strict=True)
        relative = source.relative_to(CURATED).as_posix()
        target = laws / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            law_page(
                metadata,
                body,
                graph_relations.get(str(metadata.get("id") or ""), []),
                release_version=str(metrics["version"]),
            ),
            encoding="utf-8", newline="\n",
        )
    by_domain: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_domain.setdefault(domain_key(row["domain"]), []).append(row)
    catalog = [
        "# Cat\u00e1logo da legisla\u00e7\u00e3o", "",
        "> Corpus federal curado. Cada entrada aponta para a p\u00e1gina derivada e para o Markdown can\u00f4nico.", "",
        f"Documentos: **{len(rows)}** \u00b7 Data de corte: **{max((row['cutoff'] for row in rows), default='n\u00e3o informada')}**", "",
        "## Grandes C\u00f3digos da Rep\u00fablica", "",
        "| Diploma | Tipo e n\u00famero | Ano |", "| --- | --- | --- |",
    ]
    by_id = {row["id"]: row for row in rows}
    for identifier in FEATURED_LAW_IDS:
        row = by_id.get(identifier)
        if not row:
            continue
        title = POPULAR_TITLES.get(identifier, row["title"])
        kind = DOCUMENT_TYPE_LABELS.get(row["type"], row["type"].replace("_", " ").title())
        number = f"{kind} n\u00ba {row['number']}" if row["number"] else kind
        catalog.append(f"| [{title}]({row['path']}) | `{number}` | `{row['year']}` |")
    catalog.extend(["", "---", ""])
    for domain in sorted(by_domain):
        catalog.extend([
            f"## {esc(domain_label(domain))}", "",
            "| Diploma | Tipo e n\u00famero | Ano |", "| --- | --- | --- |",
        ])
        for row in by_domain[domain]:
            display_title = POPULAR_TITLES.get(row["id"], row["title"])
            kind = DOCUMENT_TYPE_LABELS.get(row["type"], row["type"].replace("_", " ").title())
            number = f"{kind} n\u00ba {row['number']}" if row["number"] else kind
            catalog.append(f"| [{display_title}]({row['path']}) | `{number}` | `{row['year']}` |")
        catalog.append("")
    (GENERATED / "catalog.md").write_text("\n".join(catalog) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "docs/INDICE_LEGISLACAO.md").write_text(
        corpus_markdown_index(rows, str(metrics["cutoff"])), encoding="utf-8", newline="\n"
    )
    compact_search_documents: list[dict[str, object]] = []
    compact_by_id: dict[str, dict[str, object]] = {}
    for record in search_records:
        if record["kind"] == "document":
            compact = {
                key: record[key]
                for key in (
                    "id", "title", "popular_title", "type", "number", "year", "domain", "status", "href"
                )
            }
            compact["articles"] = []
            compact_search_documents.append(compact)
            compact_by_id[record["id"]] = compact
        else:
            document = compact_by_id[record["id"]]
            articles = document["articles"]
            assert isinstance(articles, list)
            articles.append([record["article"], record["href"].rsplit("#", 1)[-1]])

    search_index = {
        "schema": "vademecum-search/v1",
        "release": str(metrics["version"]),
        "cutoff": str(metrics["cutoff"]),
        "scope": ["diploma", "identificador", "tipo", "número", "ano", "domínio", "rótulo do artigo"],
        "documents": compact_search_documents,
    }
    (GENERATED / "search-index.json").write_text(
        json.dumps(search_index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (laws / "index.md").write_text("# Legislação\n\nNavegue pelo catálogo para abrir um diploma.\n", encoding="utf-8", newline="\n")
    home = (
        "---\n"
        "social:\n"
        "  cards_layout_options:\n"
        "    title: \"Legislação federal em leitura e dados\"\n"
        "    description: \"Corpus brasileiro estruturado, com proveniência e corte temporal explícitos.\"\n"
        "---\n\n"
        "<!-- Generated by tools/site/build_site.py; edit the generator, not this file. -->\n\n"
        + home_page(rows, metrics)
    )
    (SITE / "index.md").write_text(home, encoding="utf-8", newline="\n")
    graph_payload = graph_index_data(rows, metrics)
    (GENERATED / "graph-index.json").write_text(
        json.dumps(graph_payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    preview_path = SITE / "assets/normative-graph-preview.svg"
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.write_text(graph_preview_svg(graph_payload), encoding="utf-8", newline="\n")
    update_readme_graph(graph_payload)
    (GENERATED / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"documents": len(rows), "domains": len(by_domain), "relations": int(metrics["relations"])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validar que a camada de site pode ser gerada")
    args = parser.parse_args()
    result = build()
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
