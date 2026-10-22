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


def status_label(status: str) -> str:
    return {
        "em_vigor": "Em vigor",
        "parcialmente_revogada": "Parcialmente revogada",
        "revogada": "Revogada",
        "transitoria": "Transitória",
        "desconhecida": "Situação desconhecida",
    }.get(status, status.replace("_", " ").title())


def law_page(metadata: dict[str, object], body: str) -> str:
    title = str(metadata.get("titulo") or "Diploma normativo")
    ementa = str(metadata.get("ementa") or "Ementa não disponível na publicação pública.")
    source = next(iter(metadata.get("fonte_oficial") or []), "")
    status = str(metadata.get("situacao") or "desconhecida")
    consolidation = str(metadata.get("consolidacao_status") or "desconhecida")
    fidelity = str(metadata.get("fidelity_status") or "não informado")
    document_id = str(metadata.get("id") or "")
    cutoff = str(metadata.get("data_corte") or "não informado")
    article_body = article_anchors(body)
    # The canonical title is retained in the body. The generated page uses a
    # richer header and removes only the first identical H1 for presentation.
    article_body = re.sub(rf"^#\s+{re.escape(title)}\s*\n+", "", article_body, count=1, flags=re.IGNORECASE)
    source_link = f'<a href="{esc(source)}" rel="noreferrer">Fonte oficial</a>' if source else "Fonte oficial indisponível"
    return f'''<div class="law-hero" data-law-id="{esc(document_id)}">
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
        "official_source_count": sum(bool(row.get("source")) for row in rows),
        "relations": relations,
        "tests": tests,
        "cutoff": cutoff,
        "version": str(release.get("version", "1.1.1")),
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
  <a class="metric-card reveal" href="quality/"><span>Núcleo P0</span><strong>{metrics["p0_count"]}<sup>/33</sup></strong><small>consolidado</small></a>
  <a class="metric-card reveal" href="graph/"><span>Relações</span><strong>{metrics["relations"]:,}</strong><small>grafo normativo</small></a>
  <a class="metric-card reveal" href="quality/"><span>Data de corte</span><strong>{esc(metrics["cutoff"])}</strong><small>snapshot público</small></a>
</div>

<section class="audiences-section reveal">
  <div class="section-heading"><div><p class="eyebrow">Uma base, três leituras</p><h2>Feito para quem lê, mede e constrói.</h2></div><a href="audiences/">Ver contratos de consumo ↗</a></div>
  <div class="audience-grid">
    <a class="audience-card audience-law" href="audiences/#para-advogados-e-pesquisadores-juridicos"><span class="audience-kicker">01 · jurídico</span><h3>Advogados e pesquisadores</h3><p>Texto integral, situação, fonte oficial e citação por dispositivo.</p><span class="audience-link">Ler com contexto ↗</span></a>
    <a class="audience-card audience-data" href="audiences/#para-cientistas-de-dados"><span class="audience-kicker">02 · dados</span><h3>Cientistas de dados</h3><p>IDs estáveis, hashes, manifestos e relações para pipelines reproduzíveis.</p><span class="audience-link">Explorar o contrato ↗</span></a>
    <a class="audience-card audience-agent" href="audiences/#para-desenvolvedores-de-agentes-de-ia"><span class="audience-kicker">03 · agentes</span><h3>Desenvolvedores de IA</h3><p>Evidência rastreável, limites explícitos e Markdown pronto para ferramentas.</p><span class="audience-link">Construir com segurança ↗</span></a>
  </div>
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
        target.write_text(law_page(metadata, body), encoding="utf-8", newline="\n")
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
    ]
    for domain in sorted(by_domain):
        slug = slugify(domain)
        catalog.extend([f'<div id="{esc(slug)}"></div>', f"## {esc(domain_label(domain))}", "", "| Diploma | Situação | Prioridade |", "| --- | --- | --- |"])
        for row in by_domain[domain]:
            catalog.append(f"| [{row['title']}]({row['path']}) | `{status_label(row['status'])}` | `{row['priority']}` |")
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
