# Draft v0.2 contracts

**Status: draft. Not published. Not implemented by the Python or R engines.**

These files propose the next version of the Statistical Data Manager contracts as
described in [ADR 0002](../../docs/decisions/0002-routing-provenance-and-state-model.md).
They are exercised only by contract tests with synthetic examples.

## Contents

| File | Purpose |
|---|---|
| `common.schema.json` | Identifier patterns, `artifact_ref`, engine records, state enumerations |
| `finding.schema.json` | Observed evidence, with release scope and materiality |
| `action.schema.json` | One immutable proposed action; `mutation_class` is `none`, `metadata_only`, or `data_mutation` |
| `extensions/trim-whitespace.action.schema.json` | Slice-specific constraints for `trim_whitespace` |
| `approval.schema.json` | A decision concerning one action; `approved`, `rejected`, or `deferred` |
| `engine-result.schema.json` | One engine's result with engine records and coordination mode |
| `audit-event.schema.json` | One state transition; the ordered stream is authoritative for current state |
| `run-manifest.schema.json` | Links every artifact by `run_id`; release is evaluated per scope |
| `state-transitions.json` | Machine-readable transition table, mirrored in the ADR |
| `examples/` | Valid instances, invalid instances, and sidecar files naming the expected failures |

## Relationship to v0.1

The three schemas in [`schemas/`](..) (`finding`, `approval`, `run-manifest`)
remain the implemented contract. The current Python and R output conforms to
them. Phase 1 does not modify them, and nothing in this directory replaces them.

The v0.2 files carry the same `$id` base as v0.1 plus `/v0.2/`. That base is a
placeholder pending the decision in
[open decisions](../../docs/decisions/open-decisions.md). Tests resolve every
`$ref` through a local registry and never use the network.

## Migration requirements

A move from v0.1 to v0.2 would require:

| v0.1 | v0.2 |
|---|---|
| Approval refers to `finding_code` | Approval refers to `action_id` and `action_digest`; `needs_context` is no longer a decision (`deferred` records the context required) |
| A finding carries a `proposed_action` string | The finding carries evidence only; proposals are separate action documents |
| No engine provenance | `engines[]`, `produced_by`, and `coordination_mode` are required |
| Manifest `engine` is `r`, `python`, or `cross-language` | `engines[]` of engine records plus `coordination_mode` |
| One manifest-wide verification status | Verification status plus per-scope release status and blockers |
| No audit events | An audit-event stream is authoritative for current state |

The engines would need adapters that emit v0.2 documents, any consumer of v0.1
files would need notice, and the version identifiers in `schema_version` and the
`$id` path would need a published compatibility statement.

## Promotion criteria

These contracts move out of draft only when all of the following hold:

1. ADR 0002 is accepted.
2. Ownership and publication of the `$id` base are confirmed and recorded.
3. At least one implemented vertical slice emits v0.2 documents from the engines,
   and those documents pass the contract tests.
4. Cross-engine contract tests pass, including the disagreement path.
5. A migration guide for v0.1 consumers is written.
6. The v0.1 relationship is decided: replace, deprecate, or version side by side.
7. No blocking review item remains in the open-decisions register.

## Conventions

- Draft 2020-12 with format checking. Tests build every validator through one
  factory that sets `Draft202012Validator` and its `FormatChecker`.
- Documents are immutable snapshots. The `status` field is the status at
  emission and is not authoritative; replaying the audit stream is.
- The schemas avoid `oneOf` and `anyOf` so validation errors are flat and their
  JSON paths predictable.
- Invalid examples are pure instances. The expected validator and JSON path for
  each live in a sidecar file of the same name under `examples/expected-failures/`.
- Audit streams under `examples/audit-streams/` demonstrate replay, duplicate
  handling, sequence collisions, gaps, and guard violations.
