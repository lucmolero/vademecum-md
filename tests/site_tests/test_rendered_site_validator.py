import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools" / "validate"))
from validate_site import SOCIAL_CARD_PAGES, validate, validate_internal_links, validate_social_cards  # noqa: E402


class RenderedSiteValidatorTest(unittest.TestCase):
    def test_internal_link_validator_checks_routes_and_fragments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                '<a href="audiences/#para-agentes">Agentes</a>'
                '<button aria-label="Abrir menu"></button>', encoding="utf-8"
            )
            audiences = root / "audiences" / "index.html"
            audiences.parent.mkdir()
            audiences.write_text('<h2 id="para-agentes">Agentes</h2>', encoding="utf-8")
            site_url = "https://example.org/project/"
            self.assertEqual(validate_internal_links(root, site_url), [])
            (root / "index.html").write_text(
                '<a href="audiences/#missing">Agentes</a><a href="missing/">Lei</a>'
                '<a href="audiences/"></a><button></button>', encoding="utf-8"
            )
            audiences.write_text(
                '<h2 id="para-agentes">Agentes</h2><span id="para-agentes">Duplicado</span>',
                encoding="utf-8",
            )
            errors = validate_internal_links(root, site_url)
            self.assertEqual(len(errors), 5)
            self.assertTrue(any("missing internal link fragment" in error for error in errors))
            self.assertTrue(any("missing internal link target" in error for error in errors))
            self.assertTrue(any("duplicate HTML id" in error for error in errors))
            self.assertEqual(sum("missing accessible name" in error for error in errors), 2)

    def test_accessibility_baseline_accepts_valid_document(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "stylesheets").mkdir(parents=True)
            (root / "javascripts").mkdir(parents=True)
            (root / "index.html").write_text(
                '<html lang="pt-BR"><body><a data-md-component="skip" href="#main">Pular</a>'
                '<main id="main"><h1>VadeMecum MD</h1><img alt="Marca" src="mark.svg"></main></body></html>',
                encoding="utf-8",
            )
            (root / "stylesheets" / "extra.css").write_text(
                ":focus { outline: 2px solid; } @media (prefers-reduced-motion: reduce) {} "
                ".vmd-hero {} .law-hero {}",
                encoding="utf-8",
            )
            (root / "javascripts" / "portfolio.js").write_text(
                'window.matchMedia("(prefers-reduced-motion: reduce)");', encoding="utf-8"
            )
            self.assertEqual(validate(root), [])

    def test_accessibility_baseline_rejects_missing_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text("<html><body><img src='mark.svg'></body></html>", encoding="utf-8")
            errors = validate(root)
            self.assertTrue(any("lang" in error for error in errors))
            self.assertTrue(any("skip" in error for error in errors))
            self.assertTrue(any("heading" in error for error in errors))
            self.assertTrue(any("image" in error for error in errors))

    def test_social_card_validator_accepts_metadata_and_local_pngs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, page_name in enumerate(SOCIAL_CARD_PAGES):
                page = root / page_name
                page.parent.mkdir(parents=True, exist_ok=True)
                image_path = f"assets/images/social/card-{index}.png"
                image = root / image_path
                image.parent.mkdir(parents=True, exist_ok=True)
                image.write_bytes(bytes([137, 80, 78, 71, 13, 10, 26, 10]) + b"fixture")
                page.write_text(
                    '<meta property="og:title" content="Título">'
                    '<meta property="og:description" content="Descrição">'
                    f'<meta property="og:image" content="https://example.org/project/{image_path}">'
                    '<meta property="og:url" content="https://example.org/project/">'
                    '<meta property="twitter:card" content="summary_large_image">',
                    encoding="utf-8",
                )
            self.assertEqual(validate_social_cards(root, "https://example.org/project/"), [])

    def test_social_card_validator_rejects_missing_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            page.write_text(
                '<meta property="og:image" content="https://example.org/project/missing.png">'
                '<meta property="twitter:card" content="summary_large_image">',
                encoding="utf-8",
            )
            errors = validate_social_cards(root, "https://example.org/project/")
            self.assertTrue(any("social image file missing" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
