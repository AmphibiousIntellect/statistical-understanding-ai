# ADR 0002: Deterministic routing, provenance, and the state model

- **Status:** Proposed
- **Date:** 2026-11-23
- **Related:** [ADR 0001](0001-complementary-r-python-engines.md) (refined, not replaced),
  [open decisions](open-decisions.md), [draft v0.2 contracts](../../schemas/v0.2/README.md)

## Context

ADR 0001 established complementary R and Python engines with collaborative,
native, and independent-validation modes, shared identifiers and states, and
preserved disagreements. It did not say how work is routed, what happens when an
engine is unavailable, how engine participation is recorded, how states change,
or when a result may be released. The v0.1 schemas also identify approvals by a
finding code, which cannot express several alternative actions for one finding,
and they record no engine provenance.

This ADR does not change ADR 0001. It makes its commitments precise enough to
test. The contracts it describes live in `schemas/v0.2/` as **drafts**; the
implemented v0.1 schemas in `schemas/` are unchanged by this decision.

## Decision

### 1. Deterministic engine routing

Routing is a pure function of four recorded inputs: the requested capability,
the requested coordination mode, the declared availability of engines, and the
routing-policy identifier and version. Given the same inputs it always selects
the same engines. Routing may not depend on randomness, on hidden state, or on
data-dependent heuristics that are not written in the routing policy. The run
manifest records the policy (`routing_policy`), the mode, and the selected
engine records, so that the selection can be reproduced and audited.

### 2. No silent engine fallback

If a selected engine is unavailable or fails, the result records it:

- the engine result has status `unavailable` or `failed` with an error;
- the coordinator records an `engine_unavailable` finding;
- the run's `verification_status` is `not_run` or `failed`.

No other engine is substituted and no partial result is presented as complete.
Using a different engine requires a new run whose requested mode or engines say
so explicitly. Native-mode runs and independent-validation runs follow the same
rule.

### 3. Engine and capability provenance

Every engine result, finding, action, and audit event identifies the engine and
capability that produced it. Engine participation is an array of **engine
records**; each record carries `name`, `version`, `capability`,
`implementation_revision`, and `configuration`. Engine names are free strings:
the schemas do not enumerate engines or assign languages to roles.

### 4. Coordination modes

`coordination_mode` is a separate required field with one of three values.

| Mode | Engine records | Meaning |
|---|---|---|
| `native` | exactly one | One engine completes the work. |
| `collaborative` | two or more | Engines own complementary stages and exchange results through the contracts. |
| `independent_validation` | two or more | Selected high-risk facts or decisions are evaluated separately by each engine. |

### 5. Disagreement preservation and reconciliation

A disagreement between engines is evidence, not an error to be repaired. When
independent results differ on a common fact beyond its documented tolerance, the
coordinator records a finding with code `engine_disagreement`. Its evidence names
the fact, the tolerance, and at least two observations (engine, engine result,
value). Original engine results are never overwritten, averaged, or ranked. The
finding starts as `needs_context` and is `release_blocking` by default for the
scopes that depend on the disputed fact.

Reconciliation is a documented decision by a person or a documented rule. It is
recorded as a `disagreement_reconciled` audit event with a rationale and the
resolution basis `disagreement_reconciled`; the finding then becomes `resolved`.
The original observations remain in the record.

### 6. Identifiers

| Identifier | Identifies | Prefix |
|---|---|---|
| `finding_id` | One piece of observed evidence | `fnd_` |
| `action_id` | One exact, immutable proposed action | `act_` |
| `approval_id` | One decision concerning an action | `apr_` |
| `audit_event_id` | One state transition or run-level event | `evt_` |
| `run_id` | The run that links all artifacts | `run_` |
| `engine_result_id`, `release_scope_id` | An engine result; a released output set | `res_`, `scp_` |

An approval references `action_id` and the SHA-256 `action_digest` of the action
as emitted. A finding alone is never enough: one finding may have several
alternative actions. Digest input is the canonical JSON (sorted keys, no
insignificant whitespace, UTF-8) of the action document.

### 7. State model

The audit-event stream is **authoritative** for current state. The `status`
field of a finding or action document is its status at emission and is not
authoritative. Documents are immutable; a changed action is a new action with a
new `action_id` and `supersedes_action_id`.

`needs_context` is a finding status. It is not an approval decision. Approval
decisions are `approved`, `rejected`, and `deferred`; a deferral records the
`context_required`.

