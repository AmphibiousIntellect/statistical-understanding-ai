# Positron and agent development workflow

How to set up and work on this repository in [Positron](https://positron.posit.co/),
alone or with a local coding agent. The repository has two test suites (Python and
R), one set of schemas, and documentation whose internal links are tested.

## Prerequisites

- Positron, with Python 3.10 or later and R installed
- `git`
- For the draft v0.2 contract tests: Python packages `jsonschema` (4.18 or later)
  and `rfc3339-validator`, installed through the project's `test` extra

## One-time setup

From the repository root, create an ignored, repository-local virtual environment
and install only the project's declared dependencies:

```bash
python3.12 -m venv .venv
```

```bash
.venv/bin/python -m pip install -e "skills/statistical-data-manager/python[test]"
```

`.venv/` is in `.gitignore`. Do not install packages globally.

In Positron, choose `.venv` as the Python interpreter for the workspace using the
interpreter selector, and choose your installed R for the R session. For R, the
only package needed for the existing tests is `testthat`:

```r
install.packages("testthat")
```

## Run the checks

Python (includes the schema, state, replay, link, and repository-hygiene tests):

```bash
cd skills/statistical-data-manager/python && ../../../.venv/bin/python -m unittest discover -s tests
```

R, from the repository root:

```bash
Rscript -e 'testthat::test_dir("skills/statistical-data-manager/r/tests/testthat")'
```

Continuous integration runs the same two commands.

## Branches and pull requests

- Work on a feature branch. Do not push directly to `main`.
- Keep a change small and testable, and say whether it is shared, R-led,
  Python-led, or collaborative (see [CONTRIBUTING](../../CONTRIBUTING.md)).
- Changes to accepted architecture need a new decision record under
  `docs/decisions/`.
- Changes to the draft contracts follow
  [`schemas/v0.2/README.md`](../../schemas/v0.2/README.md). Do not edit the
  implemented v0.1 schemas in `schemas/` as part of a draft change.

## Working with a local agent

Give the agent these rules before it edits anything:

1. **Read first.** Start with `README.md`, `CONTRIBUTING.md`, the
   [Amphibious Skill Standard](../amphibious-skill-standard.md), and the relevant
   ADR. Run the existing tests before changing code.
2. **Plan, then wait.** For non-trivial work, the agent proposes files, tests, and
   acceptance criteria and waits for approval.
3. **Detection is not permission to mutate data.** Never delete duplicate-looking
   rows automatically, invent missing analytical context, or fall back silently
   from one engine to another. Preserve R/Python disagreements.
4. **Stay public-safe.** Synthetic data only. No credentials, private benchmarks,
   or proprietary material (see the
   [reference use policy](../reference-use-policy.md) and
   [open-core boundary](../open-core.md)).
5. **Report faithfully.** State which tests ran, which were skipped, and why.

## Pull request checklist

- [ ] Python and R suites pass locally, and CI is green
- [ ] Every internal Markdown link resolves (part of the Python tests)
- [ ] New behavior has routine, ambiguous, and failure cases where applicable
- [ ] No `.pyc`, `__pycache__`, `.venv`, or other generated files are committed
- [ ] Statistical assumptions and limitations are explained in the description
- [ ] No private data, credentials, or proprietary material is included
