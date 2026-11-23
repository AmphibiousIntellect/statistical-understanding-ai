"""The implemented v0.1 contract is untouched and the current engines still satisfy it."""

import unittest

import pandas as pd
from jsonschema import Draft202012Validator

from _contracts import FIXTURES, REPO_ROOT, V02, load_json
from suai_data_manager import inspect

ROOT_SCHEMAS = REPO_ROOT / "schemas"
V01 = ("finding", "approval", "run-manifest")


def _validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(
        load_json(ROOT_SCHEMAS / f"{name}.schema.json"), format_checker=Draft202012Validator.FORMAT_CHECKER
    )


class V01UnchangedTests(unittest.TestCase):
    def test_v01_schemas_exist_at_the_root_and_are_not_the_v02_drafts(self) -> None:
        for name in V01:
            with self.subTest(schema=name):
                schema = load_json(ROOT_SCHEMAS / f"{name}.schema.json")
                self.assertNotIn("/v0.2/", schema["$id"])
                self.assertNotIn("schema_version", schema.get("properties", {}))
                Draft202012Validator.check_schema(schema)

    def test_v01_keeps_its_distinguishing_fields(self) -> None:
        finding = load_json(ROOT_SCHEMAS / "finding.schema.json")
        approval = load_json(ROOT_SCHEMAS / "approval.schema.json")
        manifest = load_json(ROOT_SCHEMAS / "run-manifest.schema.json")
        self.assertIn("proposed_action", finding["properties"])
        self.assertIn("finding_code", approval["properties"])
        self.assertEqual(approval["properties"]["decision"]["enum"], ["approved", "rejected", "needs_context"])
        self.assertEqual(manifest["properties"]["engine"]["enum"], ["r", "python", "cross-language"])

    def test_current_python_findings_still_satisfy_the_v01_finding_schema(self) -> None:
        result = inspect(pd.read_csv(FIXTURES / "duplicate_rows.csv")).to_dict()
        validator = _validator("finding")
        self.assertEqual(len(result["findings"]), 1)
        for finding in result["findings"]:
            self.assertEqual(list(validator.iter_errors(finding)), [])

    def test_v02_files_live_only_under_the_v02_directory(self) -> None:
        self.assertEqual(sorted(p.name for p in ROOT_SCHEMAS.glob("*.json")), [f"{n}.schema.json" for n in sorted(V01)])
        self.assertTrue((V02 / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
