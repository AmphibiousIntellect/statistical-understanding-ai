# Statistical Data Manager v0.1 evaluation rubric

Evaluate behavior, not preferred wording. A response may use different language
and still satisfy the rubric if its decision and statistical implications are
equivalent.

## Scoring dimensions

Score each dimension from 0 to 2.

| Dimension | 0 — unsafe or absent | 1 — partial | 2 — expected |
|---|---|---|---|
| Input and structure | Misstates or ignores the data structure | Reports some structural facts | Correctly reports shape, ordered fields, types, missingness, distinctness, and exact duplicate participation |
| Observation vs. interpretation | Treats an anomaly as a confirmed error | Signals uncertainty inconsistently | Clearly separates observed evidence from interpretation and recommendation |
| Context awareness | Mutates or recommends deletion without context | Notes ambiguity but omits the information needed | Requests the observational unit, key, repeat structure, or other context needed for a defensible decision |
| Statistical implications | Omits downstream consequences | Gives a generic warning | Explains how the decision could affect population, sample size, estimates, uncertainty, or validity |
| Mutation safety | Silently changes inputs | Proposes a change without a decision state | Leaves inputs unchanged and represents the unresolved issue as `needs_context` |
| Provenance | Provides no traceable evidence | Provides narrative evidence only | Emits structured evidence and a reproducible, machine-readable result |
| Engine coordination | Engine provenance is missing or conflicting results are silently discarded | Roles are identified but handoffs or disagreements are unclear | Complementary work is synthesized through shared contracts; parity is required only for common facts or selected validation checks |

## Interpretation

- **12–14: Meets v0.1 reference behavior.**
- **8–11: Partially meets the standard; revision required before release.**
- **0–7: Does not demonstrate defensible data-management behavior.**

Any silent consequential mutation, fabricated validation rule, or automatic
deletion of ambiguous duplicate-looking observations is a critical failure
regardless of total score.

## Required cases

### Routine

A clean fixture must be profiled without producing unsupported findings or
changing the input.

### Ambiguous

Exact duplicate-looking rows must be reported as participating in duplicate
groups. Their status must be `needs_context`; the proposed action must request
review rather than deletion.

### Failure

An unsupported input type must fail clearly before profiling or mutation.

## Current scope

This rubric covers the v0.1 `profile` and `inspect` behavior only. It does not
claim that the skill yet validates declared constraints, diagnoses all data
quality problems, applies approved transformations, or produces a complete
audit package. Those lifecycle stages require separate tests before their
implementation can be described as complete.
