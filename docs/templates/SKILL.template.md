---
name: skill-name
description: One precise sentence that says when to activate this skill and what it does. Name the task, the inputs, and the boundary.
---

# Skill name

Follow the [Amphibious Skill Standard](../amphibious-skill-standard.md) and the
shared protocol in `spec/protocol.md`. Replace every bracketed prompt below and
delete this paragraph. Links here are relative to the template; adjust them when
you copy it into `skills/<name>/`.

## Scope and non-goals

- **In scope:** [the statistical task this skill performs]
- **Out of scope:** [adjacent tasks it must not attempt, and where they belong]

## Reason

[Identify the objective, the estimand or target when applicable, the study and
data structure, required context, assumptions, and plausible alternatives
before selecting an operation.]

## Execute

[State the traceable steps. Follow the shared specification rather than
language-specific defaults. Name the engine routing and coordination mode, and
what each engine contributes.]

## Verify

[List the checks on inputs, intermediate decisions, and outputs, and the
strongest applicable verification level: contract, behavioral, statistical, or
independent replication.]

## Explain

[State what the skill reports: the question addressed, evidence used, decisions
made, assumptions, limitations, and the provenance needed to reproduce the
result. Separate observations from interpretations and recommendations.]

## Know when not to proceed

[List the missing information that must stop the skill and request context. State
that anomaly detection never grants permission to mutate data, select a model, or
make a stronger claim than the design and evidence support.]

## Decision states

[Map the skill's outputs to observed, needs context, proposed, approved or
rejected, and applied. Say where a consequential action requires explicit
approval.]

## Required contents checklist

- [ ] `SKILL.md` with a precise activation description
- [ ] A language-agnostic specification (inputs, outputs, decision states, invariants, stop conditions)
- [ ] Fixtures with at least one **routine**, one **ambiguous**, and one **failure** case
- [ ] Behavioral tests for the statistically important invariants
- [ ] An evaluation rubric describing expected, weak, and unsafe behavior
- [ ] Provenance requirements for consequential decisions and generated outputs
- [ ] Engine-routing, interoperability, and parity notes if R or Python is implemented
- [ ] Explicit scope, non-goals, limitations, and human-review requirements

## Rubric dimensions

Assess at least: correctness and appropriateness; recognition of missing context;
assumption handling; preservation of data and analytical provenance; uncertainty
and limitation communication; robustness to meaningful perturbations; resistance to
unsupported causal or inferential claims; reproducibility and independent
replication.

## Public and enterprise boundary

[Confirm all fixtures are synthetic and licensed for redistribution, and that no
private benchmarks, proprietary rules, or credentials are included. See the
[external reference use policy](../reference-use-policy.md) and
[open-core boundary](../open-core.md).]
