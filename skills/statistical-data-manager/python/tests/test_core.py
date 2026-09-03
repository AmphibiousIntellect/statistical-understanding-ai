from pathlib import Path
import unittest

import pandas as pd

from suai_data_manager import inspect, profile


FIXTURE = Path(__file__).parents[2] / "fixtures" / "duplicate_rows.csv"


class CoreTests(unittest.TestCase):
    def test_profile_reports_shared_fixture(self) -> None:
        data = pd.read_csv(FIXTURE)
        result = profile(data)

        self.assertEqual(result["row_count"], 4)
        self.assertEqual(result["column_count"], 3)
        self.assertEqual(result["columns"], ["participant_id", "visit", "value"])
        self.assertEqual(result["missing_count"]["value"], 2)
        self.assertEqual(result["duplicate_row_count"], 2)

    def test_inspect_proposes_review_without_mutating(self) -> None:
        data = pd.read_csv(FIXTURE)
        before = data.copy(deep=True)

        result = inspect(data)

        pd.testing.assert_frame_equal(data, before)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].code, "duplicate_rows")
        self.assertEqual(result.findings[0].status, "needs_context")


if __name__ == "__main__":
    unittest.main()
