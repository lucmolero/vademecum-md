"""Generate the editorial site layer from the canonical Markdown corpus.

The site is deliberately derived: it may add navigation, metadata panels and
article anchors, but it never rewrites the canonical corpus under bases/.
"""

from __future__ import annotations

import argparse
import csv
import html
from html.parser import HTMLParser
import json
import markdown
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
    "br-federal-lei_ordinaria-15190-2025": "Lei Geral do Licenciamento Ambiental (Lei nº 15.190/2025)",
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


DOCUMENT_TYPE_LABELS = {
    "ato_constitucional": "Ato constitucional",
    "constituicao": "Constituição",
    "decreto_lei": "Decreto-lei",
    "decreto": "Decreto",
    "lei_complementar": "Lei complementar",
    "lei_ordinaria": "Lei ordinária",
}


def document_type_label(value: object) -> str:
    key = str(value or "").strip().lower()
    return DOCUMENT_TYPE_LABELS.get(key, key.replace("_", " ").replace("-", " ").title() or "Diploma")


def document_number_label(value: object) -> str:
    raw = str(value or "").strip()
    if not raw or raw.lower() in {"none", "null", "nan"}:
        return ""
    if raw.isdigit():
        return f"{int(raw):,}".replace(",", ".")
    return raw


def article_anchors(body: str) -> str:
    """Promote article labels to headings without duplicating the legal text."""
    output: list[str] = []
    for line in body.strip().splitlines():
        match = ARTICLE_LINE.match(line) if line.lstrip().startswith(("**Art.", "Art.")) else None
        if match:
            label = re.sub(r"\s+", " ", match.group(1)).strip()
            remainder = match.group(2).strip()
            output.extend([f"## {label}", ""])
            if remainder:
                output.append(remainder)
        else:
            output.append(line)
    return "\n".join(output).strip() + "\n"