**Finding states:** `observed`, `needs_context`, `proposed`, `resolved`,
`remediated`. **Action states:** `proposed`, `approved`, `rejected`, `deferred`,
`applied`, `verified`, `verification_failed`, `superseded`.

Creating an action does not change its finding. A finding becomes `proposed`
only through an explicit transition. A finding may have several alternative
actions, optionally grouped by `alternative_group_id`.

No action may execute while its associated finding remains `needs_context`. This
does not make such findings permanently unactionable: once context is
documented, the finding may transition to `proposed`, and an action already
proposed (for example one that was deferred) may be approved under the same
`action_id` if its digest is unchanged, or a new action may be proposed.

#### Finding transitions

| ID | From | To | Event type(s) | Actor | Guard |
|---|---|---|---|---|---|
| F1 | ∅ | observed | `finding_recorded` | engine | Evidence is present. |
| F2 | ∅ | needs_context | `finding_recorded` | engine | `context_required` is non-empty. |
| F3 | observed | needs_context | `finding_transitioned` | engine or human | `context_required` is stated. |
| F4 | observed | proposed | `finding_transitioned` | coordinator or human | At least one candidate action exists that is not superseded. Explicit; never automatic. |
| F5 | needs_context | proposed | `finding_transitioned` | coordinator or human | Context is documented (a context artifact or a human rationale) and a candidate action is `proposed` or `deferred`. |
| F6 | proposed | needs_context | `finding_transitioned` | coordinator or human | `context_required` is stated, for example after a deferral. Explicit; a deferral alone does not move the finding. |
| F7 | proposed | observed | `finding_transitioned` | coordinator or human | No action is `proposed`, `deferred`, `approved`, or `applied`; all candidates are rejected or superseded. |
| F8 | proposed | resolved | `finding_transitioned` | human or coordinator | A `resolution_basis` and rationale are recorded; every candidate action is rejected or superseded. |
| F9 | needs_context | resolved | `finding_transitioned`, `disagreement_reconciled` | human | A `resolution_basis` and rationale are recorded; no candidate action is open. Engine disagreements use `disagreement_reconciled`. |
| F10 | proposed | remediated | `finding_transitioned` | coordinator or human | At least one action is `verified` and no sibling in its alternative group is open. |

#### Action transitions

| ID | From | To | Event type(s) | Actor | Guard |
|---|---|---|---|---|---|
| A1 | ∅ | proposed | `action_proposed` | engine | The finding exists; `postconditions` and `release_blocking` are declared. Does not change the finding. |
| A2 | proposed | approved | `approval_recorded` | human | `decision` is `approved`; `action_id` and `action_digest` match; the finding is `proposed`; no sibling in the alternative group is approved, applied, or verified. |
| A3 | proposed | rejected | `approval_recorded` | human | `decision` is `rejected` with a rationale. |
| A4 | proposed | deferred | `approval_recorded` | human | `decision` is `deferred` with `context_required`. |
| A5 | deferred | approved | `approval_recorded` | human | As A2; the approval supersedes the deferral and the digest is unchanged. |
| A6 | deferred | rejected | `approval_recorded` | human | The approval supersedes the deferral. |
| A7 | deferred | deferred | `approval_recorded` | human | More context is required; the approval supersedes the earlier deferral. |
| A8 | approved | rejected | `approval_recorded` | human | Revocation before the action is applied; the approval supersedes the earlier approval. |
| A9 | proposed | superseded | `action_superseded` | engine or human | A new action sets `supersedes_action_id`; rationale required. |
| A10 | deferred | superseded | `action_superseded` | engine or human | As A9. |
| A11 | approved | superseded | `action_superseded` | engine or human | As A9, before apply, for example when the input checksum changed. |
| A12 | approved | applied | `transformation_applied` | engine | `mutation_class` is `metadata_only` or `data_mutation`; the finding is `proposed` and not `needs_context`; a matching `action_id` and digest are approved; the input checksum equals the action's target input; output is written to a separate artifact. |
| A13 | applied | verified | `verification_completed` | engine | Every declared postcondition holds. |
| A14 | applied | verification_failed | `verification_completed` | engine | Any declared postcondition fails. |

`rejected`, `verified`, `verification_failed`, and `superseded` are terminal.
Actions with `mutation_class: none` are advisory: they may be decided, but are
never applied. Any pair not listed is invalid. The machine-readable form is
`schemas/v0.2/state-transitions.json`; tests assert that this ADR, that file, and
the schema enumerations agree.

