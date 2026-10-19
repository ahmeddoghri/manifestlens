"""The claim that matters: a modified asset must stop validating.

Everything else this tool reports is bookkeeping. These tests run against the
committed, really-signed C2PA sample and a byte-flipped copy of it, through
the official SDK.
"""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from manifestlens.core import inspect_asset

ASSET = Path(__file__).parents[1] / "demo" / "C_with_CAWG_data.jpg"


def _tampered(directory: str) -> str:
    data = bytearray(ASSET.read_bytes())
    start = int(len(data) * 0.85)
    for index in range(start, start + 400):
        data[index] ^= 0x5A
    path = Path(directory) / "tampered.jpg"
    path.write_bytes(bytes(data))
    return str(path)


class RealAssetTamperTest(unittest.TestCase):
    def test_the_untouched_signed_asset_validates_and_is_hard_bound(self):
        summary = inspect_asset(str(ASSET))["summary"]
        self.assertTrue(summary["valid"])
        self.assertEqual(summary["validation_errors"], [])
        # Label-only detection reported no binding here: a real asset records
        # its hard binding as a success code, never as an assertion label.
        self.assertTrue(summary["has_hard_binding"])

    def test_an_untrusted_signer_is_surfaced_rather_than_passed_over(self):
        summary = inspect_asset(str(ASSET))["summary"]
        # This sample is signed with a test certificate. Integrity holds, the
        # signer is not trusted, and the report has to say both.
        self.assertFalse(summary["signer_trusted"])
        codes = {item["code"] for item in summary["validation_warnings"]}
        self.assertIn("signingCredential.untrusted", codes)

    def test_flipping_bytes_in_the_image_breaks_the_hard_binding(self):
        with TemporaryDirectory() as directory:
            summary = inspect_asset(_tampered(directory))["summary"]
        self.assertFalse(summary["valid"])
        self.assertFalse(summary["has_hard_binding"])
        codes = {item["code"] for item in summary["validation_errors"]}
        self.assertIn("assertion.dataHash.mismatch", codes)


if __name__ == "__main__":
    unittest.main()