class _ReaderHTMLSanitizer(HTMLParser):
    """Keep the semantic markup needed by the reader and discard active content."""

    ALLOWED = {
        "a", "abbr", "b", "blockquote", "br", "caption", "code", "dd", "del",
        "details", "div", "dl", "dt", "em", "h2", "h3", "h4", "hr", "i",
        "li", "ol", "p", "pre", "s", "small", "span", "strong", "sub", "summary",
        "sup", "table", "tbody", "td", "th", "thead", "tr", "u", "ul",
    }
    VOID = {"br", "hr"}
    DROP = {"embed", "iframe", "object", "script", "style", "svg", "math"}
    ATTRS = {
        "a": {"href", "rel", "target", "title"},
        "details": {"open"},
        "div": {"class", "id", "role", "aria-label"},
        "h2": {"class", "id"},
        "h3": {"class", "id"},
        "h4": {"class", "id"},
        "ol": {"class"},
        "p": {"class", "id"},
        "span": {"class", "id", "role", "aria-label"},
        "table": {"class"},
        "td": {"colspan", "rowspan"},
        "th": {"colspan", "rowspan", "scope"},
        "ul": {"class"},
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.stack: list[str] = []
        self.drop_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.DROP:
            self.drop_depth += 1
            return
        if self.drop_depth or tag not in self.ALLOWED:
            return
        allowed = self.ATTRS.get(tag, set())
        safe_attrs: list[str] = []
        for name, value in attrs:
            name = name.lower()
            if name not in allowed or value is None:
                continue
            if name == "href":
                compact = value.strip().lower()
                if compact.startswith(("javascript:", "data:", "vbscript:")):
                    continue
            if name == "target" and value != "_blank":
                continue
            safe_attrs.append(f' {name}="{html.escape(value, quote=True)}"')
        if tag == "a" and any(name == "target" and value == "_blank" for name, value in attrs):
            if not any(item.startswith(" rel=") for item in safe_attrs):
                safe_attrs.append(' rel="noreferrer"')
        self.parts.append(f"<{tag}{''.join(safe_attrs)}>")
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.DROP and self.drop_depth:
            self.drop_depth -= 1
            return
        if self.drop_depth or tag in self.VOID or tag not in self.stack:
            return
        index = len(self.stack) - 1 - self.stack[::-1].index(tag)
        for closing in reversed(self.stack[index:]):
            self.parts.append(f"</{closing}>")
        del self.stack[index:]

    def handle_data(self, data: str) -> None:
        if not self.drop_depth:
            self.parts.append(html.escape(data, quote=False))

    def handle_comment(self, data: str) -> None:
        return

    def get_html(self) -> str:
        for tag in reversed(self.stack):
            self.parts.append(f"</{tag}>")
        self.stack.clear()
        return "".join(self.parts)


def reader_html(markdown_body: str) -> str:
    """Render trusted Markdown source into a safe HTML fragment for the single reader."""
    rendered = markdown.markdown(
        markdown_body,
        extensions=["toc", "tables", "fenced_code", "footnotes", "sane_lists"],
        output_format="html5",
    )
    sanitizer = _ReaderHTMLSanitizer()
    sanitizer.feed(rendered)
    sanitizer.close()
    return sanitizer.get_html()


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
    <button type="button" class="btn-focus-mode" id="btn-focus-mode" title="Alternar modo de leitura sem distrações" aria-pressed="false">
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


def reader_document(
    metadata: dict[str, object],
    body: str,
    relations: list[dict[str, object]],
    release_version: str,
) -> dict[str, object]:
    """Build the one-document payload loaded on demand by the integrated reader."""
    document_id = str(metadata.get("id") or "")
    canonical_title = str(metadata.get("titulo") or "Diploma normativo")
    title = POPULAR_TITLES.get(document_id, canonical_title)
    source = next(iter(metadata.get("fonte_oficial") or []), "")
    article_body = contextualize_articles(body, relations, document_id)
    article_body = re.sub(rf"^#\s+{re.escape(canonical_title)}\s*\n+", "", article_body, count=1, flags=re.IGNORECASE)
    article_html = reader_html(article_anchors(article_body))
    relation_cards = "".join(relation_markup(relation) for relation in relations)
    relation_markup_html = (
        f'<details class="relation-list"><summary>Exibir {len(relations)} relações registradas</summary>{relation_cards}</details>'
        if len(relations) > 12 else relation_cards
    )
    return {
        "schema": "vademecum-reader-document/v1",
        "id": document_id,
        "title": title,
        "type": document_type_label(metadata.get("tipo")),
        "number": document_number_label(metadata.get("numero")),
        "year": str(metadata.get("ano") or ""),
        "domain": domain_label(str(metadata.get("dominio") or "")),
        "ementa": str(metadata.get("ementa") or ""),
        "status": str(metadata.get("situacao") or "desconhecida"),
        "status_label": status_label(str(metadata.get("situacao") or "desconhecida")),
        "consolidation": str(metadata.get("consolidacao_status") or "desconhecida"),
        "fidelity": str(metadata.get("fidelity_status") or "não informado"),
        "cutoff": str(metadata.get("data_corte") or "não informado"),
        "source_url": str(source),
        "source_unit_id": str(metadata.get("source_unit_id") or ""),
        "sha256_source_raw": str(metadata.get("sha256_source_raw") or ""),
        "sha256_published_body": str(metadata.get("sha256_published_body") or ""),
        "release": release_version,
        "article_html": article_html,
        "relations_html": reader_html(relation_markup_html),
        "relation_count": len(relations),
    }


def legacy_reader_page(metadata: dict[str, object], source_path: str) -> str:
    """Keep existing law URLs useful while moving their reading experience to /reader/."""
    document_id = str(metadata.get("id") or "")
    title = POPULAR_TITLES.get(document_id, str(metadata.get("titulo") or "Diploma normativo"))
    github_path = f"https://github.com/lucmolero/vademecum-md/blob/main/bases/curated/legislacao/federal/{source_path}"
    return f'''<div class="legacy-reader-redirect" data-document-id="{esc(document_id)}">
<p class="eyebrow">VadeMecum MD · leitor integrado</p>
<h1>{esc(title)}</h1>
<p>Este diploma agora é lido no VadeMecum completo, com índice de artigos, fonte e data de corte no mesmo espaço.</p>
<p><a class="md-button md-button--primary" href="../../../../../../reader/#/{esc(document_id)}">Abrir no leitor integrado <span aria-hidden="true">↗</span></a></p>
<p><a href="{esc(github_path)}">Abrir o Markdown canônico no GitHub</a> · <a href="../../../../../../generated/catalog/">Voltar ao catálogo</a></p>
</div>
<script>
(() => {{
  const article = /^#(art-[a-z0-9-]+)$/i.exec(location.hash);
  const suffix = article ? `/${{article[1]}}` : "";
  location.replace(new URL(`../../../../../../reader/#/{esc(document_id)}${{suffix}}`, location.href).href);
}})();
</script>
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
        "version": str(release.get("version", "1.1.3")),
        "quality": str(baseline.get("status", "unknown")),
    }


def home_page(rows: list[dict[str, str]], metrics: dict[str, object]) -> str:
    domain_counts = Counter(domain_key(row["domain"] or "especializado") for row in rows)
    domain_names = {domain_key(row["domain"] or "especializado"): domain_label(row["domain"] or "especializado") for row in rows}
    by_id = {row["id"]: row for row in rows}
    quick_specs = [
        ("br-federal-constituicao-1988", "CF/88", "Constituição Federal"),
        ("br-federal-lei_ordinaria-10406-2002", "CÓDIGO CIVIL", "Código Civil"),
        ("br-federal-lei_ordinaria-13105-2015", "PROCESSO CIVIL", "Código de Processo Civil"),
        ("br-federal-decreto_lei-2848-1940", "CÓDIGO PENAL", "Código Penal"),
        ("br-federal-decreto_lei-3689-1941", "PROCESSO PENAL", "Código de Processo Penal"),
        ("br-federal-decreto_lei-5452-1943", "TRABALHO", "Consolidação das Leis do Trabalho"),
    ]
    quick_cards = []
    for document_id, kind, title in quick_specs:
        row = by_id.get(document_id)
        if not row:
            continue
        quick_cards.append(
            f'<a class="vmd-quick-card" href="reader/#/{esc(document_id)}">'
            f'<span>{esc(kind)}</span><strong>{esc(title)}</strong>'
            f'<small>{esc(status_label(row["status"]))} no corte · abrir no leitor <b aria-hidden="true">↗</b></small></a>'
        )
    topic_specs = [
        ("administrativo", "Administrativo", "Estado, gestão e políticas públicas"),
        ("ambiental", "Ambiental", "Ambiente e recursos naturais"),
        ("civil", "Civil", "Pessoas, bens e relações privadas"),
        ("constitucional", "Constitucional", "Constituição e direitos fundamentais"),
        ("direitos_sociais", "Direitos sociais", "Proteção social e direitos coletivos"),
        ("penal", "Penal", "Crimes, garantias e processo"),
        ("trabalhista_previdenciario", "Trabalho e previdência", "Relações de trabalho e proteção previdenciária"),
        ("tributario_financeiro", "Tributário e financeiro", "Tributos e organização financeira"),
    ]
    topic_cards = []
    for key, title, description in topic_specs:
        count = domain_counts.get(key, 0)
        if not count:
            continue
        anchor = slugify(domain_names.get(key, title))
        topic_cards.append(
            f'<a class="vmd-topic-card" href="generated/catalog/#{esc(anchor)}">'
            f'<span>{esc(title)}</span><small>{count:03d} diplomas</small>'
            f'<p>{esc(description)}</p><b aria-hidden="true">↗</b></a>'
        )
    return f'''<div class="vmd-home">
  <nav class="vmd-home-nav" aria-label="Atalhos da página inicial">
    <span>ARQUIVO NORMATIVO <i aria-hidden="true"></i> CORTE {esc(metrics["cutoff"])}</span>
    <div><a href="reader/">Leitor completo</a><a href="generated/catalog/">Catálogo</a><a href="methodology/">Como funciona</a><a href="https://github.com/lucmolero/vademecum-md" target="_blank" rel="noreferrer">GitHub ↗</a></div>
  </nav>

  <section class="vmd-home-hero" aria-labelledby="vmd-home-title">
    <div class="vmd-home-copy">
      <p class="vmd-kicker"><span aria-hidden="true"></span> VADEMECUM MD · LEGISLAÇÃO FEDERAL</p>
      <h1 id="vmd-home-title">A lei,<br><em>sem perder</em><br>o contexto.</h1>
      <p class="vmd-home-lede">Um leitor para atravessar o texto normativo com fonte, data de corte e estrutura sempre à vista.</p>
      <form class="vmd-home-search" id="home-reader-search" role="search" action="reader/" method="get" data-reader-home-search>
        <label class="vmd-visually-hidden" for="home-query">Buscar legislação por nome, número ou tipo</label>
        <span class="vmd-search-mark" aria-hidden="true">⌕</span>
        <input id="home-query" name="q" type="search" placeholder="Código, número ou nome da norma…" autocomplete="off" aria-controls="home-search-results" aria-expanded="false" />
        <button type="submit">Buscar <span aria-hidden="true">↗</span></button>
        <div class="vmd-search-results" id="home-search-results" role="listbox" aria-label="Normas encontradas" hidden></div>
      </form>
      <p class="vmd-search-note"><kbd>Ctrl</kbd> + <kbd>K</kbd> para buscar <span>·</span> 375 diplomas no snapshot</p>
      <div class="vmd-home-actions"><a class="vmd-primary-action" href="reader/">Abrir o leitor integral <span aria-hidden="true">→</span></a><a class="vmd-secondary-action" href="generated/catalog/">Explorar por área</a></div>
    </div>
    <aside class="vmd-reading-preview" aria-label="Exemplo de leitura no VadeMecum MD">
      <div class="vmd-preview-top"><span>EXEMPLO DE LEITURA</span><span>CF · ART. 5º</span></div>
      <div class="vmd-preview-paper">
        <div class="vmd-preview-meta"><span>CONSTITUIÇÃO FEDERAL</span><span>1988</span></div>
        <h2>Dos direitos e garantias fundamentais</h2>
        <p><b>Art. 5º</b> Todos são iguais perante a lei, sem distinção de qualquer natureza…</p>
        <div class="vmd-preview-rule"></div>
        <div class="vmd-preview-source"><span>FONTE OFICIAL IDENTIFICADA</span><span>CORTE 2026-10-21</span></div>
      </div>
      <div class="vmd-preview-foot"><span>Texto com contexto verificável</span><span aria-hidden="true">↗</span></div>
    </aside>
  </section>

  <section class="vmd-snapshot" aria-label="Estado desta coleção">
    <div><strong>{int(metrics["corpus_count"])}</strong><span>diplomas curados</span></div>
    <div><strong>{esc(metrics["cutoff"])}</strong><span>data de corte do corpus</span></div>
    <div><strong>v{esc(metrics["version"])}</strong><span>release versionada</span></div>
    <p>Snapshot fixo; não representa atualização em tempo real.</p>
  </section>

  <section class="vmd-quick-section" id="normas-essenciais">
    <div class="vmd-section-heading"><div><p class="vmd-kicker">CONSULTA DIRETA</p><h2>Normas essenciais</h2><p>Abra um diploma no leitor e continue a consulta no mesmo espaço.</p></div><a href="reader/">Ver o acervo completo <span aria-hidden="true">↗</span></a></div>
    <div class="vmd-quick-grid">{"".join(quick_cards)}</div>
  </section>

  <section class="vmd-subject-section" id="assuntos">
    <div class="vmd-section-heading"><div><p class="vmd-kicker">ÍNDICE TEMÁTICO</p><h2>Entre pelo assunto</h2><p>Os totais acompanham os domínios publicados no catálogo deste snapshot.</p></div><a href="generated/catalog/">Todos os domínios <span aria-hidden="true">↗</span></a></div>
    <div class="vmd-topic-grid">{"".join(topic_cards)}</div>
  </section>

  <section class="vmd-trust-section" aria-labelledby="vmd-trust-title">
    <div><p class="vmd-kicker">LEITURA COM PROVENIÊNCIA</p><h2 id="vmd-trust-title">Texto. Fonte. Corte.</h2></div>
    <div><p>O VadeMecum MD é uma coleção curada, derivada de fontes públicas oficiais. O corte identifica a versão consultada; <strong>a publicação oficial continua sendo a autoridade textual.</strong></p><a href="legal-limits/">Entenda as fontes e os limites jurídicos ↗</a></div>
  </section>

  <footer class="vmd-home-footer"><span>VadeMecum MD · release v{esc(metrics["version"])} · snapshot {esc(metrics["cutoff"])}</span><span>{esc(metrics["tests"])} verificações automatizadas · <a href="https://github.com/lucmolero/vademecum-md">código aberto ↗</a></span></footer>
</div>
'''

def build() -> dict[str, int]:
    release_path = ROOT / "manifests/release.json"
    release_data = json.loads(release_path.read_text(encoding="utf-8")) if release_path.is_file() else {}
    release_version = str(release_data.get("version") or "")
    if GENERATED.exists():
        for child in GENERATED.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    laws = GENERATED / "laws"
    reader_data = GENERATED / "reader-data"
    documents_dir = reader_data / "documents"
    laws.mkdir(parents=True, exist_ok=True)
    documents_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    documents: list[tuple[str, dict[str, object], str]] = []
    for source in sorted((CURATED / "federal").rglob("*.md")):
        metadata, body = parse_frontmatter(source.read_text(encoding="utf-8"), strict=True)
        relative = source.relative_to(CURATED).as_posix()
        document_id = str(metadata.get("id") or "")
        if not re.fullmatch(r"[a-z0-9_-]+", document_id, re.IGNORECASE):
            raise ValueError(f"Unsafe or missing document ID for reader data: {relative}")
        documents.append((relative, metadata, body))
        rows.append({
            "id": document_id,
            "title": str(metadata.get("titulo", source.stem)),
            "type": document_type_label(metadata.get("tipo")),
            "number": document_number_label(metadata.get("numero")),
            "year": str(metadata.get("ano", "")),
            "domain": str(metadata.get("dominio", "")),
            "status": str(metadata.get("situacao", "desconhecida")),
            "priority": str(metadata.get("prioridade", "P2")),
            "source": str(next(iter(metadata.get("fonte_oficial") or []), "")),
            "cutoff": str(metadata.get("data_corte", "")),
            "consolidation": str(metadata.get("consolidacao_status", "desconhecida")),
            "fidelity": str(metadata.get("fidelity_status", "não informado")),
            "ementa": str(metadata.get("ementa", "")),
            "path": f"laws/{relative}",
        })

    graph_relations = relation_index(rows)
    by_id = {row["id"]: row for row in rows}
    for relative, metadata, body in documents:
        document_id = str(metadata.get("id") or "")
        relations = graph_relations.get(document_id, [])
        legacy_target = laws / relative
        legacy_target.parent.mkdir(parents=True, exist_ok=True)
        legacy_target.write_text(legacy_reader_page(metadata, relative), encoding="utf-8", newline="\n")
        payload = reader_document(metadata, body, relations, release_version)
        (documents_dir / f"{document_id}.json").write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8", newline="\n",
        )

    metrics = load_metrics(rows)
    domain_rows: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        domain_rows.setdefault(domain_key(row["domain"]), []).append(row)
    domain_index = [
        {
            "key": key,
            "title": domain_label(domain_rows[key][0]["domain"]),
            "slug": slugify(domain_label(domain_rows[key][0]["domain"])),
            "count": len(domain_rows[key]),
        }
        for key in sorted(domain_rows)
    ]
    index_documents = []
    for row in sorted(rows, key=lambda item: (domain_label(item["domain"]).casefold(), POPULAR_TITLES.get(item["id"], item["title"]).casefold())):
        display_title = POPULAR_TITLES.get(row["id"], row["title"])
        index_documents.append({
            "id": row["id"],
            "title": display_title,
            "canonical_title": row["title"],
            "type": row["type"],
            "number": row["number"],
            "year": row["year"],
            "domain": domain_label(row["domain"]),
            "domain_key": domain_key(row["domain"]),
            "status": row["status"],
            "status_label": status_label(row["status"]),
            "priority": row["priority"],
            "cutoff": row["cutoff"],
            "ementa": row["ementa"],
            "aliases": list(dict.fromkeys([display_title, row["title"], f'{row["type"]} {row["number"]}/{row["year"]}'])),
        })
    reader_index = {
        "schema": "vademecum-reader-index/v1",
        "release": release_version,
        "cutoff": metrics["cutoff"],
        "document_count": len(rows),
        "domains": domain_index,
        "documents": index_documents,
    }
    (reader_data / "index.json").write_text(
        json.dumps(reader_index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8", newline="\n",
    )

    code_order = [
        "br-federal-constituicao-1988",
        "br-federal-lei_ordinaria-10406-2002",
        "br-federal-lei_ordinaria-13105-2015",
        "br-federal-decreto_lei-2848-1940",
        "br-federal-decreto_lei-3689-1941",
        "br-federal-decreto_lei-5452-1943",
        "br-federal-lei_ordinaria-8078-1990",
        "br-federal-lei_ordinaria-14133-2021",
        "br-federal-lei_ordinaria-8906-1994",
        "br-federal-lei_ordinaria-5172-1966",
    ]
    catalog = [
        "# Catálogo da legislação",
        "",
        '<div class="vmd-catalog-hero">',
        '<p class="vmd-kicker">ACERVO FEDERAL · SNAPSHOT VERSIONADO</p>',
        "<p>Encontre um diploma pelo nome, número ou área. Abra qualquer resultado no leitor integrado para ler o texto e verificar seu contexto.</p>",
        f'<div class="vmd-catalog-facts"><span><strong>{len(rows)}</strong> diplomas</span><span>Release <strong>v{esc(metrics["version"])}</strong></span><span>Corte <strong>{esc(metrics["cutoff"])}</strong></span></div>',
        '<a class="vmd-primary-action" href="../../reader/">Abrir o leitor completo <span aria-hidden="true">↗</span></a>',
        "</div>",
        "",
        "## Grandes códigos e referências",
        "",
        '<div class="vmd-catalog-featured">',
    ]
    for document_id in code_order:
        row = by_id.get(document_id)
        if not row:
            continue
        label = POPULAR_TITLES.get(document_id, row["title"])
        number_year = f'{row["number"]}/{row["year"]}' if row["number"] else row["year"]
        catalog.extend([
            f'<a class="vmd-catalog-code" href="../../reader/#/{esc(document_id)}">',
            f'<span>{esc(row["type"])} · {esc(number_year)}</span>',
            f'<strong>{esc(label)}</strong>',
            f'<small>{esc(status_label(row["status"]))} no corte <b aria-hidden="true">↗</b></small>',
            "</a>",
        ])
    catalog.extend(["</div>", "", "## Navegar por área", "", '<nav class="vmd-catalog-index" aria-label="Índice de áreas">'])
    for item in domain_index:
        catalog.append(
            f'<a href="#{esc(item["slug"])}"><span>{esc(item["title"])}</span><small>{int(item["count"]):03d}</small></a>'
        )
    catalog.extend(["</nav>", ""])
    for domain in sorted(domain_rows, key=lambda key: domain_label(domain_rows[key][0]["domain"]).casefold()):
        label = domain_label(domain_rows[domain][0]["domain"])
        slug = slugify(label)
        catalog.extend([
            f'<div class="vmd-catalog-domain" id="{esc(slug)}"></div>',
            f"## {esc(label)}",
            "",
            '<div class="vmd-table-wrap"><table class="vmd-catalog-table">',
            '<thead><tr><th scope="col">Diploma</th><th scope="col">Situação no corte</th><th scope="col">Prioridade</th></tr></thead><tbody>',
        ])
        for row in sorted(domain_rows[domain], key=lambda item: POPULAR_TITLES.get(item["id"], item["title"]).casefold()):
            display_title = POPULAR_TITLES.get(row["id"], row["title"])
            number_year = f'{row["number"]}/{row["year"]}' if row["number"] else row["year"]
            catalog.append(
                f'<tr><td><a href="../../reader/#/{esc(row["id"])}">{esc(display_title)}</a>'
                f'<span class="vmd-catalog-subtitle">{esc(row["type"])} · {esc(number_year)}</span></td>'
                f'<td><span class="vmd-status-text">{esc(status_label(row["status"]))}</span></td>'
                f'<td><span class="vmd-priority">{esc(row["priority"])}</span></td></tr>'
            )
        catalog.extend(["</tbody></table></div>", ""])
    (GENERATED / "catalog.md").write_text("\n".join(catalog) + "\n", encoding="utf-8", newline="\n")

    law_index = f'''# Arquivos da legislação

<div class="vmd-library-index">
<p class="vmd-kicker">DISTRIBUIÇÃO E LEITURA</p>
<h2>O acervo em três formas</h2>
<p>Use o leitor para percorrer as normas no navegador, o catálogo para navegar por áreas ou a release para baixar e fixar uma cópia reproduzível.</p>
<div class="vmd-library-links">
<a href="../../reader/"><strong>Leitor integral</strong><span>Leia os diplomas no mesmo espaço, com índice de artigos e proveniência.</span></a>
<a href="../catalog/"><strong>Catálogo completo</strong><span>Veja os diplomas agrupados por área, estado e prioridade.</span></a>
<a href="https://github.com/lucmolero/vademecum-md/releases"><strong>Releases versionadas ↗</strong><span>Baixe o corpus, manifestos e checksums da versão escolhida.</span></a>
<a href="https://github.com/lucmolero/vademecum-md/tree/main/bases/curated/legislacao/federal"><strong>Markdown canônico ↗</strong><span>Consulte os arquivos de origem do leitor no repositório.</span></a>
</div>
<p class="vmd-library-note">A release consultada tem corte em <strong>{esc(metrics["cutoff"])}</strong>. O site não representa atualização em tempo real nem substitui a publicação oficial.</p>
</div>
'''
    (laws / "index.md").write_text(law_index, encoding="utf-8", newline="\n")

    home = "<!-- Generated by tools/site/build_site.py; edit the generator, not this file. -->\n\n" + home_page(rows, metrics)
    (SITE / "index.md").write_text(home, encoding="utf-8", newline="\n")
    reader_metrics = {
        "schema": "vademecum-reader-metrics/v1",
        "document_count": len(rows),
        "domain_count": len(domain_rows),
        "article_count": sum(len(re.findall(r"^\s*(?:\*\*)?Art\.\s+[0-9]+(?:\s*[ºª°])?(?:\s*-\s*[A-Za-z])?(?:\*\*)?", body, re.IGNORECASE | re.MULTILINE)) for _, _, body in documents),
        "reader_index_bytes": (reader_data / "index.json").stat().st_size,
        "reader_data_bytes": sum(path.stat().st_size for path in documents_dir.glob("*.json")),
    }
    (reader_data / "metrics.json").write_text(json.dumps(reader_metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (GENERATED / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"documents": len(rows), "domains": len(domain_rows), "relations": int(metrics["relations"]), "reader_data_bytes": int(reader_metrics["reader_data_bytes"])}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validar que a camada de site pode ser gerada")
    args = parser.parse_args()
    result = build()
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
