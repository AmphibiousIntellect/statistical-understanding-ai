"""Reference audit-stream replay verifier.

TEST-ONLY. This is contract-verification infrastructure that makes the draft v0.2
audit rules executable for tests. It is not product code, performs no data
transformation, and is not exported by the package. Phase 2 may promote it.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from _contracts import V02, canonical_json, load_json

_TABLE = load_json(V02 / "state-transitions.json")
_LEGAL: dict[tuple[str, str | None, str], set[str]] = {}
for _machine in ("finding", "action"):
    for _t in _TABLE[_machine]["transitions"]:
        _LEGAL[(_machine, _t["from"], _t["to"])] = set(_t["event_types"])

_OPEN_ACTION_STATES = {"proposed", "deferred", "approved", "applied"}


@dataclass
class ReplayResult:
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    states: dict[tuple[str, str], str] = field(default_factory=dict)
    event_count: int = 0
    last_sequence: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def error_codes(self) -> list[str]:
        return sorted({e["code"] for e in self.errors})

    @property
    def warning_codes(self) -> list[str]:
        return sorted({w["code"] for w in self.warnings})


def replay(
    events: list[dict[str, Any]],
    actions: dict[str, dict[str, Any]] | None = None,
    manifest: dict[str, Any] | None = None,
    stream_bytes: bytes | None = None,
) -> ReplayResult:
    """Replay an audit stream. The stream is the sole authority on current state."""
    actions = actions or {}
    result = ReplayResult()

    # 1. Duplicate handling by audit_event_id.
    seen: dict[str, str] = {}
    kept: list[dict[str, Any]] = []
    for event in events:
        event_id = event["audit_event_id"]
        canon = canonical_json(event)
        if event_id in seen:
            if seen[event_id] == canon:
                result.warnings.append({"code": "duplicate_event_ignored", "event": event_id})
            else:
                result.errors.append({"code": "conflicting_duplicate", "event": event_id})
            continue
        seen[event_id] = canon
        kept.append(event)

    # 2. Sequence uniqueness and gaps.
    by_sequence: dict[int, list[str]] = {}
    for event in kept:
        by_sequence.setdefault(event["sequence"], []).append(event["audit_event_id"])
    for sequence, ids in sorted(by_sequence.items()):
        if len(ids) > 1:
            result.errors.append({"code": "sequence_collision", "sequence": sequence, "events": ids})
    if by_sequence:
        for missing in sorted(set(range(1, max(by_sequence) + 1)) - set(by_sequence)):
            result.errors.append({"code": "sequence_gap", "sequence": missing})
    result.event_count = len(kept)
    result.last_sequence = max(by_sequence) if by_sequence else 0

    # 3. State replay in sequence order.
    action_finding: dict[str, str] = {}
    group_of = {aid: doc.get("alternative_group_id") for aid, doc in actions.items()}
    states = result.states

    def finding_state(finding_id: str) -> str | None:
        return states.get(("finding", finding_id))

    def siblings(action_id: str) -> list[str]:
        group = group_of.get(action_id)
        if not group:
            return []
        finding_id = action_finding.get(action_id)
        return [
            other
            for other, other_finding in action_finding.items()
            if other != action_id and other_finding == finding_id and group_of.get(other) == group
        ]

    for event in sorted(kept, key=lambda e: (e["sequence"], e["audit_event_id"])):
        machine = event["state_machine"]
        if machine is None:
            continue
        subject = event["finding_id"] if machine == "finding" else event["action_id"]
        key = (machine, subject)
        previous, new, event_type = event["previous_state"], event["new_state"], event["event_type"]
        seq = event["sequence"]

        if previous != states.get(key):
            result.errors.append({"code": "state_mismatch", "sequence": seq, "subject": subject})
        if event_type not in _LEGAL.get((machine, previous, new), set()):
            result.errors.append({"code": "illegal_transition", "sequence": seq, "subject": subject})

        if machine == "action":
            finding_id = event["finding_id"]
            if event_type == "action_proposed":
                action_finding[subject] = finding_id
            if event_type == "approval_recorded" and new == "approved":
                if finding_state(finding_id) != "proposed":
                    result.errors.append({"code": "approval_requires_proposed_finding", "sequence": seq})
                if any(states.get(("action", s)) in {"approved", "applied", "verified"} for s in siblings(subject)):
                    result.errors.append({"code": "sibling_already_selected", "sequence": seq})
            if event_type == "transformation_applied" and finding_state(finding_id) != "proposed":
                result.errors.append({"code": "apply_requires_proposed_finding", "sequence": seq})
            if event_type == "action_superseded" and event.get("related_action_id") not in action_finding:
                result.errors.append({"code": "unknown_superseding_action", "sequence": seq})
        else:
            owned = [a for a, f in action_finding.items() if f == subject]
            if new == "remediated":
                verified = [a for a in owned if states.get(("action", a)) == "verified"]
                if not verified:
                    result.errors.append({"code": "remediation_requires_verified_action", "sequence": seq})
                for chosen in verified:
                    if any(states.get(("action", s)) in _OPEN_ACTION_STATES for s in siblings(chosen)):
                        result.errors.append({"code": "open_sibling_action", "sequence": seq})
            if new == "resolved" and any(
                states.get(("action", a)) in _OPEN_ACTION_STATES | {"verified"} for a in owned
            ):
                result.errors.append({"code": "resolved_with_open_actions", "sequence": seq})

        states[key] = new

    # 4. Manifest agreement.
    if manifest is not None:
        log = manifest["audit_log"]
        if log["event_count"] != result.event_count:
            result.errors.append({"code": "manifest_event_count_mismatch"})
        if log["last_sequence"] != result.last_sequence:
            result.errors.append({"code": "manifest_last_sequence_mismatch"})
        if stream_bytes is not None and hashlib.sha256(stream_bytes).hexdigest() != log["sha256"]:
            result.errors.append({"code": "manifest_sha256_mismatch"})
    return result


def check_approval_chain(action: dict[str, Any], approvals: list[dict[str, Any]]) -> list[str]:
    """Check the immutable approval history for one action. Returns error codes."""
    from _contracts import action_digest

    chain = _TABLE["approval_chain"]
    codes: list[str] = []
    digest = action_digest(action)
    head: dict[str, Any] | None = None
    superseded: set[str] = set()
    for approval in approvals:
        if approval["action_id"] != action["action_id"]:
            codes.append("approval_for_other_action")
        if approval["action_digest"] != digest:
            codes.append("digest_mismatch")
        target = approval["supersedes_approval_id"]
        if head is None:
            if target is not None:
                codes.append("first_approval_supersedes_unknown")
        else:
            if target is None:
                codes.append("missing_supersedes")
            elif target != head["approval_id"]:
                codes.append("approval_fork" if target in superseded else "supersedes_not_head")
            elif approval["decision"] not in chain[head["decision"]]:
                codes.append("illegal_decision_change")
        if head is not None and target is not None:
            superseded.add(target)
        head = approval
    return sorted(set(codes))


def evaluate_release(
    scope_ids: list[str],
    findings: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    replayed: ReplayResult,
    events: list[dict[str, Any]],
    verification_status: str = "passed",
) -> dict[str, list[str]]:
    """Per-scope release blockers. Not every open item blocks every scope."""
    blockers: dict[str, list[str]] = {scope: [] for scope in scope_ids}
    if not replayed.ok:
        for scope in scope_ids:
            blockers[scope].append("run_wide:replay_failed")
    if verification_status != "passed":
        for scope in scope_ids:
            blockers[scope].append("run_wide:verification_not_passed")

    declared = {e["finding_id"] for e in events if e["event_type"] == "release_materiality_declared" and "finding_id" in e}
    for finding in findings:
        state = replayed.states.get(("finding", finding["finding_id"]), finding["status"])
        if state != "needs_context":
            continue
        if finding["release_blocking"]:
            code = f"finding_needs_context:{finding['finding_id']}"
        elif finding["finding_id"] not in declared:
            code = f"undeclared_materiality:{finding['finding_id']}"
        else:
            continue
        for scope in finding["affected_release_scope"]:
            if scope in blockers:
                blockers[scope].append(code)
    for action in actions:
        state = replayed.states.get(("action", action["action_id"]), action["status"])
        if action["release_blocking"] and state in {"proposed", "deferred", "approved", "applied", "verification_failed"}:
            for scope in action["affected_release_scope"]:
                if scope in blockers:
                    blockers[scope].append(f"action_open:{action['action_id']}")
    return {scope: sorted(codes) for scope, codes in blockers.items()}
