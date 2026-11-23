import unittest

from jsonschema import Draft202012Validator

from _contracts import (
    EXAMPLES,
    REGISTRY,
    SCHEMA_FILES,
    collect_errors,
    load_json,
    load_schema,
    make_validator,
    schema_for_example,
)

DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"
ID_BASE = "https://amphibiousintellect.org/suai/v0.2/"


def _contains_key(node, key: str) -> bool:
    if isinstance(node, dict):
        return key in node or any(_contains_key(v, key) for v in node.values())
    if isinstance(node, list):
        return any(_contains_key(v, key) for v in node)
    return False


class SchemaMetaTests(unittest.TestCase):
    def test_every_schema_is_draft_2020_12_and_valid(self) -> None:
        for relative in SCHEMA_FILES.values():
            with self.subTest(schema=relative):
                schema = load_schema(relative)
                self.assertEqual(schema["$schema"], DRAFT_2020_12)
                self.assertTrue(schema["$id"].startswith(ID_BASE))
                Draft202012Validator.check_schema(schema)

    def test_validator_factory_uses_draft_2020_12_with_format_checker(self) -> None:
        for relative in SCHEMA_FILES.values():
            with self.subTest(schema=relative):
                validator = make_validator(relative)
                self.assertIsInstance(validator, Draft202012Validator)
                self.assertIsNotNone(validator.format_checker)
        self.assertIn("date-time", Draft202012Validator.FORMAT_CHECKER.checkers)

    def test_format_checking_is_actually_enforced(self) -> None:
        sub = Draft202012Validator(
            {"$ref": ID_BASE + "common.schema.json#/$defs/timestamp"},
            registry=REGISTRY,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        )
        self.assertTrue(list(sub.iter_errors("yesterday")))
        self.assertFalse(list(sub.iter_errors("2026-11-23T12:00:00Z")))

    def test_schemas_do_not_use_oneof_or_anyof(self) -> None:
        # Flat error output keeps sidecar JSON paths predictable.
        for relative in SCHEMA_FILES.values():
            with self.subTest(schema=relative):
                schema = load_schema(relative)
                self.assertFalse(_contains_key(schema, "oneOf"))
                self.assertFalse(_contains_key(schema, "anyOf"))

    def test_object_schemas_forbid_additional_properties(self) -> None:
        for key in ("finding", "action", "approval", "engine-result", "audit-event", "run-manifest"):
            with self.subTest(schema=key):
                self.assertIs(load_schema(SCHEMA_FILES[key])["additionalProperties"], False)


class ValidExampleTests(unittest.TestCase):
    def test_valid_examples_validate(self) -> None:
        paths = sorted((EXAMPLES / "valid").glob("*.json"))
        self.assertGreaterEqual(len(paths), 15)
        for path in paths:
            with self.subTest(example=path.name):
                validator = make_validator(schema_for_example(path.name))
                self.assertEqual(collect_errors(validator, load_json(path)), [])

    def test_every_schema_has_a_valid_example(self) -> None:
        names = {p.name.split(".", 1)[0] for p in (EXAMPLES / "valid").glob("*.json")}
        for key in SCHEMA_FILES:
            if key != "common":
                self.assertIn(key, names)

    def test_trim_extension_examples_also_satisfy_the_base_action_schema(self) -> None:
        base = make_validator("action.schema.json")
        for path in (EXAMPLES / "valid").glob("trim-whitespace-action.*.json"):
            with self.subTest(example=path.name):
                self.assertEqual(collect_errors(base, load_json(path)), [])

    def test_engine_result_producer_is_a_participating_engine(self) -> None:
        for path in (EXAMPLES / "valid").glob("engine-result.*.json"):
            with self.subTest(example=path.name):
                doc = load_json(path)
                participants = {(e["name"], e["capability"]) for e in doc["engines"]}
                self.assertIn((doc["produced_by"]["name"], doc["produced_by"]["capability"]), participants)


class InvalidExampleTests(unittest.TestCase):
    def test_every_invalid_instance_has_a_sidecar_and_vice_versa(self) -> None:
        instances = {p.name for p in (EXAMPLES / "invalid").glob("*.json")}
        sidecars = {p.name for p in (EXAMPLES / "expected-failures").glob("*.json")}
        self.assertGreaterEqual(len(instances), 20)
        self.assertEqual(instances, sidecars)

    def test_invalid_instances_are_pure(self) -> None:
        for path in (EXAMPLES / "invalid").glob("*.json"):
            with self.subTest(example=path.name):
                self.assertFalse(_contains_key(load_json(path), "_why_invalid"))

    def test_expected_validator_and_json_path_are_reported_exactly(self) -> None:
        for path in sorted((EXAMPLES / "invalid").glob("*.json")):
            with self.subTest(example=path.name):
                sidecar = load_json(EXAMPLES / "expected-failures" / path.name)
                errors = collect_errors(make_validator(sidecar["schema"]), load_json(path))
                expected = sidecar["expected_errors"]
                self.assertEqual(len(errors), len(expected), f"unexpected error set: {errors}")
                remaining = list(errors)
                for want in expected:
                    match = next(
                        (
                            e
                            for e in remaining
                            if e["validator"] == want["validator"]
                            and e["json_path"] == want["json_path"]
                            and want.get("message_contains", "") in e["message"]
                        ),
                        None,
                    )
                    self.assertIsNotNone(match, f"missing expected error {want} in {errors}")
                    remaining.remove(match)

    def test_required_negative_cases_are_covered(self) -> None:
        names = {p.stem for p in (EXAMPLES / "invalid").glob("*.json")}
        for required in (
            "approval.finding-id-only",
            "approval.decision-needs-context",
            "approval.deferred-without-context",
            "approval.missing-supersedes-key",
            "approval.bad-timestamp",
            "engine-result.native-two-engines",
            "engine-result.collaborative-one-engine",
            "action.metadata-only-without-approval",
            "action.data-mutation-without-postconditions",
            "action.full-values-without-rationale",
            "trim-whitespace-action.counts-only-policy",
            "finding.non-blocking-without-rationale",
            "finding.malformed-id",
            "finding.extra-property",
            "run-manifest.releasable-with-blockers",
        ):
            self.assertIn(required, names)


if __name__ == "__main__":
    unittest.main()
