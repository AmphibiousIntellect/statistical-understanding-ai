# Amphibious Skill Standard v0.1

The Amphibious Skill Standard defines the minimum public contract for a
statistical skill in SUAI. A skill is not merely a prompt or a wrapper around a
library. It must express how an AI reasons about a statistical task, executes it
transparently, verifies the result, communicates its limits, and recognizes when
it should not proceed.

## Required capabilities

Every skill must support five capabilities.

### 1. Reason

Identify the scientific or analytical objective, the estimand or target when
applicable, the study and data structure, required context, assumptions, and
plausible alternatives before selecting an operation.

### 2. Execute

Produce a traceable implementation in R, Python, or both. Execution must follow
the shared statistical specification rather than allowing language-specific
defaults to determine the analysis silently.

### 3. Verify

Check inputs, intermediate decisions, and outputs. When both engines exist, use
shared fixtures and compare behavior at the level that matters statistically:
populations, exclusions, derivations, estimates, uncertainty, and conclusions.

### 4. Explain

Report the question addressed, evidence used, decisions made, assumptions,
limitations, and the provenance needed to reproduce the result. Separate
observations from interpretations and recommendations.

### 5. Know when not to proceed

Stop or request context when information needed for a defensible decision is
missing. A skill must not turn anomaly detection into permission to mutate data,
select a model, or make a stronger claim than the design and evidence support.

## Required skill contents

Each public skill must include:

- `SKILL.md` with a precise activation description and the essential reasoning
  and safety instructions;
- a language-agnostic specification defining inputs, outputs, decision states,
  invariants, and failure or stop conditions;
- examples or fixtures that include routine, ambiguous, and failure cases;
- behavioral tests for the statistically important invariants;
- an evaluation rubric describing expected, weak, and unsafe behavior;
- provenance requirements for consequential decisions and generated outputs;
- engine-routing, interoperability, and targeted parity notes when R or Python
  execution is implemented.

Supporting references and scripts should exist only when they make the skill
more reliable or keep conditional detail out of `SKILL.md`.

## Decision states

A skill must distinguish at least these states:

- **observed** — directly supported by the input;
- **needs context** — detected, but not defensibly interpretable yet;
- **proposed** — an action or conclusion has been recommended with rationale;
- **approved** or **rejected** — a consequential proposal has been decided;
- **applied** — an approved action was executed and verified.

These states prevent a finding, suggestion, and completed transformation from
being represented as the same event.

## Verification levels

Use the strongest applicable verification level:

1. **Contract verification** — inputs and outputs satisfy the declared schema.
2. **Behavioral verification** — expected decisions hold on shared fixtures.
3. **Statistical verification** — populations, derivations, estimates,
   uncertainty, and interpretations are defensible.
4. **Independent replication** — a separate implementation reproduces the
   material result, preferably across R and Python when both are available.

Cross-language agreement is evidence, not proof. Matching implementations can
share the same conceptual error, so independent statistical review remains
necessary for consequential use.

## Minimum evaluation dimensions

Every skill's rubric must assess:

- correctness and appropriateness;
- recognition of missing context;
- assumption handling;
- preservation of data and analytical provenance;
- uncertainty and limitation communication;
- robustness to statistically meaningful perturbations;
- resistance to unsupported causal or inferential claims;
- reproducibility and, where applicable, independent replication.

## Public and enterprise boundary

The standard, reference behavior, representative fixtures, and basic evaluation
methods are public. Private benchmark libraries, organization-specific rules,
regulated workflows, scoring internals, governance, and production monitoring
may remain enterprise assets. Public examples must still be substantive enough
to make claims about a skill testable.

## Definition of ready

A skill is ready for an initial public release when:

- its scope and non-goals are explicit;
- all five required capabilities are represented;
- ambiguous inputs trigger an appropriate stop or context request;
- consequential actions are traceable and never silently applied;
- at least one routine, one ambiguous, and one failure case are tested;
- implemented R and Python behaviors agree on shared fixtures;
- limitations and human-review requirements are documented.