#### Approval history

Approvals are immutable. The first approval for an action supersedes nothing
(`supersedes_approval_id` is null). Every later approval for the same action must
supersede the current head approval and carry the same `action_digest`.
Permitted decision changes are `deferred` to any decision, and `approved` to
`rejected` before apply. `rejected` is final. A fork (two approvals superseding
the same approval) is invalid.

#### Alternatives, selection, resolution, remediation

- **Selection** is approving one action. It is invalid if another action in the
  same alternative group is already approved, applied, or verified. Remaining
  group members then need explicit `rejected` or `superseded` decisions; they are
  not changed implicitly.
- **Rejection** of an action never changes the finding by itself.
- **Resolution** records that no remediation is required, with a
  `resolution_basis` of `context_shows_legitimate`, `disagreement_reconciled`, or
  `accepted_unchanged`, and a rationale. No candidate action may remain open.
- **Remediation** records that a verified action satisfies the finding, by an
  explicit transition after at least one action is `verified`.

### 8. Audit stream: replay and integrity

1. Events are ordered by `sequence`, an integer unique within a run, starting at
   1 and increasing without gaps.
2. A repeated event with the same `audit_event_id` and identical content is
   idempotent: it is applied once and reported as a warning.
3. The same `audit_event_id` with different content, or two different events with
   the same `sequence`, is a hard failure.
4. A missing sequence number is a hard failure and a run-wide release blocker.
5. Each event's `previous_state` must equal the replayed state of its subject,
   and the pair must be a listed transition for its event type. Guards that
   reference other subjects (finding state, alternative groups) are checked
   during replay.
6. The run manifest carries the stream's SHA-256, `event_count`, and
   `last_sequence`, which replay must reproduce. The manifest holds no state
   summary of its own.

### 9. Release blockers

Release is evaluated per **release scope**: a named set of outputs declared in
the manifest. A finding or action declares `release_blocking`, the scopes it
affects (`affected_release_scope`), and a `materiality_rationale`, required when
it is not blocking. Not every open item blocks every output.

*Scoped blockers* (they block only the scopes they affect):

- a `release_blocking` finding in `needs_context`, including an unreconciled
  `engine_disagreement`;
- a `release_blocking` action that is `proposed`, `deferred`, `approved`,
  `applied`, or `verification_failed`;
- a non-blocking declaration for a `needs_context` finding that has no
  `release_materiality_declared` audit event.

*Run-wide blockers* (they block every scope):

- audit replay failure: a sequence gap or collision, a conflicting duplicate, a
  state mismatch, or a manifest mismatch;
- an input or output checksum mismatch;
- a required engine that was unavailable in the declared mode;
- schema-validation failure of any run artifact;
- `verification_status` other than `passed`;
- an approval whose digest does not match its action.

Engines default `needs_context` findings and disagreements to
`release_blocking: true`, because an engine cannot judge materiality without
analytical context. Lowering that default is a recorded decision with a
rationale.

### 10. Engine roles are not architecture

The first implementation slice may use one engine to execute and another to
validate independently. That division is a property of that slice, not an
architectural requirement. Nothing in the schemas or this ADR assigns languages
to roles.

## Consequences

- The v0.2 contracts are drafts under `schemas/v0.2/`. The v0.1 schemas in
  `schemas/` remain the implemented contract. Promotion criteria are in
  `schemas/v0.2/README.md`.
- v0.2 differs from v0.1 in ways that will need migration if promoted:
  approvals reference `action_id` and `action_digest` instead of `finding_code`;
  `needs_context` is no longer an approval decision (`deferred` replaces it);
  a finding's `proposed_action` string becomes separate action documents;
  engine provenance (`engines[]`, `produced_by`) and `coordination_mode` are
  required; `engine` in the manifest is replaced by `engines[]`; and the manifest
  gains release scopes and an audit-log reference.
- Documents become immutable snapshots and current state comes from audit replay.
- Every transformation proposal is tied to an exact action version, an approval,
  and verification evidence.
- Existing Python and R behavior is unchanged by this decision, and no
  transformation is implemented by it.

## Open items

Recorded in [open decisions](open-decisions.md): the ownership and publication of
the schema `$id` base, and a review of the contact address in
`skills/statistical-data-manager/r/DESCRIPTION`.
