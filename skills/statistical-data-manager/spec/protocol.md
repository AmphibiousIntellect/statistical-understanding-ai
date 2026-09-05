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

## Engine coordination

Before inspection, select an operating mode:

- **Collaborative** — R and Python own complementary stages or checks and their
  results are synthesized into one outcome. This is the default when both add
  meaningful value.
- **Native** — one engine owns the workflow because it is sufficient and better
  suited to the task.
- **Independent validation** — both engines evaluate selected high-risk facts or
  decisions separately, and disagreements are escalated for reconciliation.

Every delegated result must identify its engine, capability, evidence, and
provenance. The coordinator must preserve disagreements rather than overwrite
or average them.

## Interoperability contract

R and Python share identifiers, profile field definitions, finding states,
approval semantics, and audit-event structure. Common factual checks should be
consistent within documented tolerances. Advanced methods and language-specific
capabilities do not require equivalent implementations or outputs.

## Safety invariants

- Detection is not permission to mutate.
- Plausibility is contextual; an extreme value is not automatically erroneous.
- Duplicate-looking rows may be legitimate repeated observations.
- Missingness can be structural or informative and should not be erased by default.
- Every applied transformation links to its evidence, rationale, approval, and verification.

## Starter contract

`profile(data)` returns row count, column count, ordered column names, inferred
types, missing counts, unique counts, and exact duplicate-row count.

`inspect(data)` returns the profile plus findings. Each future finding will also
identify its producing engine and coordination mode. The starter duplicate finding
uses `needs_context` status and proposes review rather than deletion.
