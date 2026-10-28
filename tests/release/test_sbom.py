import importlib.util
import json
import sys
import unittest
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location("vmd_sbom", ROOT / "tools/release/build_sbom.py")
SBOM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SBOM)


class SbomTest(unittest.TestCase):
    def test_serial_number_is_a_valid_stable_uuid_and_timestamp_is_release_bound(self):
        first = SBOM.build_document()
        second = SBOM.build_document()
        serial = first["serialNumber"]

        self.assertTrue(serial.startswith("urn:uuid:"))
        UUID(serial.removeprefix("urn:uuid:"))
        self.assertEqual(serial, second["serialNumber"])
        self.assertEqual(first["metadata"]["timestamp"], second["metadata"]["timestamp"])
        release_date = json.loads((ROOT / "manifests/release.json").read_text(encoding="utf-8"))["generated_at"]
        self.assertEqual(first["metadata"]["timestamp"], f"{release_date}T00:00:00Z")

    def test_release_workflow_never_replaces_existing_assets(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertNotIn("--clobber", workflow)
        self.assertIn("published assets are immutable", workflow)
        self.assertIn('exit 0', workflow)


if __name__ == "__main__":
    unittest.main()
