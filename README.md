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

## Skill #001: Statistical Data Manager

The first reference skill applies statistical reasoning before changing data:

**Inspect → Profile → Validate → Diagnose → Propose → Transform → Verify → Document**

The specification is language-agnostic. Starter implementations are provided
for both [Python](skills/statistical-data-manager/python/README.md) and
[R](skills/statistical-data-manager/r/README.md), with shared fixtures and
behavioral expectations. The central safety principle is:

> Never clean data without preserving the reasoning behind the cleaning decision.

This initial version profiles data and identifies issues. It does not silently
apply consequential transformations.

## Open-core boundary

This repository contains the public framework, documentation, starter tests,
shared schemas, examples, and reference implementations. Proprietary enterprise
assets—advanced/adversarial validation suites, private benchmark libraries,
scoring internals, regulated-industry modules, organization-specific rules,
governance workflows, and production monitoring—are intentionally not stored
here. See [Open Core](docs/open-core.md).

## Quick start

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

Early public scaffold. The framework, protocol, and APIs will evolve in public.
Contributions should preserve cross-language behavioral parity and make a clear
distinction between detection, recommendation, and mutation.

## License

MIT License. See [LICENSE](LICENSE).
