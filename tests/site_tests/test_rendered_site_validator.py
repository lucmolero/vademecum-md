import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools" / "validate"))
from validate_site import validate  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
