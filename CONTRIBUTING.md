# Contributing

Thank you for helping define and test statistical understanding in AI.

## Principles

- Follow the [Amphibious Skill Standard](docs/amphibious-skill-standard.md).
- Separate statistical reasoning from language-specific execution.
- Do not silently mutate questionable data.
- Record the evidence, implication, and rationale for every proposal.
- Preserve R/Python interoperability and shared safety semantics.
- Require parity for common facts and contracts, not identical implementations.
- Let each engine own capabilities where its ecosystem is materially stronger.
- Use synthetic or appropriately licensed data only.
- Do not contribute confidential validation cases or enterprise assets.
- Follow the [external reference use policy](docs/reference-use-policy.md). Do
  not copy or lightly paraphrase proprietary manuals, examples, diagrams,
  training materials, or test suites into the repository.

## Workflow

1. Open an issue describing the capability or behavior.
2. Identify whether the change is shared, R-led, Python-led, or collaborative.
3. Add or update shared fixtures and expected behavior when parity is required.
4. Implement the smallest defensible change.
5. Run the relevant engine tests and any cross-engine contract tests.
6. Explain statistical assumptions and limitations in the pull request.

New skills should begin with the [skill template](docs/templates/SKILL.template.md)
and must include routine, ambiguous, and failure cases before an initial public
release.

Changes to the six-domain framework should include a motivating example and a
clear account of what the change makes measurable.

If a contribution was informed by restricted or proprietary references, the
pull request must identify the public citations and confirm that its prose,
examples, fixtures, and implementation were created independently.
