"""Generate the editorial site layer from the canonical Markdown corpus.

The site is deliberately derived: it may add navigation, metadata panels and
article anchors, but it never rewrites the canonical corpus under bases/.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter
from pathlib import Path

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


def law_page(metadata: dict[str, object], body: str, relations: list[dict[str, object]] | None = None, release_version: str = "") -> str:
    title = str(metadata.get("titulo") or "Diploma normativo")
    ementa = str(metadata.get("ementa") or "Ementa não disponível na publicação pública.")
    source = next(iter(metadata.get("fonte_oficial") or []), "")
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
    source_btn = f'<a href="{esc(source)}" class="btn-official-source" target="_blank" rel="noreferrer" title="Abrir a fonte oficial indicada no documento">Fonte oficial ↗</a>' if source else ""
    reader_toolbar = f'''<div class="reader-toolbar" role="toolbar" aria-label="Ferramentas de leitura forense">
  <div class="reader-toolbar-group">
    <button type="button" class="btn-quick-jump" id="btn-quick-jump" title="Buscar e saltar para artigo (Atalho: Ctrl + K)">
      <svg class="reader-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="10.8" cy="10.8" r="6.2"/><path d="m15.4 15.4 4.2 4.2"/></svg> Ir para artigo <kbd>Ctrl K</kbd>
    </button>
    <button type="button" class="btn-focus-mode" id="btn-focus-mode" title="Alternar modo de leitura sem distrações">
      <svg class="reader-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 5.5c3.2-.9 6.1-.5 8 1.2v12c-1.9-1.7-4.8-2.1-8-1.2z"/><path d="M20 5.5c-3.2-.9-6.1-.5-8 1.2v12c1.9-1.7 4.8-2.1 8-1.2z"/></svg> Modo leitura
    </button>
  </div>
  <div class="reader-toolbar-group">
    <button type="button" class="btn-font-size" id="btn-font-decrease" title="Diminuir tamanho da fonte">A-</button>
    <button type="button" class="btn-font-size" id="btn-font-increase" title="Aumentar tamanho da fonte">A+</button>
    {source_btn}
  </div>
</div>'''
    relation_cards = ''.join(relation_markup(rel) for rel in relations)
    relation_listing = (
        f'<details class="relation-list"><summary>Exibir {len(relations)} relações registradas</summary>{relation_cards}</details>'
        if len(relations) > 12 else relation_cards
    )
    return f'''<div class="law-hero" data-law-id="{esc(document_id)}" data-release-version="{esc(release_version)}">
<p class="eyebrow">{esc(metadata.get("tipo"))} · {esc(metadata.get("numero"))}/{esc(metadata.get("ano"))}</p>
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


def home_page(rows: list[dict[str, str]], metrics: dict[str, object]) -> str:
    domains = Counter(domain_key(row["domain"] or "especializado") for row in rows)
    labels = {domain_key(row["domain"] or "especializado"): domain_label(row["domain"] or "especializado") for row in rows}
    domain_cards = "\n".join(
        f'<a class="domain-card reveal" href="generated/catalog/#{slugify(labels[domain])}">'
        f'<span>{esc(labels[domain])}</span><strong>{count:03d}</strong></a>'
        for domain, count in sorted(domains.items())
    )
    return f'''<div class="vmd-hero">
  <div class="hero-copy reveal">
    <img class="hero-logo" src="assets/logo-lockup.svg" alt="VadeMecum MD" />
    <p class="eyebrow">Corpus federal curado <span class="eyebrow-dot"></span> release {esc(metrics["version"])}</p>
    <h1>O direito federal,<br><em>em estado legível.</em></h1>
    <p class="hero-lede">Legislação brasileira estruturada para leitura humana, validação auditável e uso por máquinas.</p>
    <div class="hero-actions">
      <a class="md-button md-button--primary" href="generated/catalog/">Explorar legislação <span aria-hidden="true">↗</span></a>
      <a class="md-button" href="methodology/">Ver metodologia</a>
    </div>
    <p class="hero-disclaimer">Corpus autoral e derivado de fontes públicas oficiais. Não é publicação oficial nem aconselhamento jurídico.</p>
  </div>
  <div class="hero-visual reveal" aria-hidden="true">
    <svg class="normative-constellation" viewBox="0 0 520 420" role="presentation">
      <defs>
        <linearGradient id="vmd-line" x1="0" x2="1">
          <stop offset="0" stop-color="#B48A3C" stop-opacity=".12" />
          <stop offset=".5" stop-color="#B48A3C" stop-opacity=".9" />
          <stop offset="1" stop-color="#2D7659" stop-opacity=".15" />
        </linearGradient>
        <filter id="vmd-glow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      </defs>
      <g class="constellation-lines" stroke="url(#vmd-line)" fill="none">
        <path d="M60 250C118 82 248 68 330 180S448 326 470 100" />
        <path d="M42 328C154 310 194 170 292 118S395 92 478 286" />
        <path d="M82 96C170 152 190 290 318 300S425 250 474 210" />
      </g>
      <g class="constellation-nodes" filter="url(#vmd-glow)">
        <circle cx="60" cy="250" r="7"/><circle cx="118" cy="126" r="4"/><circle cx="190" cy="284" r="5"/>
        <circle cx="248" cy="72" r="6"/><circle cx="330" cy="180" r="10"/><circle cx="392" cy="292" r="5"/>
        <circle cx="470" cy="100" r="7"/><circle cx="478" cy="286" r="4"/><circle cx="82" cy="96" r="5"/>
      </g>
      <g class="constellation-labels" fill="#FBF8F0" font-family="monospace" font-size="11">
        <text x="315" y="162">ART. 01</text><text x="445" y="84">FONTE</text><text x="42" y="348">HASH</text>
      </g>
    </svg>
    <div class="hero-visual-caption"><span class="signal"></span> estrutura normativa em movimento</div>
  </div>
</div>

<div class="metric-grid">
  <a class="metric-card reveal" href="generated/catalog/"><span>Diplomas curados</span><strong>{metrics["corpus_count"]}</strong><small>corpus federal</small></a>
  <a class="metric-card reveal" href="quality/"><span>Núcleo P0</span><strong>{metrics["p0_ready"]}<sup>/{metrics["p0_total"]}</sup></strong><small>consolidado</small></a>
  <a class="metric-card reveal" href="graph/"><span>Relações</span><strong>{metrics["relations"]:,}</strong><small>registros publicados, inclui inversas</small></a>
  <a class="metric-card reveal" href="quality/"><span>Data de corte</span><strong>{esc(metrics["cutoff"])}</strong><small>snapshot público</small></a>
</div>

<section class="featured-codes-section reveal">
  <div class="section-heading">
    <div>
      <p class="eyebrow">Destaques do ordenamento</p>
      <h2>Grandes Códigos da República</h2>
    </div>
    <a href="generated/catalog/">Explorar todos os 375 diplomas ↗</a>
  </div>
  <p class="snapshot-note">As situações exibidas correspondem ao corte do corpus ({esc(metrics["cutoff"])}). Confirme a fonte oficial para verificar a situação aplicável na data da consulta.</p>
  <div class="featured-codes-grid">
    <a class="code-card" href="generated/laws/federal/constituicao/1988/constituicao-da-republica-federativa-do-brasil-1988/">
      <div class="code-card-badge">CF/88</div>
      <h3>Constituição Federal</h3>
      <p>Norma fundamental da República promulgada em 5 de outubro de 1988.</p>
      <span class="code-card-status status-em_vigor">Em vigor</span>
    </a>
    <a class="code-card" href="generated/laws/federal/leis-ordinarias/2002/lei-ordinaria-10406-2002/">
      <div class="code-card-badge">Lei 10.406</div>
      <h3>Código Civil</h3>
      <p>Direitos e deveres das pessoas, bens, obrigações e contratos civis.</p>
      <span class="code-card-status status-em_vigor">Em vigor</span>
    </a>
    <a class="code-card" href="generated/laws/federal/leis-ordinarias/2015/lei-ordinaria-13105-2015/">
      <div class="code-card-badge">Lei 13.105</div>
      <h3>Código de Processo Civil</h3>
      <p>Normas fundamentais e ritos de tutela jurisdicional perante os tribunais.</p>
      <span class="code-card-status status-em_vigor">Em vigor</span>
    </a>
    <a class="code-card" href="generated/laws/federal/decretos-lei/1940/decreto-lei-2848-1940/">
      <div class="code-card-badge">DL 2.848</div>
      <h3>Código Penal</h3>
      <p>Parte Geral e tipificação de crimes e contravenções no âmbito repressivo.</p>
      <span class="code-card-status status-em_vigor">Em vigor</span>
    </a>
    <a class="code-card" href="generated/laws/federal/decretos-lei/1941/decreto-lei-3689-1941/">
      <div class="code-card-badge">DL 3.689</div>
      <h3>Código de Processo Penal</h3>
      <p>Inquérito policial, instrução criminal, garantias processuais e provas.</p>
      <span class="code-card-status status-em_vigor">Em vigor</span>
    </a>
    <a class="code-card" href="generated/laws/federal/decretos-lei/1943/decreto-lei-5452-1943/">
      <div class="code-card-badge">DL 5.452</div>
      <h3>Consolidação das Leis do Trabalho</h3>
      <p>Relações individuais e coletivas de trabalho e direito processual trabalhista.</p>
      <span class="code-card-status status-em_vigor">Em vigor</span>
    </a>
  </div>
</section>

<section class="audiences-section reveal">
  <div class="section-heading"><div><p class="eyebrow">Leitura humana e consulta por agentes</p><h2>Conhecimento normativo com evidência.</h2></div><a href="audiences/">Como usar</a></div>
  <div class="audience-grid audience-primary-grid">
    <a class="audience-card audience-law" href="audiences/#para-advogados-e-pesquisadores-juridicos"><span class="audience-kicker">01 · leitura humana</span><h3>Advogados e pesquisadores</h3><p>Texto integral, situação, fonte oficial e citação por dispositivo.</p><span class="audience-link">Ler com contexto →</span></a>
    <a class="audience-card audience-agent" href="audiences/#para-agentes-de-ia"><span class="audience-kicker">02 · agentes de IA</span><h3>Conhecimento para agentes</h3><p>Corpus rastreável para localizar normas, conferir o corte e produzir referências com proveniência.</p><span class="audience-link">Ler instruções da skill →</span></a>
  </div>
  <p class="integration-audience"><strong>Integração:</strong> dados estruturados, IDs estáveis, hashes e manifestos para desenvolvedores conectarem o corpus a ferramentas e pipelines.</p>
</section>

<section class="editorial-section reveal">
  <p class="eyebrow">A ponte</p>
  <h2>Texto jurídico com estrutura de sistema.</h2>
  <p class="section-lede">O VadeMecum MD trata o diploma como texto editorial e como unidade computável, sem confundir as duas camadas.</p>
  <div class="split-principles">
    <div><span class="principle-index">01</span><h3>Leitura jurídica</h3><p>Texto integral, hierarquia, ementa, vigência, fonte e data de corte em uma experiência de leitura confortável.</p></div>
    <div><span class="principle-index">02</span><h3>Consumo computável</h3><p>IDs estáveis, hashes, manifests, relações normativas e artefatos derivados para ferramentas e agentes.</p></div>
  </div>
</section>

<section class="pipeline-section reveal">
  <div><p class="eyebrow">Método</p><h2>Do documento à evidência.</h2></div>
  <div class="pipeline-list">
    <a href="sources/"><span>01</span><strong>Fonte oficial</strong><small>aquisição pública allowlisted</small></a>
    <a href="contract/"><span>02</span><strong>Normalização</strong><small>transformação determinística</small></a>
    <a href="legal-audit/"><span>03</span><strong>Auditoria</strong><small>fidelidade e anomalias</small></a>
    <a href="graph/"><span>04</span><strong>Relações</strong><small>histórico e grafo normativo</small></a>
    <a href="quality/"><span>05</span><strong>Release</strong><small>gates e pacote reproduzível</small></a>
  </div>
</section>

<section class="domains-section reveal">
  <div class="section-heading"><div><p class="eyebrow">Explorar</p><h2>Uma entrada para cada domínio.</h2></div><a href="generated/catalog/">Ver catálogo completo ↗</a></div>
  <div class="domain-grid">{domain_cards}</div>
</section>

<section class="trust-section reveal">
  <div class="trust-mark">VMD<span>·</span>01</div>
  <div><p class="eyebrow">Transparência por design</p><h2>Auditável não significa oficial.</h2><p>O projeto documenta fontes, transformações, decisões e limitações. A fonte oficial continua sendo a autoridade textual. O site é uma camada de leitura regenerável.</p><a class="text-link" href="legal-limits/">Conhecer os limites jurídicos ↗</a></div>
</section>

<div class="home-footer-note"><strong>Snapshot {esc(metrics["cutoff"])}</strong><span>·</span><span>{esc(metrics["tests"])} testes automatizados</span><span>·</span><a href="https://github.com/lucmolero/vademecum-md">código aberto no GitHub ↗</a></div>
'''


def build() -> dict[str, int]:
    release_path = ROOT / "manifests/release.json"
    release_data = json.loads(release_path.read_text(encoding="utf-8")) if release_path.is_file() else {}
    release_version = str(release_data.get("version") or "")
    laws = GENERATED / "laws"
    if GENERATED.exists():
        for child in GENERATED.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    laws.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for source in sorted((CURATED / "federal").rglob("*.md")):
        metadata, body = parse_frontmatter(source.read_text(encoding="utf-8"), strict=True)
        relative = source.relative_to(CURATED).as_posix()
        target = laws / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        rows.append({
            "id": str(metadata.get("id", "")),
            "title": str(metadata.get("titulo", source.stem)),
            "domain": str(metadata.get("dominio", "")),
            "status": str(metadata.get("situacao", "desconhecida")),
            "priority": str(metadata.get("prioridade", "P2")),
            "source": next(iter(metadata.get("fonte_oficial") or []), ""),
            "cutoff": str(metadata.get("data_corte", "")),
            "path": f"laws/{relative}",
        })
    graph_relations = relation_index(rows)
    # Re-render after the full corpus index is known so both endpoints use their
    # canonical titles and every relation is represented with its original direction.
    for source in sorted((CURATED / "federal").rglob("*.md")):
        metadata, body = parse_frontmatter(source.read_text(encoding="utf-8"), strict=True)
        relative = source.relative_to(CURATED).as_posix()
        target = laws / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            law_page(metadata, body, graph_relations.get(str(metadata.get("id") or ""), []), release_version),
            encoding="utf-8", newline="\n",
        )
    by_domain: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_domain.setdefault(domain_key(row["domain"]), []).append(row)
    catalog = [
        "# Catálogo da legislação",
        "",
        "> Corpus federal curado. Cada entrada aponta para uma página de leitura derivada do Markdown canônico.",
        "",
        f"Documentos: **{len(rows)}** · Data de corte: **{max((row['cutoff'] for row in rows), default='não informada')}**",
        "",
        "## Grandes Códigos da República",
        "",
        "| Diploma | Situação registrada no corte do documento | Prioridade |",
        "| --- | --- | --- |",
        "| [Constituição da República Federativa do Brasil](laws/federal/constituicao/1988/constituicao-da-republica-federativa-do-brasil-1988.md) | `Em vigor` | `P0` |",
        "| [Código Civil (Lei nº 10.406/2002)](laws/federal/leis-ordinarias/2002/lei-ordinaria-10406-2002.md) | `Em vigor` | `P0` |",
        "| [Código de Processo Civil (Lei nº 13.105/2015)](laws/federal/leis-ordinarias/2015/lei-ordinaria-13105-2015.md) | `Em vigor` | `P0` |",
        "| [Código Penal (Decreto-Lei nº 2.848/1940)](laws/federal/decretos-lei/1940/decreto-lei-2848-1940.md) | `Em vigor` | `P0` |",
        "| [Código de Processo Penal (Decreto-Lei nº 3.689/1941)](laws/federal/decretos-lei/1941/decreto-lei-3689-1941.md) | `Em vigor` | `P0` |",
        "| [Consolidação das Leis do Trabalho (Decreto-Lei nº 5.452/1943)](laws/federal/decretos-lei/1943/decreto-lei-5452-1943.md) | `Em vigor` | `P0` |",
        "| [Código de Defesa do Consumidor (Lei nº 8.078/1990)](laws/federal/leis-ordinarias/1990/lei-ordinaria-8078-1990.md) | `Em vigor` | `P0` |",
        "| [Nova Lei de Licitações e Contratos (Lei nº 14.133/2021)](laws/federal/leis-ordinarias/2021/lei-ordinaria-14133-2021.md) | `Em vigor` | `P0` |",
        "| [Estatuto da Advocacia e da OAB (Lei nº 8.906/1994)](laws/federal/leis-ordinarias/1994/lei-ordinaria-8906-1994.md) | `Em vigor` | `P0` |",
        "| [Código Tributário Nacional (Lei nº 5.172/1966)](laws/federal/leis-ordinarias/1966/lei-ordinaria-5172-1966.md) | `Em vigor` | `P0` |",
        "",
        "---",
        "",
    ]
    for domain in sorted(by_domain):
        slug = slugify(domain)
        catalog.extend([f'<div id="{esc(slug)}"></div>', f"## {esc(domain_label(domain))}", "", "| Diploma | Situação registrada no corte do documento | Prioridade |", "| --- | --- | --- |"])
        for row in by_domain[domain]:
            display_title = POPULAR_TITLES.get(row["id"], row["title"])
            catalog.append(f"| [{display_title}]({row['path']}) | `{status_label(row['status'])}` | `{row['priority']}` |")
        catalog.append("")
    (GENERATED / "catalog.md").write_text("\n".join(catalog) + "\n", encoding="utf-8", newline="\n")
    (laws / "index.md").write_text("# Legislação\n\nNavegue pelo catálogo para abrir um diploma.\n", encoding="utf-8", newline="\n")
    metrics = load_metrics(rows)
    home = "<!-- Generated by tools/site/build_site.py; edit the generator, not this file. -->\n\n" + home_page(rows, metrics)
    (SITE / "index.md").write_text(home, encoding="utf-8", newline="\n")
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
