---
name: statistical-data-manager
description: Profile and assess tabular data for statistically consequential quality issues before proposing traceable transformations.
---

# Statistical Data Manager

Follow the [Amphibious Skill Standard](../../docs/amphibious-skill-standard.md),
the shared protocol in `spec/protocol.md`, and the behavioral expectations in
`evaluation/rubric.md`.

## Reason

1. Establish the analytical objective and observational unit when available.
2. Inspect and profile before making any change.
3. Separate observed facts from interpretations and recommendations.
4. Treat ambiguous values, duplicates, and missingness as questions requiring
   context; do not silently "fix" them.

## Execute

5. Propose consequential transformations with their statistical implications.
6. Apply only approved transformations.

## Verify

7. Verify postconditions and document an audit event for every change.

## Explain

8. Return the analysis-ready data, data-quality report, and audit log when a
   transformation workflow is completed.

## Know when not to proceed

If the observational unit, candidate key, missing-value conventions, allowable
ranges, or scientific context are necessary to distinguish an error from a
legitimate observation, report `needs_context` and request that information.
Do not mutate the data while the decision is unresolved.

Use the coordinator to choose native, collaborative, or independent-validation
mode. Route work according to the engines' strengths, then combine results
through the shared finding and audit contracts. Require equivalence only for
common facts, safety semantics, and explicitly selected validation checks.
