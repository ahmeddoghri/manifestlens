import json
import unittest
from pathlib import Path

from manifestlens.core import DEMO, analyze, inspect_asset


class ManifestLensTest(unittest.TestCase):
    def test_demo_summarizes_provenance_chain(self):
        result = analyze(DEMO)
        self.assertTrue(result["valid"])
        self.assertTrue(result["has_hard_binding"])
        self.assertEqual(result["ingredient_count"], 1)
        self.assertIn("c2pa.cropped", result["actions"])

    def test_reads_committed_c2pa_asset(self):
        result = inspect_asset(str(Path(__file__).parents[1] / "demo" / "C_with_CAWG_data.jpg"))
        self.assertTrue(result["summary"]["active_manifest"])
        self.assertGreaterEqual(result["summary"]["assertion_labels"].__len__(), 1)


if __name__ == "__main__":
    unittest.main()
