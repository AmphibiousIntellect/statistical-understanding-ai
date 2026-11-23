"""Disagreement-path contract, exercised with a deterministic scripted double.

No pandas or R parsing is involved, so these tests cannot change with library
versions. Real cross-engine parsing cases are separate future work.
"""

import copy
import unittest

from _contracts import collect_errors, make_validator
from replay import evaluate_release, replay
from validator_double import RUN_ID, ScriptedEngine, build_disagreement_finding

SCOPES = ["scp_main", "scp_other"]
INDEPENDENT = "independent_validation"


def _event(seq: int, etype: str, actor: dict, **kw) -> dict:
    base = {
        "schema_version": "0.2", "audit_event_id": f"evt_{seq:03d}", "run_id": RUN_ID, "sequence": seq,
        "occurred_at": f"2026-11-23T12:{seq:02d}:00Z", "actor": actor, "event_type": etype,
        "state_machine": None, "previous_state": None, "new_state": None, "engine": None,
        "input_artifacts": [], "output_artifacts": [],
    }
    base.update(kw)
    return base


class DisagreementContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = ScriptedEngine("double_a", "profile", {"row_count": 4})
        self.b = ScriptedEngine("double_b", "profile", {"row_count": 5})
        participants = [self.a, self.b]
        self.results = [
            self.a.result("res_a", INDEPENDENT, participants),
            self.b.result("res_b", INDEPENDENT, participants),
        ]
        self.finding = build_disagreement_finding(self.results, "row_count", 0, ["scp_main"])

    def test_results_and_finding_validate_against_the_schemas(self) -> None:
        result_validator = make_validator("engine-result.schema.json")
        for result in self.results:
            self.assertEqual(collect_errors(result_validator, result), [])
        self.assertEqual(collect_errors(make_validator("finding.schema.json"), self.finding), [])

    def test_disagreement_preserves_both_observations_unaltered(self) -> None:
        values = {o["engine"]["name"]: o["value"] for o in self.finding["evidence"]["observations"]}
        self.assertEqual(values, {"double_a": 4, "double_b": 5})
        self.assertEqual(self.results[0]["profile"], {"row_count": 4})
        self.assertEqual(self.results[1]["profile"], {"row_count": 5})
        self.assertEqual(self.finding["status"], "needs_context")
        self.assertNotIn("proposed_action", self.finding)

    def test_agreement_within_tolerance_produces_no_finding(self) -> None:
        close = ScriptedEngine("double_c", "profile", {"row_count": 5})
        results = [self.b.result("res_b", INDEPENDENT, [self.b, close]), close.result("res_c", INDEPENDENT, [self.b, close])]
        self.assertIsNone(build_disagreement_finding(results, "row_count", 0, ["scp_main"]))
        self.assertIsNone(build_disagreement_finding(self.results, "row_count", 1, ["scp_main"]))

    def test_release_is_blocked_only_in_the_affected_scope_until_reconciled(self) -> None:
        engine = {"type": "engine", "id": "double_a"}
        coordinator = {"type": "coordinator", "id": "coordinator"}
        recorded = _event(
            1, "finding_recorded", coordinator, state_machine="finding", finding_id="fnd_disagree01",
            previous_state=None, new_state="needs_context",
        )
        before = replay([recorded])
        self.assertEqual(
            evaluate_release(SCOPES, [self.finding], [], before, [recorded]),
            {"scp_main": ["finding_needs_context:fnd_disagree01"], "scp_other": []},
        )

        reconciled = _event(
            2, "disagreement_reconciled", {"type": "human", "id": "analyst_01"}, state_machine="finding",
            finding_id="fnd_disagree01", previous_state="needs_context", new_state="resolved",
            resolution_basis="disagreement_reconciled", rationale="double_b counted a header row; double_a confirmed.",
        )
        events = [recorded, reconciled]
        for event in events:
            self.assertEqual(collect_errors(make_validator("audit-event.schema.json"), event), [])
        after = replay(events)
        self.assertTrue(after.ok, after.errors)
        self.assertEqual(after.states[("finding", "fnd_disagree01")], "resolved")
        self.assertEqual(evaluate_release(SCOPES, [self.finding], [], after, events), {s: [] for s in SCOPES})
        # Reconciliation is a documented decision. The original observations are untouched.
        self.assertEqual(self.finding["evidence"]["observations"][1]["value"], 5)
        del engine

    def test_resolution_without_basis_is_rejected_by_the_schema(self) -> None:
        bad = _event(
            2, "disagreement_reconciled", {"type": "human", "id": "analyst_01"}, state_machine="finding",
            finding_id="fnd_disagree01", previous_state="needs_context", new_state="resolved",
            rationale="trust me",
        )
        errors = collect_errors(make_validator("audit-event.schema.json"), bad)
        self.assertEqual([(e["validator"], e["json_path"]) for e in errors], [("required", "$")])

    def test_unavailable_engine_is_reported_and_never_replaced(self) -> None:
        silent = ScriptedEngine("double_b", "profile", {"row_count": 5}, available=False)
        participants = [self.a, silent]
        results = [self.a.result("res_a", INDEPENDENT, participants), silent.result("res_b", INDEPENDENT, participants)]
        self.assertEqual(results[1]["status"], "unavailable")
        self.assertIsNone(results[1]["profile"])
        self.assertEqual(results[1]["errors"][0]["code"], "engine_unavailable")
        for result in results:
            self.assertEqual(collect_errors(make_validator("engine-result.schema.json"), result), [])
        # No third value is substituted and no comparison is manufactured.
        self.assertIsNone(build_disagreement_finding(results, "row_count", 0, ["scp_main"]))
        self.assertEqual([r["produced_by"]["name"] for r in results], ["double_a", "double_b"])
        self.assertEqual(results[0]["profile"], {"row_count": 4})

    def test_double_is_deterministic(self) -> None:
        again = ScriptedEngine("double_a", "profile", {"row_count": 4}).result("res_a", INDEPENDENT, [self.a, self.b])
        self.assertEqual(again, copy.deepcopy(self.results[0]))


if __name__ == "__main__":
    unittest.main()
