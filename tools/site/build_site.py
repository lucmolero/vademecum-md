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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from migrate_public_corpus import CURATED, parse_frontmatter  # noqa: E402

SITE = ROOT / "site_docs"
GENERATED = SITE / "generated"


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


def status_label(status: str) -> str:
    return {
        "em_vigor": "Em vigor",
        "parcialmente_revogada": "Parcialmente revogada",
        "revogada": "Revogada",
        "transitoria": "Transitória",
        "desconhecida": "Situação desconhecida",
    }.get(status, status.replace("_", " ").title())


def legacy_reader_page(document_id: str, title: str, source_path: str) -> str:
    """Keep old per-law URLs useful by forwarding them to the canonical library."""
    title = POPULAR_TITLES.get(document_id, title)
    github_path = f"https://github.com/lucmolero/vademecum-md/blob/main/bases/curated/legislacao/federal/{source_path}"
    return f'''<div class="legacy-reader-redirect" data-document-id="{esc(document_id)}">
<p class="eyebrow">VadeMecum MD · biblioteca oficial</p>
<h1>{esc(title)}</h1>
<p>O leitor oficial agora está na Biblioteca Vademecum, com índice, fonte e dados de proveniência da mesma release.</p>
<p><a class="md-button md-button--primary" href="https://lucmolero.github.io/vademecum-md/biblioteca/#documento={esc(document_id)}">Abrir na biblioteca <span aria-hidden="true">↗</span></a></p>
<p><a href="{esc(github_path)}">Abrir o Markdown canônico no GitHub</a> · <a href="../../../../../../generated/catalog/">Voltar ao catálogo</a></p>
</div>
<script>
(() => {{
  const article = /^#(art-[a-z0-9-]+)$/i.exec(location.hash);
  const params = new URLSearchParams({{documento: "{esc(document_id)}"}});
  if (article) params.set("artigo", article[1]);
  const target = new URL("https://lucmolero.github.io/vademecum-md/biblioteca/");
  target.hash = params.toString();
  location.replace(target.href);
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


def build() -> dict[str, int]:
    release_path = ROOT / "manifests/release.json"
    release_data = json.loads(release_path.read_text(encoding="utf-8")) if release_path.is_file() else {}
    if GENERATED.exists():
        for child in GENERATED.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    laws = GENERATED / "laws"
    laws.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for source in sorted((CURATED / "federal").rglob("*.md")):
        metadata, _body = parse_frontmatter(source.read_text(encoding="utf-8"), strict=True)
        relative = source.relative_to(CURATED).as_posix()
        document_id = str(metadata.get("id") or "")
        if not re.fullmatch(r"[a-z0-9_-]+", document_id, re.IGNORECASE):
            raise ValueError(f"Unsafe or missing document ID in canonical corpus: {relative}")
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

    by_id = {row["id"]: row for row in rows}
    for row in rows:
        relative = row["path"].removeprefix("laws/")
        legacy_target = laws / relative
        legacy_target.parent.mkdir(parents=True, exist_ok=True)
        legacy_target.write_text(legacy_reader_page(row["id"], row["title"], relative), encoding="utf-8", newline="\n")

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
        '<a class="vmd-primary-action" href="https://lucmolero.github.io/vademecum-md/biblioteca/">Abrir o leitor completo <span aria-hidden="true">↗</span></a>',
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
            f'<a class="vmd-catalog-code" href="https://lucmolero.github.io/vademecum-md/biblioteca/#documento={esc(document_id)}">',
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
                f'<tr><td><a href="https://lucmolero.github.io/vademecum-md/biblioteca/#documento={esc(row["id"])}">{esc(display_title)}</a>'
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
<a href="https://lucmolero.github.io/vademecum-md/biblioteca/"><strong>Biblioteca e leitor</strong><span>Leia os diplomas no mesmo espaço, com índice de artigos e proveniência.</span></a>
<a href="../catalog/"><strong>Catálogo completo</strong><span>Veja os diplomas agrupados por área, estado e prioridade.</span></a>
<a href="https://github.com/lucmolero/vademecum-md/releases"><strong>Releases versionadas ↗</strong><span>Baixe o corpus, manifestos e checksums da versão escolhida.</span></a>
<a href="https://github.com/lucmolero/vademecum-md/tree/main/bases/curated/legislacao/federal"><strong>Markdown canônico ↗</strong><span>Consulte os arquivos de origem do leitor no repositório.</span></a>
</div>
<p class="vmd-library-note">A release consultada tem corte em <strong>{esc(metrics["cutoff"])}</strong>. O site não representa atualização em tempo real nem substitui a publicação oficial.</p>
</div>
'''
    (laws / "index.md").write_text(law_index, encoding="utf-8", newline="\n")

    (GENERATED / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"documents": len(rows), "domains": len(domain_rows), "relations": int(metrics["relations"])}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validar que a camada de site pode ser gerada")
    args = parser.parse_args()
    result = build()
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
