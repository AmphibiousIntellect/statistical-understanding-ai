# Shared protocol

## Lifecycle

1. **Inspect** — identify shape, fields, types, observational unit, candidate keys, and provenance.
2. **Profile** — summarize missingness, distinctness, distributions, category levels, and ranges.
3. **Validate** — evaluate declared constraints without inventing undeclared rules.
4. **Diagnose** — distinguish confirmed defects from anomalies that need context.
5. **Propose** — state evidence, statistical implication, proposed action, and reversibility.
6. **Transform** — apply approved actions only; preserve original values or an equivalent lineage path.
7. **Verify** — rerun relevant checks and confirm row, key, type, and value postconditions.
8. **Document** — emit a machine-readable audit log and a human-readable quality report.

## Safety invariants

- Detection is not permission to mutate.
- Plausibility is contextual; an extreme value is not automatically erroneous.
- Duplicate-looking rows may be legitimate repeated observations.
- Missingness can be structural or informative and should not be erased by default.
- Every applied transformation links to its evidence, rationale, approval, and verification.

## Starter contract

`profile(data)` returns row count, column count, ordered column names, inferred
types, missing counts, unique counts, and exact duplicate-row count.

`inspect(data)` returns the profile plus findings. The starter duplicate finding
uses `needs_context` status and proposes review rather than deletion.
