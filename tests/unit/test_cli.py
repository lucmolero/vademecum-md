import subprocess
import sys
import unittest
import os
from pathlib import Path

ROOT = Path(__file__).parents[2]


class CliContractTest(unittest.TestCase):
    def test_cli_exposes_operational_commands(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run([sys.executable, "-m", "vademecum_md.cli", "--help"], cwd=ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("acquire", "normalize", "audit", "graph", "site", "release"):
            self.assertIn(command, result.stdout)


if __name__ == "__main__":
    unittest.main()
