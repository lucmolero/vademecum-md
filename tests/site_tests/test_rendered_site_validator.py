import tempfile
import unittest
from pathlib import Path
import sys
import json

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools" / "validate"))
from validate_site import validate, validate_dark_theme_contrast  # noqa: E402


class RenderedSiteValidatorTest(unittest.TestCase):
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
                ':focus { outline: 2px solid; } [data-md-color-scheme="slate"] {'
                '--md-default-bg-color: #0d1828; --vmd-paper: #14253a; '
                '--vmd-slate: #b9c9de; --vmd-green: #83d6ae; --vmd-amber: #f0c078; '
                '--vmd-red: #f2a3a3; --vmd-gold: #e0bb70; --vmd-ink-soft: #b9c9de; } '
                "@media (prefers-reduced-motion: reduce) {} "
                ".vmd-hero {} .law-hero {}",
                encoding="utf-8",
            )
            (root / "javascripts" / "portfolio.js").write_text(
                'window.matchMedia("(prefers-reduced-motion: reduce)");', encoding="utf-8"
            )
            (root / "stylesheets" / "launch.css").write_text(".vmd-reader-app {}", encoding="utf-8")
            (root / "javascripts" / "reader.js").write_text("function initIntegratedReader() {}", encoding="utf-8")
            data = root / "generated" / "reader-data"
            (data / "documents").mkdir(parents=True)
            (data / "index.json").write_text(
                json.dumps({"schema": "vademecum-reader-index/v1", "document_count": 1, "documents": [{"id": "law"}]}),
                encoding="utf-8",
            )
            (data / "documents" / "law.json").write_text(
                json.dumps({"schema": "vademecum-reader-document/v1", "id": "law", "article_html": "<p>Texto</p>"}),
                encoding="utf-8",
            )
            (root / "reader").mkdir()
            (root / "reader" / "index.html").write_text(
                '<html lang="pt-BR"><body><a data-md-component="skip" href="#reader">Pular</a>'
                '<main id="reader"><h1>Leitor</h1><div data-reader-app></div></main></body></html>',
                encoding="utf-8",
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

    def test_dark_theme_rejects_low_contrast_palette(self):
        css = '[data-md-color-scheme="slate"] { --md-default-bg-color: #0d1828; '
        css += '--vmd-paper: #14253a; --vmd-slate: #38516d; --vmd-green: #2d7659; '
        css += '--vmd-amber: #a96d19; --vmd-red: #a23b3b; --vmd-gold: #b48a3c; '
        css += '--vmd-ink-soft: #1c3552; }'
        self.assertGreaterEqual(len(validate_dark_theme_contrast(css)), 1)


if __name__ == "__main__":
    unittest.main()
