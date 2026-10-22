import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]


class GraphContractTest(unittest.TestCase):
    def test_confidence_is_calibrated_and_inverse_state_is_explicit(self):
        rows = [json.loads(line) for line in (ROOT / "bases/derived/relacoes/normative-graph.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertTrue(rows)
        self.assertTrue(all(row.get("metodo_analise") for row in rows))
        self.assertTrue(all(row.get("status_relacao_inversa") in {"complete", "excluded_by_policy"} for row in rows))
        self.assertFalse(any(row.get("confianca") == "alta" and (not row.get("dispositivo") or not row.get("data_efeito")) for row in rows))


if __name__ == "__main__":
    unittest.main()
