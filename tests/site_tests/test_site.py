import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]


class SiteContractTest(unittest.TestCase):
    def test_site_contract_and_brand_assets_exist(self):
        self.assertTrue((ROOT / "mkdocs.yml").is_file())
        self.assertTrue((ROOT / "site_docs/index.md").is_file())
        self.assertTrue((ROOT / "site_docs/assets/brand-mark.svg").is_file())
        self.assertTrue((ROOT / "site_docs/stylesheets/extra.css").is_file())
        catalog = ROOT / "site_docs/generated/catalog.md"
        self.assertTrue(catalog.is_file())
        self.assertIn("Catálogo da legislação", catalog.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
