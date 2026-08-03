import copy
import unittest

from manifestlens.core import DEMO, analyze


class ValidationStatusFailOpenTest(unittest.TestCase):
    """analyze() previously treated an ABSENT validation_status field the
    same as an empty one, defaulting to []. That meant valid=True even
    when no cryptographic validation had actually happened -- any caller
    (or attacker) could mark an unverified manifest "valid" by simply
    omitting the field from the JSON payload sent to /api/analyze.
    Separately, has_hard_binding only checked for the PRESENCE of a hash
    assertion label, not whether that specific binding check passed, so
    it stayed True even when validation_status explicitly reported a
    hash mismatch (a tampering signal)."""

    def test_missing_validation_status_is_not_treated_as_valid(self):
        payload = copy.deepcopy(DEMO)
        del payload["validation_status"]
        result = analyze(payload)
        self.assertFalse(result["valid"])
        self.assertFalse(result["validation_status_present"])

    def test_missing_validationstatus_camelcase_is_not_treated_as_valid(self):
        payload = copy.deepcopy(DEMO)
        del payload["validation_status"]
        payload["activeManifest"] = payload.pop("active_manifest")
        result = analyze(payload)
        self.assertFalse(result["valid"])

    def test_explicit_empty_validation_status_is_still_valid(self):
        """An explicitly empty list (the demo's own convention) means
        'checked, no errors found' and must still report valid."""
        payload = copy.deepcopy(DEMO)
        payload["validation_status"] = []
        result = analyze(payload)
        self.assertTrue(result["valid"])
        self.assertTrue(result["validation_status_present"])

    def test_hash_mismatch_clears_has_hard_binding_even_though_label_is_present(self):
        payload = copy.deepcopy(DEMO)
        payload["validation_status"] = [{"code": "assertion.dataHash.mismatch", "success": False}]
        result = analyze(payload)
        self.assertFalse(result["valid"])
        self.assertFalse(result["has_hard_binding"])

    def test_unrelated_validation_error_does_not_clear_has_hard_binding(self):
        """A validation error unrelated to hashing/binding shouldn't
        falsely zero out a genuinely present, unaffected hard binding."""
        payload = copy.deepcopy(DEMO)
        payload["validation_status"] = [{"code": "signingCredential.expired", "success": False}]
        result = analyze(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(result["has_hard_binding"])

    def test_demo_still_reports_valid_with_hard_binding(self):
        result = analyze(DEMO)
        self.assertTrue(result["valid"])
        self.assertTrue(result["has_hard_binding"])


if __name__ == "__main__":
    unittest.main()
