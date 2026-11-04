"""Exercise security checks against complete workflow files."""

import contextlib
import io
import shutil
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[2] / "tools" / "validate"))
import validate_workflows


class WorkflowPolicyTests(unittest.TestCase):
    def check_reference(self, replacement: str | None) -> tuple[int, str]:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = root / ".github" / "workflows"
            shutil.copytree(validate_workflows.WORKFLOWS, workflows)
            shutil.copy(validate_workflows.ROOT / ".github/dependabot.yml", root / ".github")
            if replacement:
                path = workflows / "browser-webkit.yml"
                text = path.read_text(encoding="utf-8")
                text = text.replace(
                    "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1",
                    replacement,
                )
                path.write_text(text, encoding="utf-8")
            output = io.StringIO()
            with patch.object(validate_workflows, "ROOT", root), patch.object(
                validate_workflows, "WORKFLOWS", workflows
            ), contextlib.redirect_stdout(output):
                result = validate_workflows.main()
            return result, output.getvalue()

    def test_pinned_actions_and_local_reusable_workflows_pass(self):
        self.assertEqual(self.check_reference(None)[0], 0)

    def test_floating_step_action_is_rejected(self):
        result, output = self.check_reference("actions/setup-node@v7")
        self.assertEqual(result, 1)
        self.assertIn("action sem SHA completa", output)

    def test_step_action_outside_allowlist_is_rejected(self):
        result, output = self.check_reference("unknown/setup-node@" + "a" * 40)
        self.assertEqual(result, 1)
        self.assertIn("action fora da allowlist oficial", output)
