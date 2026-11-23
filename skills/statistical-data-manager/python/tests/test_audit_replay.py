import copy
import unittest

from _contracts import EXAMPLES, collect_errors, load_json, make_validator, read_jsonl
from replay import replay

STREAMS = EXAMPLES / "audit-streams"
EXPECTATIONS = load_json(STREAMS / "expectations.json")


def _actions() -> dict[str, dict]:
    docs = [load_json(p) for p in (EXAMPLES / "valid").glob("*action*.json")]
    return {d["action_id"]: d for d in docs}


class ReplayTests(unittest.TestCase):
    def test_every_stream_event_validates_against_the_schema(self) -> None:
        validator = make_validator("audit-event.schema.json")
        for path in sorted(STREAMS.glob("*.jsonl")):
            for event in read_jsonl(path):
                with self.subTest(stream=path.name, event=event["audit_event_id"]):
                    self.assertEqual(collect_errors(validator, event), [])

    def test_streams_match_expectations(self) -> None:
        streams = {p.name for p in STREAMS.glob("*.jsonl")}
        self.assertEqual(streams, set(EXPECTATIONS))
        for name, expected in EXPECTATIONS.items():
            with self.subTest(stream=name):
                result = replay(read_jsonl(STREAMS / name), actions=_actions())
                self.assertEqual(result.error_codes, sorted(expected["errors"]))
                self.assertEqual(result.warning_codes, sorted(expected["warnings"]))
                self.assertEqual(result.ok, not expected["errors"])

    def test_valid_lifecycle_replays_to_expected_current_state(self) -> None:
        result = replay(read_jsonl(STREAMS / "valid-lifecycle.jsonl"), actions=_actions())
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.states[("finding", "fnd_ws01")], "remediated")
        self.assertEqual(result.states[("finding", "fnd_dup01")], "needs_context")
        self.assertEqual(result.states[("action", "act_trim01")], "verified")
        self.assertEqual(result.states[("action", "act_trim02")], "rejected")

    def test_exact_duplicate_is_applied_once(self) -> None:
        events = read_jsonl(STREAMS / "valid-lifecycle.jsonl")
        base = replay(events, actions=_actions())
        dup = replay(events + [copy.deepcopy(events[3])], actions=_actions())
        self.assertTrue(dup.ok)
        self.assertEqual(dup.states, base.states)
        self.assertEqual(dup.event_count, base.event_count)
        self.assertEqual(dup.warning_codes, ["duplicate_event_ignored"])

    def test_event_order_in_the_file_does_not_change_the_outcome(self) -> None:
        events = read_jsonl(STREAMS / "valid-lifecycle.jsonl")
        shuffled = events[8:] + events[:8]
        self.assertEqual(replay(shuffled, actions=_actions()).states, replay(events, actions=_actions()).states)

    def test_documents_status_snapshots_are_not_authoritative(self) -> None:
        dup = load_json(EXAMPLES / "valid" / "finding.whitespace-observed.json")
        self.assertEqual(dup["status"], "observed")
        result = replay(read_jsonl(STREAMS / "valid-lifecycle.jsonl"), actions=_actions())
        self.assertEqual(result.states[("finding", dup["finding_id"])], "remediated")

    def test_manifest_must_agree_with_the_stream(self) -> None:
        path = STREAMS / "valid-lifecycle.jsonl"
        manifest = load_json(EXAMPLES / "valid" / "run-manifest.two-scopes.json")
        events, data = read_jsonl(path), path.read_bytes()
        self.assertTrue(replay(events, _actions(), manifest, data).ok)
        for key, code in (
            ("event_count", "manifest_event_count_mismatch"),
            ("last_sequence", "manifest_last_sequence_mismatch"),
            ("sha256", "manifest_sha256_mismatch"),
        ):
            with self.subTest(field=key):
                tampered = copy.deepcopy(manifest)
                tampered["audit_log"][key] = "f" * 64 if key == "sha256" else 99
                self.assertIn(code, replay(events, _actions(), tampered, data).error_codes)


if __name__ == "__main__":
    unittest.main()
