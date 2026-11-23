import copy
import unittest

from _contracts import EXAMPLES, collect_errors, load_json, make_validator

TRIM = "extensions/trim-whitespace.action.schema.json"
VALID = EXAMPLES / "valid"


class BaseActionGeneralityTests(unittest.TestCase):
    def test_non_mutating_action_is_valid_without_approval(self) -> None:
        action = load_json(VALID / "action.review-none.json")
        self.assertEqual(action["mutation_class"], "none")
        self.assertFalse(action["approval_required"])
        self.assertEqual(collect_errors(make_validator("action.schema.json"), action), [])

    def test_metadata_only_action_is_valid_and_requires_approval(self) -> None:
        action = load_json(VALID / "action.metadata-only.json")
        validator = make_validator("action.schema.json")
        self.assertEqual(collect_errors(validator, action), [])
        action["approval_required"] = False
        self.assertTrue(collect_errors(validator, action))

    def test_base_schema_does_not_hard_code_trim_whitespace(self) -> None:
        action = copy.deepcopy(load_json(VALID / "action.metadata-only.json"))
        action["action_type"] = "some_future_action"
        self.assertEqual(collect_errors(make_validator("action.schema.json"), action), [])

    def test_trim_extension_rejects_other_action_types_and_classes(self) -> None:
        validator = make_validator(TRIM)
        trim = load_json(VALID / "trim-whitespace-action.both-sides.json")
        for field, value in (("action_type", "other_action"), ("mutation_class", "metadata_only")):
            with self.subTest(field=field):
                changed = {**trim, field: value}
                self.assertIn(field, {e["json_path"].removeprefix("$.") for e in collect_errors(validator, changed)})


class ValueCapturePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.trim = load_json(VALID / "trim-whitespace-action.both-sides.json")
        self.ref = {"row_position": 1, "column": "visit"}
        self.sha = "a" * 64

    def _with(self, policy: str, **affected) -> dict:
        doc = copy.deepcopy(self.trim)
        doc["value_capture_policy"] = policy
        doc["affected"].update(affected)
        return doc

    def test_hashes_policy_needs_hashes_method_and_salt_policy(self) -> None:
        validator = make_validator(TRIM)
        complete = self._with(
            "hashes",
            value_hashes=[{"ref": self.ref, "before_sha256": self.sha, "after_sha256": "b" * 64}],
            hash_method="hmac_sha256", hash_salt_policy="keyed",
        )
        self.assertEqual(collect_errors(validator, complete), [])
        partial = self._with("hashes", value_hashes=complete["affected"]["value_hashes"])
        self.assertTrue(collect_errors(validator, partial))

    def test_redacted_preview_policy_is_supported_without_raw_values(self) -> None:
        doc = self._with(
            "redacted_preview",
            redacted_previews=[{"ref": self.ref, "before_preview": "V*** ", "after_preview": "V***", "redaction": "mask_after_first_char"}],
        )
        self.assertEqual(collect_errors(make_validator(TRIM), doc), [])

    def test_raw_values_are_never_required_by_default_policies(self) -> None:
        # The shipped trim example captures only record references.
        self.assertNotIn("full_values", self.trim["affected"])
        self.assertEqual(self.trim["value_capture_policy"], "record_references")
        self.assertEqual(collect_errors(make_validator(TRIM), self.trim), [])

    def test_trim_must_identify_cells_even_under_other_policies(self) -> None:
        doc = self._with(
            "hashes",
            value_hashes=[{"ref": self.ref, "before_sha256": self.sha, "after_sha256": self.sha}],
            hash_method="hmac_sha256", hash_salt_policy="keyed",
        )
        del doc["affected"]["record_references"]
        paths = {e["json_path"] for e in collect_errors(make_validator(TRIM), doc)}
        self.assertIn("$.affected", paths)


if __name__ == "__main__":
    unittest.main()
