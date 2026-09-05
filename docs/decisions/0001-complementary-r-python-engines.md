# ADR 0001: Complementary R and Python engines

- **Status:** Accepted
- **Date:** 2026-09-05

## Context

The initial architecture described R and Python as parallel implementations of
one specification and emphasized equivalent behavior. That approach supports
reproducibility but underuses the distinct strengths of the two ecosystems and
encourages duplicate implementation work.

## Decision

The Statistical Data Manager will be one coordinated statistical reasoning
system with complementary R and Python execution engines.

Collaborative mode is the preferred mode when both engines add meaningful
value. Native mode uses one engine when it is sufficient. Independent
validation mode assigns selected high-risk checks to both engines and preserves
disagreements for reconciliation or human review.

R and Python must share identifiers, profile definitions, finding and approval
states, provenance, and audit-event structure. They must agree on common facts
within documented tolerances. They are not required to implement the same
advanced capabilities or produce identical reports.

## Consequences

- A coordinator and explicit engine-routing policy become first-class parts of
  the system.
- Every result must identify its producing engine and capability.
- Shared tests focus on contracts, safety invariants, handoffs, and selected
  cross-engine validation cases.
- Engine-specific tests may cover capabilities available in only one ecosystem.
- Disagreement is represented as evidence requiring resolution, not treated as
  an implementation failure by default.
- Cross-language equivalence remains available as a validation technique but is
  no longer the defining architecture.
