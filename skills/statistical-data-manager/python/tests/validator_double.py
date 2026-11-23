"""Deterministic validator test double for the disagreement-path contract (test-only).

It uses fixed, scripted facts. It does not parse data, so it cannot flake on
pandas or R version differences. Real cross-engine parsing cases are separate.
"""

from __future__ import annotations

from typing import Any

NOW = "2026-11-23T12:00:00Z"
RUN_ID = "run_double01"
INPUT = {"path": "fixtures/duplicate_rows.csv", "sha256": "0" * 64}


class ScriptedEngine:
    def __init__(self, name: str, capability: str, facts: dict[str, Any], available: bool = True) -> None:
        self.name = name
        self.capability = capability
        self.facts = facts
        self.available = available

    def record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": "double-1",
            "capability": self.capability,
            "implementation_revision": "double-rev",
            "configuration": {"scripted": True},
        }

    def result(self, result_id: str, mode: str, participants: list["ScriptedEngine"]) -> dict[str, Any]:
        base: dict[str, Any] = {
            "schema_version": "0.2",
            "engine_result_id": result_id,
            "run_id": RUN_ID,
            "coordination_mode": mode,
            "engines": [p.record() for p in participants],
            "produced_by": {"name": self.name, "capability": self.capability},
            "started_at": NOW,
            "completed_at": NOW,
            "inputs": [INPUT],
            "findings": [],
        }
        if not self.available:
            return {**base, "status": "unavailable", "completed_at": None, "profile": None,
                    "errors": [{"code": "engine_unavailable", "message": f"{self.name} did not respond"}]}
        return {**base, "status": "completed", "profile": dict(self.facts), "errors": []}


def build_disagreement_finding(
    results: list[dict[str, Any]], fact: str, tolerance: float | None, scopes: list[str]
) -> dict[str, Any] | None:
    """Return an engine_disagreement finding, or None when the completed results agree.

    Observations are preserved verbatim. Nothing is averaged, chosen, or overwritten.
    """
    completed = [r for r in results if r["status"] == "completed"]
    values = [r["profile"][fact] for r in completed]
    if len(completed) < 2:
        return None
    spread_ok = max(values) - min(values) <= (tolerance or 0)
    if spread_ok:
        return None
    return {
        "schema_version": "0.2",
        "finding_id": "fnd_disagree01",
        "run_id": RUN_ID,
        "code": "engine_disagreement",
        "severity": "error",
        "status": "needs_context",
        "message": f"Engines disagree on {fact}.",
        "evidence": {
            "fact": fact,
            "tolerance": tolerance,
            "observations": [
                {"engine": r["produced_by"], "engine_result_id": r["engine_result_id"], "value": r["profile"][fact]}
                for r in completed
            ],
        },
        "statistical_implication": "Downstream populations and estimates depend on which value is correct.",
        "context_required": ["Reconcile the disputed fact and document the basis."],
        "produced_by": {"name": "coordinator", "capability": "reconciliation"},
        "engine_result_id": completed[0]["engine_result_id"],
        "release_blocking": True,
        "affected_release_scope": scopes,
        "materiality_rationale": None,
    }
