import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PRIVACY = (ROOT / "docs/PRIVACY_POLICY_DRAFT.md").read_text(encoding="utf-8")
TERMS = (ROOT / "docs/TERMS_OF_USE_DRAFT.md").read_text(encoding="utf-8")


class LegalReadinessTests(unittest.TestCase):
    def test_drafts_cannot_be_mistaken_for_approved_policies(self):
        for document in (PRIVACY, TERMS):
            self.assertIn("Not approved for publication", document)
            self.assertIn("[EFFECTIVE DATE]", document)
            self.assertIn("[LEGAL ENTITY", document)

    def test_privacy_draft_matches_the_code_derived_data_inventory(self):
        for item in ("email address", "company name", "pipeline", "revenue target", "Supabase"):
            self.assertIn(item, PRIVACY)
        self.assertIn("does not sell personal information", PRIVACY)
        self.assertIn("permanent account deletion", PRIVACY)

    def test_terms_preserve_the_core_product_disclaimer(self):
        terms = " ".join(TERMS.split())
        for item in ("indicators only", "do not confirm", "Users must verify", "Australian Consumer Law"):
            self.assertIn(item, terms)


if __name__ == "__main__":
    unittest.main()
