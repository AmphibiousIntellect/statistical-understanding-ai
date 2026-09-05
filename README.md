# Statistical Understanding in AI

> We build, evaluate, and validate statistical understanding in artificial intelligence.

Statistical Understanding in AI (SUAI) is an open-source initiative from
[Amphibious Intellect](https://github.com/AmphibiousIntellect). It asks a harder
question than whether an AI can produce a correct answer: can it reason
appropriately about data, variation, uncertainty, evidence, and inference—and
recognize when the available data do not justify the requested conclusion?

## The six-domain framework

1. [Data Management & Data Quality](docs/framework/01-data-management-and-quality.md)
2. [Statistical Knowledge & Problem Solving](docs/framework/02-statistical-knowledge-and-problem-solving.md)
3. [Statistical Reasoning with Data](docs/framework/03-statistical-reasoning-with-data.md)
4. [Uncertainty & Probabilistic Reasoning](docs/framework/04-uncertainty-and-probabilistic-reasoning.md)
5. [Causal vs. Associational Reasoning](docs/framework/05-causal-vs-associational-reasoning.md)
6. [Statistical Judgment](docs/framework/06-statistical-judgment.md)

The framework is described in [the framework overview](docs/framework/README.md).

## Amphibious Skill Standard

Every SUAI skill follows a shared five-part contract:

**Reason → Execute → Verify → Explain → Know when not to proceed**

The [Amphibious Skill Standard v0.1](docs/amphibious-skill-standard.md)
defines required skill contents, decision states, verification levels,
evaluation dimensions, and the initial release threshold. New skills begin from
the [skill template](docs/templates/SKILL.template.md).

## Skill #001: Statistical Data Manager

The first reference skill applies statistical reasoning before changing data:

**Inspect → Profile → Validate → Diagnose → Propose → Transform → Verify → Document**

The system has one shared statistical reasoning and audit layer with
complementary [Python](skills/statistical-data-manager/python/README.md) and
[R](skills/statistical-data-manager/r/README.md) execution engines. The engines
divide work according to their strengths, exchange findings through shared
schemas, and may independently validate selected high-risk decisions. The
central safety principle is:

> Never clean data without preserving the reasoning behind the cleaning decision.

This initial version profiles data and identifies issues. It does not silently
apply consequential transformations.

The [R package strategy](docs/architecture/r-package-strategy.md) defines how
the Data Manager will select packages for importing, dates, strings,
categoricals, missingness, validation, scale, and reproducibility without
coupling statistical judgment to any one library.

[Architecture Decision 0001](docs/decisions/0001-complementary-r-python-engines.md)
records the decision to use complementary R and Python engines with
collaborative, native, and independent-validation modes.

The [external reference use policy](docs/reference-use-policy.md) requires
independent specifications, original examples, synthetic fixtures, and licensed
dependencies. Restricted and proprietary third-party sources are not named,
quoted, reproduced, or redistributed in the public repository.

## Open-core boundary

This repository contains the public framework, documentation, starter tests,
shared schemas, examples, and reference implementations. Proprietary enterprise
assets—advanced/adversarial validation suites, private benchmark libraries,
scoring internals, regulated-industry modules, organization-specific rules,
governance workflows, and production monitoring—are intentionally not stored
here. See [Open Core](docs/open-core.md).

## Quick start

For the complete Positron and local-agent setup, see the
[Positron and Agent Development Workflow](docs/development/positron-agent-workflow.md).

Python:

```bash
cd skills/statistical-data-manager/python
python -m pip install -e .
python -m unittest discover -s tests
```

R:

```r
install.packages("testthat")
testthat::test_dir("skills/statistical-data-manager/r/tests/testthat")
```

## Status

Early public scaffold. The framework, skill standard, protocol, and APIs will
evolve in public.
Contributions should preserve cross-language interoperability and shared safety
semantics while allowing language-specific capabilities. Every implementation
must distinguish detection, recommendation, approval, and mutation.

## License

MIT License. See [LICENSE](LICENSE).
