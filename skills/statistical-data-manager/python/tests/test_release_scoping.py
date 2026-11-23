import copy
import unittest

from _contracts import EXAMPLES, load_json, read_jsonl
from replay import evaluate_release, replay

SCOPES = ["scp_main", "scp_other"]
VALID = EXAMPLES / "valid"
STREAMS = EXAMPLES / "audit-streams"


def _doc(name: str) -> dict:
    return load_json(VALID / name)


def _actions() -> dict[str, dict]:
    return {d["action_id"]: d for d in (load_json(p) for p in VALID.glob("*action*.json"))}


def _run_actions() -> list[dict]:
    """The actions that belong to the example run (the trim alternatives)."""
    return [a for a in _actions().values() if a["action_id"] in {"act_trim01", "act_trim02"}]


class ReleaseScopingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events = read_jsonl(STREAMS / "valid-lifecycle.jsonl")
        self.replayed = replay(self.events, actions=_actions())
        self.dup = _doc("finding.duplicate-needs-context.json")
        self.ws = _doc("finding.whitespace-observed.json")

    def test_needs_context_finding_blocks_only_the_scope_it_affects(self) -> None:
        blockers = evaluate_release(SCOPES, [self.dup, self.ws], _run_actions(), self.replayed, self.events)
        self.assertEqual(blockers, {"scp_main": [f"finding_needs_context:{self.dup['finding_id']}"], "scp_other": []})

    def test_manifest_example_agrees_with_evaluated_blockers(self) -> None:
        manifest = _doc("run-manifest.two-scopes.json")
        blockers = evaluate_release(SCOPES, [self.dup, self.ws], _run_actions(), self.replayed, self.events)
        for scope in manifest["release_scopes"]:
            declared = sorted(f"{b['blocker_code']}:{b['finding_id']}" for b in scope["release_blockers"])
            self.assertEqual(declared, blockers[scope["release_scope_id"]])
            self.assertEqual(scope["release_status"], "blocked" if declared else "releasable")

    def test_non_blocking_declaration_needs_an_audit_event(self) -> None:
        relaxed = copy.deepcopy(self.dup)
        relaxed.update(release_blocking=False, materiality_rationale="Rows are known repeat visits; no output depends on uniqueness.")
        undeclared = evaluate_release(SCOPES, [relaxed], [], self.replayed, self.events)
        self.assertEqual(undeclared["scp_main"], ["undeclared_materiality:fnd_dup01"])

        declared_event = {
            "schema_version": "0.2", "audit_event_id": "evt_018", "run_id": "run_demo01", "sequence": 18,
            "occurred_at": "2026-11-23T12:18:00Z", "actor": {"type": "human", "id": "analyst_01"},
            "event_type": "release_materiality_declared", "state_machine": None, "previous_state": None,
            "new_state": None, "engine": None, "input_artifacts": [], "output_artifacts": [],
            "finding_id": "fnd_dup01", "rationale": relaxed["materiality_rationale"],
        }
        events = self.events + [declared_event]
        replayed = replay(events, actions=_actions())
        self.assertEqual(evaluate_release(SCOPES, [relaxed], [], replayed, events), {"scp_main": [], "scp_other": []})

    def test_open_action_blocks_only_its_own_scope(self) -> None:
        action = copy.deepcopy(_doc("action.review-none.json"))
        action.update(action_id="act_scoped01", affected_release_scope=["scp_other"])
        blockers = evaluate_release(SCOPES, [], [action], self.replayed, self.events)
        self.assertEqual(blockers, {"scp_main": [], "scp_other": ["action_open:act_scoped01"]})

    def test_non_blocking_action_does_not_block(self) -> None:
        meta = _doc("action.metadata-only.json")
        self.assertEqual(evaluate_release(SCOPES, [], [meta], self.replayed, self.events), {s: [] for s in SCOPES})

    def test_run_wide_failures_block_every_scope(self) -> None:
        broken = replay(read_jsonl(STREAMS / "sequence-gap.jsonl"), actions=_actions())
        blockers = evaluate_release(SCOPES, [], [], broken, [])
        self.assertTrue(all(codes == ["run_wide:replay_failed"] for codes in blockers.values()))
        failed = evaluate_release(SCOPES, [], [], self.replayed, self.events, verification_status="failed")
        self.assertTrue(all(codes == ["run_wide:verification_not_passed"] for codes in failed.values()))


if __name__ == "__main__":
    unittest.main()
