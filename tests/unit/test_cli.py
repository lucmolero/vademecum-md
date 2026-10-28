import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vademecum_md.cli import find_workspace_root, main  # noqa: E402


class CliContractTest(unittest.TestCase):
    def test_cli_exposes_operational_commands(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run([sys.executable, "-m", "vademecum_md.cli", "--help"], cwd=ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("acquire", "normalize", "audit", "graph", "site", "release"):
            self.assertIn(command, result.stdout)

    def test_cli_finds_checkout_from_nested_path(self):
        self.assertEqual(find_workspace_root(ROOT / "src" / "vademecum_md"), ROOT)

    @patch("vademecum_md.cli.runpy.run_path")
    @patch("vademecum_md.cli._workspace_root", return_value=ROOT)
    def test_cli_resolves_command_from_discovered_checkout(self, _workspace_root, run_path):
        self.assertEqual(main(["site", "--dry-run"]), 0)
        run_path.assert_called_once_with(str(ROOT / "tools/site/build_site.py"), run_name="__main__")

    def test_cli_does_not_treat_unrelated_directory_as_checkout(self):
        with TemporaryDirectory() as temporary_directory:
            self.assertIsNone(find_workspace_root(Path(temporary_directory)))

    def test_operational_command_explains_checkout_requirement(self):
        error = io.StringIO()
        with patch("vademecum_md.cli._workspace_root", return_value=None):
            with redirect_stderr(error), self.assertRaises(SystemExit) as raised:
                main(["site"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("exigem um checkout", error.getvalue())
        self.assertIn("--version funciona sem checkout", error.getvalue())


if __name__ == "__main__":
    unittest.main()
