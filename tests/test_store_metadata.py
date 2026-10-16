import json
import unittest
from pathlib import Path


METADATA = json.loads(
    (Path(__file__).parents[1] / "docs" / "store_metadata.json").read_text(encoding="utf-8")
)


class StoreMetadataTests(unittest.TestCase):
    def test_store_copy_fits_console_limits(self):
        apple = METADATA["apple"]
        play = METADATA["google_play"]
        self.assertLessEqual(len(apple["name"]), 30)
        self.assertLessEqual(len(apple["subtitle"]), 30)
        self.assertLessEqual(len(apple["promotional_text"]), 170)
        self.assertLessEqual(len(apple["keywords"]), 100)
        self.assertLessEqual(len(apple["description"]), 4000)
        self.assertLessEqual(len(play["app_name"]), 30)
        self.assertLessEqual(len(play["short_description"]), 80)
        self.assertLessEqual(len(play["full_description"]), 4000)

    def test_copy_preserves_product_disclaimer_and_review_paths(self):
        combined = " ".join(
            [METADATA["apple"]["description"], METADATA["google_play"]["full_description"], METADATA["review"]["notes"]]
        ).lower()
        self.assertGreaterEqual(combined.count("not guarantee"), 3)
        for screen in ("radar", "pipeline", "insights", "profile", "settings"):
            self.assertIn(screen, METADATA["review"]["notes"].lower())
        self.assertIn("permanent account deletion", METADATA["review"]["notes"].lower())

    def test_owner_only_values_cannot_be_mistaken_for_credentials_or_live_urls(self):
        self.assertEqual(METADATA["status"], "DRAFT - OWNER REVIEW REQUIRED")
        self.assertTrue(METADATA["do_not_submit_until"])
        for section in ("apple", "google_play"):
            for key, value in METADATA[section].items():
                if key.endswith("url") or key == "website":
                    self.assertTrue(value.startswith("[OWNER:"), f"{section}.{key} must remain an owner gate")
        self.assertTrue(METADATA["review"]["account_email"].startswith("[OWNER:"))
        self.assertTrue(METADATA["review"]["account_password"].startswith("[OWNER:"))


if __name__ == "__main__":
    unittest.main()
