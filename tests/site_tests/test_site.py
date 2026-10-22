import json
import importlib.util
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
SITE_BUILDER_SPEC = importlib.util.spec_from_file_location("vmd_site_builder", ROOT / "tools/site/build_site.py")
SITE_BUILDER = importlib.util.module_from_spec(SITE_BUILDER_SPEC)
SITE_BUILDER_SPEC.loader.exec_module(SITE_BUILDER)


def contrast_ratio(first: str, second: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

    bright, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (bright + 0.05) / (dark + 0.05)


class SiteContractTest(unittest.TestCase):
    def test_brand_svg_assets_are_accessible_self_contained_and_have_unique_ids(self):
        assets = sorted((ROOT / "site_docs/assets").glob("*.svg"))
        self.assertGreaterEqual(len(assets), 6)
        for path in assets:
            with self.subTest(asset=path.name):
                root = ET.parse(path).getroot()
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                elements = list(root.iter())
                local_names = [element.tag.rsplit("}", 1)[-1] for element in elements]
                self.assertIn("title", local_names)
                self.assertIn("desc", local_names)
                self.assertNotIn("script", local_names)
                self.assertNotIn("foreignObject", local_names)

                identifiers = [element.get("id") for element in elements if element.get("id")]
                self.assertEqual(len(identifiers), len(set(identifiers)))
                for element in elements:
                    for attribute, value in element.attrib.items():
                        if attribute.rsplit("}", 1)[-1] == "href":
                            self.assertFalse(value.startswith(("http:", "https:", "//")))
                source = path.read_text(encoding="utf-8")
                self.assertNotRegex(source, r"(?i)@import\s+['\"]?https?://")
                self.assertNotRegex(source, r"(?i)url\(\s*['\"]?https?://")

    def test_brand_text_tokens_meet_wcag_aa_on_declared_flat_surfaces(self):
        css = (ROOT / "site_docs/stylesheets/extra.css").read_text(encoding="utf-8")
        light_block = re.search(r":root\s*\{([^}]+)\}", css)
        dark_block = re.search(r'\[data-md-color-scheme="slate"\]\s*\{([^}]+)\}', css)
        self.assertIsNotNone(light_block)
        self.assertIsNotNone(dark_block)
        for theme, block in (("light", light_block.group(1)), ("dark", dark_block.group(1))):
            values = dict(re.findall(r"(--vmd-[\w-]+):\s*(#[0-9a-fA-F]{6})", block))
            pairs = (
                ("--vmd-ink", "--vmd-ivory"),
                ("--vmd-ink", "--vmd-paper"),
                ("--vmd-slate", "--vmd-ivory"),
                ("--vmd-green", "--vmd-ivory"),
                ("--vmd-gold-text", "--vmd-ivory"),
                ("--vmd-amber-text", "--vmd-ivory"),
                ("--vmd-red", "--vmd-ivory"),
            )
            for foreground, background in pairs:
                with self.subTest(theme=theme, foreground=foreground, background=background):
                    self.assertIn(foreground, values)
                    self.assertIn(background, values)
                    self.assertGreaterEqual(contrast_ratio(values[foreground], values[background]), 4.5)

    def test_site_contract_and_brand_assets_exist(self):
        self.assertTrue((ROOT / "mkdocs.yml").is_file())
        self.assertTrue((ROOT / "site_docs/index.md").is_file())
        self.assertTrue((ROOT / "site_docs/assets/brand-mark.svg").is_file())
        self.assertTrue((ROOT / "site_docs/assets/logo-lockup.svg").is_file())
        self.assertTrue((ROOT / "site_docs/assets/logo-lockup-dark.svg").is_file())
        self.assertTrue((ROOT / "site_docs/stylesheets/extra.css").is_file())
        self.assertTrue((ROOT / "site_docs/javascripts/portfolio.js").is_file())
        self.assertTrue((ROOT / "site_docs/javascripts/reader.js").is_file())
        mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        self.assertIn("logo: site_docs/assets/brand-mark.svg", mkdocs)
        css = (ROOT / "site_docs/stylesheets/extra.css").read_text(encoding="utf-8")
        dark_scheme = re.search(r'\[data-md-color-scheme="slate"\]\s*\{([^}]+)\}', css)
        self.assertIsNotNone(dark_scheme)
        dark_tokens = dict(re.findall(r"(--md-primary-(?:fg|bg)-color):\s*(#[0-9a-fA-F]{6})", dark_scheme.group(1)))
        self.assertGreaterEqual(
            contrast_ratio(dark_tokens["--md-primary-fg-color"], dark_tokens["--md-primary-bg-color"]),
            4.5,
        )
        self.assertIn(".md-content h1, .md-content h2, .md-content h3 { color: var(--vmd-ink); }", css)
        self.assertTrue((ROOT / "site_docs/audiences.md").is_file())
        catalog = ROOT / "site_docs/generated/catalog.md"
        self.assertTrue(catalog.is_file())
        self.assertIn("Catálogo da legislação", catalog.read_text(encoding="utf-8"))
        self.assertIn("Grandes Códigos da República", catalog.read_text(encoding="utf-8"))
        homepage = ROOT / "site_docs/index.md"
        homepage_text = homepage.read_text(encoding="utf-8")
        self.assertIn("Legislação federal.", homepage_text)
        self.assertIn('id="home-search"', homepage_text)
        self.assertIn("Leis de consulta frequente", homepage_text)
        self.assertIn('class="home-data-strip"', homepage_text)
        self.assertNotIn("domain-grid", homepage_text)
        self.assertNotIn("audience-grid", homepage_text)
        self.assertNotIn("status-em_vigor", homepage_text)
        self.assertNotIn("testes automatizados", homepage_text)
        self.assertIn("Para advogados", (ROOT / "site_docs/audiences.md").read_text(encoding="utf-8"))
        self.assertTrue((ROOT / "tools/release/build_sbom.py").is_file())

    def test_readme_describes_static_github_rendering_and_avoids_unsupported_claims(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("<picture>", readme)
        self.assertIn("página Markdown estática", readme)
        self.assertIn("docs/INDICE_LEGISLACAO.md", readme)
        self.assertIn("## Encontre uma lei", readme)
        self.assertNotIn("Paywall", readme)
        self.assertNotIn("100% PASS", readme)
        self.assertNotIn("leitor forense aberto", readme)

    def test_readme_relative_links_and_assets_resolve(self):
        readme_path = ROOT / "README.md"
        readme = readme_path.read_text(encoding="utf-8")
        references = re.findall(
            r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)", readme
        )
        references.extend(
            re.findall(r"\b(?:href|src)=[\"']([^\"']+)[\"']", readme, re.IGNORECASE)
        )
        missing = []
        for reference in references:
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (readme_path.parent / unquote(parsed.path)).resolve()
            if not target.exists():
                missing.append(reference)
        self.assertEqual(missing, [])

    def test_homepage_audience_cards_target_existing_sections(self):
        homepage = (ROOT / "site_docs/index.md").read_text(encoding="utf-8")
        audiences = (ROOT / "site_docs/audiences.md").read_text(encoding="utf-8")
        self.assertIn('href="generated/catalog/"', homepage)
        self.assertIn('href="sources/"', homepage)
        self.assertIn('href="methodology/"', homepage)
        self.assertIn('href="quality/"', homepage)
        self.assertNotIn('href="audiences/#', homepage)
        self.assertIn("## Para advogados e pesquisadores jurídicos", audiences)
        self.assertIn("## Para agentes de IA", audiences)

    def test_homepage_and_reader_use_compact_reading_scale(self):
        homepage = (ROOT / "site_docs/index.md").read_text(encoding="utf-8")
        css = (ROOT / "site_docs/stylesheets/extra.css").read_text(encoding="utf-8")
        reader = (ROOT / "site_docs/javascripts/reader.js").read_text(encoding="utf-8")
        self.assertIn('aria-labelledby="home-title"', homepage)
        self.assertIn('id="home-search"', homepage)
        self.assertIn('class="home-law-list"', homepage)
        self.assertIn(".md-content.font-sm .md-typeset p", css)
        self.assertIn("font-size: 13px", css)
        self.assertIn(".md-content.font-md .md-typeset p", css)
        self.assertIn("font-size: 14px", css)
        self.assertIn("font-size: 16px", css)
        self.assertIn('readPreference("vmd_font_size_idx_v3", "0")', reader)
        self.assertIn("decrease.disabled = sizeIndex === 0", reader)
        self.assertIn("increase.disabled = sizeIndex === sizes.length - 1", reader)
        toolbar = re.search(r"\.md-content:has\(\.law-hero\) \.reader-toolbar\s*\{([^}]+)\}", css)
        self.assertIsNotNone(toolbar)
        self.assertIn("position: sticky", toolbar.group(1))
        self.assertIn(".md-content:has(.law-hero) .reader-toolbar { position: static", css)

    def test_markdown_law_index_links_every_canonical_document(self):
        index_path = ROOT / "docs/INDICE_LEGISLACAO.md"
        index = index_path.read_text(encoding="utf-8")
        links = re.findall(r"\]\((\.\./bases/curated/legislacao/[^)]+\.md)\)", index)
        self.assertEqual(len(set(links)), 375)
        self.assertTrue(all((index_path.parent / link).resolve().is_file() for link in links))
        self.assertIn("Navegue por tipo e ano", index)
        self.assertIn("Ctrl+F", index)
        self.assertIn("[índice completo da legislação federal]", (ROOT / "bases/curated/README.md").read_text(encoding="utf-8"))

    def test_markdown_law_index_formats_missing_metadata_and_singular_counts(self):
        row = {
            "id": "br-federal-constituicao-1988",
            "title": "Ato constitucional de teste",
            "type": "ato_constitucional",
            "number": SITE_BUILDER.metadata_text(None),
            "year": SITE_BUILDER.metadata_text("None", "Sem ano"),
            "path": "laws/atos-constitucionais/1988/teste.md",
        }
        index = SITE_BUILDER.corpus_markdown_index([row], "2026-10-21")
        self.assertIn("· 1 diploma</summary>", index)
        self.assertNotIn("1 diplomas", index)
        self.assertNotIn("nº None", index)
        self.assertNotIn("None/1988", index)

    def test_hero_graph_is_a_real_keyboard_navigable_subgraph(self):
        home = (ROOT / "site_docs/index.md").read_text(encoding="utf-8")
        nodes = re.findall(r'<a class="hero-graph-node(?: is-central)?" href="([^"]+)" aria-label="([^"]+)">', home)
        edges = re.findall(r'<line class="hero-graph-edge"[^>]+aria-label="([^"]+)"[^>]+marker-end="url\(#hero-graph-arrow\)"', home)
        self.assertEqual(len(nodes), 5)
        self.assertGreaterEqual(len(edges), 1)
        self.assertTrue(all(label for _, label in nodes))
        self.assertTrue(all(label for label in edges))
        for href, _ in nodes:
            self.assertTrue(href.startswith("generated/laws/"))
            source = ROOT / "site_docs" / (href.rstrip("/") + ".md")
            self.assertTrue(source.is_file(), href)
        self.assertIn('href="graph/"', home)
        self.assertIn('class="hero-graph-relation-list"', home)
        self.assertRegex(home, r"Ver \d+ rela\u00e7\u00f5es e seus sentidos")
        self.assertNotIn("estrutura normativa em movimento", home)

        graph_path = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
        published = set()
        for line in graph_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                published.add((record["source_id"], record["type"], record["target_id"]))
        edge_pattern = r'<line class="hero-graph-edge"[^>]*data-source-id="([^"]+)" data-target-id="([^"]+)" data-relation="([^"]+)"'
        rendered_edges = re.findall(edge_pattern, home)
        self.assertEqual(len(rendered_edges), len(edges))
        self.assertTrue(all((source, relation, target) in published for source, target, relation in rendered_edges))
        detail_pattern = r'<li data-source-id="([^"]+)" data-target-id="([^"]+)" data-relation="([^"]+)"'
        detail_edges = re.findall(detail_pattern, home)
        self.assertEqual(set(rendered_edges), set(detail_edges))
        self.assertIn(("br-federal-lei_ordinaria-13964-2019", "altera", "br-federal-decreto_lei-2848-1940"), published)
        self.assertIn(("br-federal-lei_ordinaria-13964-2019", "altera", "br-federal-decreto_lei-2848-1940"),
                      {(source, relation, target) for source, target, relation in rendered_edges})

    def test_full_graph_index_preserves_every_published_direction(self):
        index = json.loads((ROOT / "site_docs/generated/graph-index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["schema"], "vademecum-graph/v1")
        self.assertEqual(index["node_count"], 375)
        self.assertEqual(index["edge_count"], 1841)
        node_ids = {node["id"] for node in index["nodes"]}
        source = ROOT / "bases/derived/relacoes/normative-graph.jsonl"
        published = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
        expected = [
            {"source_id": edge["source_id"], "target_id": edge["target_id"], "type": edge["type"]}
            for edge in published
            if edge["source_id"] in node_ids and edge["target_id"] in node_ids
            and edge["source_id"] != edge["target_id"]
        ]
        self.assertEqual(index["edges"], expected)
        self.assertTrue(all(edge["source_id"] in node_ids and edge["target_id"] in node_ids for edge in index["edges"]))
        published_triples = {(edge["source_id"], edge["type"], edge["target_id"]) for edge in expected}
        self.assertTrue(all(
            (edge["source_id"], edge["type"], edge["target_id"]) in published_triples
            for edge in index["featured"]["edges"]
        ))

    def test_readme_graph_preview_links_to_explorer_and_canonical_laws(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        graph = json.loads((ROOT / "site_docs/generated/graph-index.json").read_text(encoding="utf-8"))
        preview = ROOT / "site_docs/assets/normative-graph-preview.svg"
        ET.parse(preview)
        self.assertIn("BEGIN GENERATED NORMATIVE GRAPH", readme)
        self.assertIn("END GENERATED NORMATIVE GRAPH", readme)
        self.assertIn("site_docs/assets/normative-graph-preview.svg", readme)
        self.assertIn("https://lucmolero.github.io/vademecum-md/graph/", readme)
        section = readme.split("<!-- BEGIN GENERATED NORMATIVE GRAPH -->", 1)[1].split(
            "<!-- END GENERATED NORMATIVE GRAPH -->", 1
        )[0]
        rows = re.findall(r"^\| \[([^\]]+)\]\(([^)]+\.md)\) \|", section, re.MULTILINE)
        self.assertEqual(len(rows), len(graph["featured"]["edges"]))
        self.assertTrue(all((ROOT / href).is_file() for _, href in rows))

    def test_graph_explorer_has_search_filters_accessible_edges_and_page_scoped_script(self):
        page = (ROOT / "site_docs/graph.md").read_text(encoding="utf-8")
        hooks = (ROOT / "site_docs/hooks.py").read_text(encoding="utf-8")
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        self.assertIn('data-index-url="../generated/graph-index.json"', page)
        self.assertIn('id="graph-search"', page)
        self.assertIn('aria-expanded="false"', page)
        self.assertIn('id="graph-relation-filter"', page)
        self.assertIn('id="graph-direction-filter"', page)
        self.assertIn('id="graph-connection-list"', page)
        self.assertIn('role="status"', page)
        explorer = (ROOT / "site_docs/javascripts/graph-explorer.js").read_text(encoding="utf-8")
        self.assertIn('searchParams.get("node")', explorer)
        self.assertIn('searchParams.set("node", identifier)', explorer)
        self.assertIn('history.pushState', explorer)
        self.assertIn('addEventListener("popstate"', explorer)
        self.assertIn('focusAfter: "graph"', explorer)
        self.assertIn('focusAfter: "search"', explorer)
        self.assertIn('setAttribute("aria-expanded", String(visible))', explorer)
        self.assertIn("compartilhe o link ou use Voltar/Avançar", page)
        self.assertIn('page.file.src_uri == "graph.md"', hooks)
        self.assertIn("graph-explorer.js", hooks)
        self.assertNotIn("graph-explorer.js", config)

    def test_generated_catalog_does_not_claim_manual_status_or_priority(self):
        catalog = (ROOT / "site_docs/generated/catalog.md").read_text(encoding="utf-8")
        self.assertNotIn("`Em vigor`", catalog)
        self.assertNotIn("`P0`", catalog)
        self.assertIn("Tipo e número", catalog)
        self.assertNotIn('<div id="', catalog)

    def test_generated_law_page_has_editorial_metadata_and_article_anchor(self):
        law = ROOT / "site_docs/generated/laws/federal/leis-ordinarias/2002/lei-ordinaria-10406-2002.md"
        content = law.read_text(encoding="utf-8")
        self.assertIn("search:\n  exclude: true", content)
        self.assertIn('data-release="1.1.2"', content)
        self.assertIn('class="law-hero"', content)
        self.assertIn("## Art. 1º", content)
        self.assertIn("data-copy-id=", content)
        self.assertIn('class="reader-toolbar"', content)
        self.assertIn('id="btn-quick-jump"', content)
        self.assertIn('id="btn-focus-mode"', content)

    def test_search_index_covers_documents_and_article_anchors_compactly(self):
        index = json.loads((ROOT / "site_docs/generated/search-index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["schema"], "vademecum-search/v1")
        self.assertEqual(len(index["documents"]), 375)
        civil = next(document for document in index["documents"] if document["id"] == "br-federal-lei_ordinaria-10406-2002")
        self.assertIn(["Art. 186.", "art-186"], civil["articles"])
        self.assertEqual(civil["href"], "generated/laws/federal/leis-ordinarias/2002/lei-ordinaria-10406-2002/")

    def test_official_source_links_reject_non_allowlisted_or_unsafe_urls(self):
        self.assertEqual(
            SITE_BUILDER.safe_official_url("https://www.planalto.gov.br/ccivil_03/leis/l10406compilada.htm"),
            "https://www.planalto.gov.br/ccivil_03/leis/l10406compilada.htm",
        )
        self.assertEqual(SITE_BUILDER.safe_official_url("javascript:alert(1)"), "")
        self.assertEqual(SITE_BUILDER.safe_official_url("https://example.com/law"), "")

    def test_graph_context_preserves_direction_and_requires_an_article_device(self):
        relation = {
            "source_id": "law-a",
            "target_id": "law-b",
            "source_title": "Lei A",
            "target_title": "Lei B",
            "type": "altera",
            "dispositivo": "art. 5º",
            "confianca": "alta",
            "status_revisao": "aprovado_autonomamente",
            "fonte": "https://example.gov.br/lei",
            "evidencia_textual": "altera o art. 5º",
            "_site_id": "normative-relation-test",
            "_site_device_document_id": "law-b",
        }
        source_context = SITE_BUILDER.contextualize_articles("**Art. 5º** Texto.", [relation], "law-a")
        target_context = SITE_BUILDER.contextualize_articles("**Art. 5º** Texto.\n\n**Art. 6º** Outro.", [relation], "law-b")
        page = SITE_BUILDER.law_page({"id": "law-b", "titulo": "Lei B"}, "**Art. 5º** Texto.", [relation])
        self.assertNotIn("relation-margin-note", source_context)
        self.assertIn("relation-margin-note", target_context)
        self.assertIn("Ver relação no grafo", target_context)
        self.assertLess(target_context.index("Ver relação no grafo"), target_context.index("Texto."))
        self.assertIn("Lei A", page)
        self.assertIn("altera", page)
        self.assertIn("altera o art. 5º", page)
        self.assertIn('id="normative-relation-test"', page)
        self.assertLess(page.index("## Art. 5º"), page.index('id="law-relations-title"'))

        without_device = {**relation, "dispositivo": None}
        no_article_marker = SITE_BUILDER.contextualize_articles("**Art. 5º** Texto.", [without_device])
        no_article_page = SITE_BUILDER.law_page({"id": "law-a", "titulo": "Lei A"}, "**Art. 5º** Texto.", [without_device])
        self.assertNotIn("relation-margin-note", no_article_marker)
        self.assertIn("Dispositivo não identificado", no_article_page)

    def test_graph_mirror_is_shown_once_with_active_direction(self):
        active = {
            "source_id": "amending-law",
            "target_id": "amended-law",
            "type": "altera",
            "dispositivo": "art. 5º",
            "data_efeito": "2024-01-01",
            "evidencia_sha256": "same-evidence",
        }
        inverse = {
            **active,
            "source_id": "amended-law",
            "target_id": "amending-law",
            "type": "alterada_por",
        }
        unique = SITE_BUILDER.deduplicate_relation_mirrors([inverse, active])
        self.assertEqual(len(unique), 1)
        self.assertEqual(unique[0]["type"], "altera")
        self.assertEqual(unique[0]["source_id"], "amending-law")

    def test_pages_pull_request_build_has_no_deploy_permissions_or_cancellation_risk(self):
        workflow = yaml.load((ROOT / ".github/workflows/site.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        self.assertIn("pull_request", workflow["on"])
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertIn("github.ref", workflow["concurrency"]["group"])
        self.assertEqual(workflow["concurrency"]["cancel-in-progress"], "${{ github.event_name == 'pull_request' }}")

        build = workflow["jobs"]["build"]
        deploy = workflow["jobs"]["deploy"]
        self.assertEqual(build["permissions"], {"contents": "read"})
        self.assertEqual(deploy["if"], "github.ref == 'refs/heads/main'")
        self.assertEqual(deploy["permissions"], {"pages": "write", "id-token": "write"})
        build_actions = {step.get("uses") for step in build["steps"] if isinstance(step, dict)}
        deploy_actions = {step.get("uses") for step in deploy["steps"] if isinstance(step, dict)}
        self.assertIn("actions/upload-pages-artifact@v5", build_actions)
        self.assertIn("actions/deploy-pages@v5", deploy_actions)


if __name__ == "__main__":
    unittest.main()
