# Statistical Data Manager protocol v0.1

## Purpose

The Statistical Data Manager turns raw tabular data and its analytical context
into a defensible, analysis-ready package. It must preserve evidence, distinguish
observation from judgment, and never silently make consequential changes.

## Inputs

- immutable raw data
- data dictionary, when available
- study design and observational unit
- analytical objective and intended analysis population
- domain rules, constraints, and expected relationships
- provenance for every input

Missing context is itself reportable. The absence of a dictionary, stated
observational unit, or analytical objective must not be silently replaced with
an unsupported assumption.

## Workflow

1. **Inspect**: identify tables, dimensions, encodings, fields, candidate keys,
   and structural relationships.
2. **Profile**: calculate deterministic summaries of types, distributions,
   missingness, categories, formats, uniqueness, and duplicate patterns.
3. **Validate**: evaluate explicit rules, constraints, expectations, and
   cross-field or cross-table relationships.
4. **Diagnose**: describe each issue's evidence, ambiguity, likely causes, and
   possible statistical consequences.
5. **Propose**: recommend zero or more actions, including preserving the value or
   requesting context. No proposal mutates data.
6. **Approve**: record an explicit decision for every consequential proposal.
7. **Transform**: apply only approved actions through deterministic,
   reproducible code.
8. **Verify**: independently check transformations, invariants, joins, record
   counts, analysis populations, and rule compliance.
9. **Document**: emit findings, decisions, changes, unresolved questions,
   validation results, and provenance.

## Required separation

Each finding separates:

- **evidence**: directly observed facts
- **statistical implication**: why the evidence may matter
- **proposed action**: a recommendation, not an executed change
- **approval**: who authorized or rejected the proposal and when
- **audit event**: what was actually executed and verified

## Status transitions

```text
observed -> needs_context -> proposed -> approved -> applied
                                  |          |
                                  +-> rejected
                                             |
                                             +-> proposed (revised proposal)
```

`applied` is valid only when an approval record and successful verification are
linked to the finding. Findings may remain `observed` or `needs_context`
indefinitely without changing the source data.

## Non-negotiable invariants

- Raw inputs are immutable and identified by a checksum.
- Detection is not permission to mutate.
- Ambiguity triggers a context request, not an invented rule.
- Every changed value is traceable to a finding, proposal, approval, and code
  revision.
- Failed verification is visible and prevents a release-ready status.
- R and Python engines implement the same externally observable behavior.
- No statistical output is released without provenance.

## Initial issue families

- dates, times, time zones, and partial dates
- missing values, missing-value codes, and structural missingness
- strings, whitespace, Unicode, case, and encoding
- categorical levels, labels, ordering, and invalid values
- identifiers, duplicates, repeated observations, joins, and table grain
- numeric types, ranges, units, coercion, and cross-field consistency

## Output package

```text
run-id/
  manifest.json
  proposed-actions.json
  approvals.json
  output/analysis-ready.*
  reports/data-quality.*
  reports/validation.*
  audit/transformations.jsonl
  audit/unresolved-issues.json
  code/transform.R
  code/transform.py
  environment/r-session-info.txt
  environment/python-environment.txt
```

The manifest must identify the input checksums, schema versions, implementation
revision, execution environment, output checksums, and verification outcome.

## v0.1 acceptance criteria

- Inspection and profiling do not mutate their input.
- Every issue includes evidence and a status valid under
  `schemas/finding.schema.json`.
- No consequential transformation runs without an approval record.
- Approved transformations are deterministic and auditable.
- Ambiguous or rejected proposals leave source values unchanged.
- Shared fixtures produce equivalent R and Python profiles and findings.
- Output schema, row identity, transformed values, and validation outcomes agree
  across engines where language differences do not prevent equivalence.
