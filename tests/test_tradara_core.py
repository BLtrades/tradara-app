import unittest

import pandas as pd

from tradara_core import fit_boost, opportunity_rows, preference_list, to_datetime


NOW = pd.Timestamp("2026-09-29T00:00:00")


def months_ago(months):
    return int((NOW - pd.Timedelta(days=months * 30.44)).timestamp() * 1000)


def feature(description, decision_date, decision="Approved", number="DEV-1"):
    return {"attributes": {
        "description": description,
        "decisiondate": decision_date,
        "decision": decision,
        "developmentnumber": number,
        "applicationurl": "https://example.test/project",
    }}


class OpportunityScoringTests(unittest.TestCase):
    def test_trade_window_scores_approved_electrical_project(self):
        data = {"features": [feature("New commercial building", months_ago(5))]}
        result = opportunity_rows(data, ["Electrician"], now=NOW)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["Action"], "CONTACT NOW — trade window")
        self.assertEqual(result.iloc[0]["Score"], 84)
        self.assertEqual(result.iloc[0]["Development"], "DEV-1")

    def test_pre_position_and_late_windows_are_distinct(self):
        early = opportunity_rows(
            {"features": [feature("New dwelling", months_ago(1))]},
            ["Electrician"], now=NOW,
        )
        late = opportunity_rows(
            {"features": [feature("New dwelling", months_ago(13))]},
            ["Electrician"], now=NOW,
        )

        self.assertEqual(early.iloc[0]["Action"], "CONTACT NOW — pre-position")
        self.assertEqual(late.iloc[0]["Action"], "LATE WINDOW — verify")

    def test_unknown_or_malformed_source_data_is_ignored_safely(self):
        data = {"features": [None, "bad", {"attributes": None}, feature("No matching work", "bad-date")]}
        result = opportunity_rows(data, ["Unknown trade", "Electrician"], now=NOW)

        self.assertTrue(result.empty)
        self.assertEqual(list(result.columns)[0], "Score")
        self.assertTrue(pd.isna(to_datetime("bad-date")))

    def test_missing_date_requires_timing_verification(self):
        data = {"features": [feature("Apartment building", None)]}
        result = opportunity_rows(data, ["HVAC"], now=NOW)

        self.assertEqual(result.iloc[0]["Action"], "VERIFY TIMING")

    def test_company_fit_boost_and_comma_preferences(self):
        row = {
            "Description": "New commercial building",
            "Trade": "Electrician",
            "Action": "CONTACT NOW — trade window",
        }
        profile = {
            "preferred_project_types": "commercial, office",
            "preferred_trades": ["Electrician"],
        }

        self.assertEqual(preference_list(profile, "preferred_project_types"), ["commercial", "office"])
        self.assertEqual(fit_boost(row, profile), (21, "preferred project type, core company trade, good timing"))


if __name__ == "__main__":
    unittest.main()
