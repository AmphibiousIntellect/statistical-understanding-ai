import copy
import re
import unittest

from _contracts import REPO_ROOT, V02, EXAMPLES, action_digest, load_json, load_schema
from replay import check_approval_chain

TABLE = load_json(V02 / "state-transitions.json")
ADR = REPO_ROOT / "docs" / "decisions" / "0002-routing-provenance-and-state-model.md"


def _adr_rows() -> dict[str, tuple[str | None, str, set[str]]]:
    rows: dict[str, tuple[str | None, str, set[str]]] = {}
    for line in ADR.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*((?:F|A)\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if match:
            ident, src, dst, events = match.groups()
            rows[ident] = (None if src == "∅" else src.strip("` "), dst.strip("` "), set(re.findall(r"`([a-z_]+)`", events)))
    return rows


class TableAgreesWithSchemasTests(unittest.TestCase):
    def test_state_enums_match_common_schema(self) -> None:
        defs = load_schema("common.schema.json")["$defs"]
        self.assertEqual(TABLE["finding"]["states"], defs["finding_state"]["enum"])
        self.assertEqual(TABLE["action"]["states"], defs["action_state"]["enum"])
        self.assertEqual(TABLE["approval_decisions"], defs["approval_decision"]["enum"])

    def test_event_types_match_audit_event_schema(self) -> None:
        audit = load_schema("audit-event.schema.json")
        self.assertEqual(TABLE["event_types"], audit["properties"]["event_type"]["enum"])

    def test_transitions_only_use_declared_states_and_events(self) -> None:
        for machine in ("finding", "action"):
            states = set(TABLE[machine]["states"])
            for t in TABLE[machine]["transitions"]:
                with self.subTest(transition=t["id"]):
                    self.assertTrue(t["from"] is None or t["from"] in states)
                    self.assertIn(t["to"], states)
                    self.assertTrue(set(t["event_types"]) <= set(TABLE["event_types"]))

    def test_needs_context_is_not_an_approval_decision(self) -> None:
        self.assertNotIn("needs_context", TABLE["approval_decisions"])
        self.assertIn("needs_context", TABLE["finding"]["states"])

    def test_adr_table_matches_machine_readable_table(self) -> None:
        rows = _adr_rows()
        expected = {
            t["id"]: (t["from"], t["to"], set(t["event_types"]))
            for machine in ("finding", "action")
            for t in TABLE[machine]["transitions"]
        }
        self.assertEqual(rows, expected)


class TransitionLegalityTests(unittest.TestCase):
    def _legal(self, machine: str, src: str | None, dst: str) -> bool:
        return any(t["from"] == src and t["to"] == dst for t in TABLE[machine]["transitions"])

    def test_illegal_pairs_are_absent(self) -> None:
        for machine, src, dst in (
            ("action", "proposed", "applied"),
            ("action", None, "applied"),
            ("action", "rejected", "approved"),
            ("action", "applied", "approved"),
            ("action", "verified", "applied"),
            ("action", "superseded", "approved"),
            ("finding", "observed", "remediated"),
            ("finding", None, "proposed"),
            ("finding", "resolved", "proposed"),
        ):
            with self.subTest(pair=(machine, src, dst)):
                self.assertFalse(self._legal(machine, src, dst))

    def test_legal_pairs_include_deferral_round_trip_and_explicit_proposal(self) -> None:
        self.assertTrue(self._legal("action", "deferred", "approved"))
        self.assertTrue(self._legal("action", "approved", "rejected"))
        self.assertTrue(self._legal("finding", "needs_context", "proposed"))
        self.assertTrue(self._legal("finding", "observed", "proposed"))

    def test_terminal_action_states_have_no_outgoing_transitions(self) -> None:
        for state in TABLE["action"]["terminal_states"]:
            with self.subTest(state=state):
                self.assertFalse([t for t in TABLE["action"]["transitions"] if t["from"] == state])

    def test_action_creation_does_not_move_a_finding(self) -> None:
        for t in TABLE["finding"]["transitions"]:
            self.assertNotIn("action_proposed", t["event_types"])


class ApprovalChainTests(unittest.TestCase):
    def setUp(self) -> None:
        valid = EXAMPLES / "valid"
        self.action = load_json(valid / "trim-whitespace-action.both-sides.json")
        self.deferred = load_json(valid / "approval.deferred.json")
        self.approved = load_json(valid / "approval.approved-after-deferral.json")

    def test_deferred_then_approved_under_same_action_id_and_digest(self) -> None:
        self.assertEqual(self.approved["action_id"], self.deferred["action_id"])
        self.assertEqual(self.approved["action_digest"], action_digest(self.action))
        self.assertEqual(check_approval_chain(self.action, [self.deferred, self.approved]), [])

    def test_digest_mismatch_is_reported(self) -> None:
        changed = copy.deepcopy(self.action)
        changed["title"] = "changed after approval"
        self.assertIn("digest_mismatch", check_approval_chain(changed, [self.deferred, self.approved]))

    def test_later_approval_must_supersede_the_head(self) -> None:
        orphan = {**self.approved, "supersedes_approval_id": None}
        self.assertIn("missing_supersedes", check_approval_chain(self.action, [self.deferred, orphan]))
        wrong = {**self.approved, "supersedes_approval_id": "apr_099"}
        self.assertIn("supersedes_not_head", check_approval_chain(self.action, [self.deferred, wrong]))

    def test_fork_is_reported(self) -> None:
        fork = {**self.approved, "approval_id": "apr_004", "decision": "rejected"}
        self.assertIn("approval_fork", check_approval_chain(self.action, [self.deferred, self.approved, fork]))

    def test_illegal_decision_changes_are_reported(self) -> None:
        again = {**self.approved, "approval_id": "apr_005", "supersedes_approval_id": "apr_002", "decision": "approved"}
        self.assertIn("illegal_decision_change", check_approval_chain(self.action, [self.deferred, self.approved, again]))
        revoked = {**again, "decision": "rejected"}
        reapprove = {**self.approved, "approval_id": "apr_007", "supersedes_approval_id": "apr_005", "decision": "approved"}
        self.assertIn(
            "illegal_decision_change",
            check_approval_chain(self.action, [self.deferred, self.approved, revoked, reapprove]),
        )
        self.assertEqual(
            check_approval_chain(self.action, [self.deferred, {**self.approved, "decision": "rejected"}]), []
        )

    def test_first_approval_may_not_supersede_anything(self) -> None:
        self.assertIn("first_approval_supersedes_unknown", check_approval_chain(self.action, [self.approved]))


if __name__ == "__main__":
    unittest.main()
