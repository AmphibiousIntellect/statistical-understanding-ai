# R package strategy for the Statistical Data Manager

The Statistical Data Manager should understand the R data ecosystem as a set of
capabilities and tradeoffs, not as a fixed list of packages. Package choice must
follow the data source, scale, required semantics, validation needs, and
reproducibility constraints.

The interface should follow readable tidy design while preserving metadata,
labels, parsing rules, missing-value semantics, group-processing assumptions,
ordering, and comparison behavior across supported data formats.

## Design rules

1. Keep the statistical reasoning and behavioral contract package-agnostic.
2. Prefer explicit parsing specifications over silent type guessing.
3. Preserve raw values before normalization or coercion.
4. Record the package, version, function, parameters, warnings, and affected
   observations for every consequential operation.
5. Treat package warnings and parsing problems as findings, not console noise.
6. Use optional adapters so the core skill does not require the entire ecosystem.
7. Test statistical behavior across package and language boundaries, not merely
   whether a function executes.

## Capability map

| Capability | Primary packages | Supporting packages | SUAI concern |
|---|---|---|---|
| Delimited import and parsing | `readr`, `vroom` | base `utils` | Preserve parsing problems, locale, encoding, declared missing codes, and column specifications |
| Excel and labelled statistical files | `readxl`, `haven` | `rio`, `openxlsx2` | Preserve labels, date systems, missing codes, sheet provenance, and source-specific semantics |
| Core transformation | `dplyr`, `tidyr` | base R, `purrr` | Make grouping, joins, reshaping, row changes, and type coercions explicit |
| High-performance tables | `data.table` | `dtplyr` | Avoid hidden copies or by-reference mutation; verify keys and row order |
| Strings and encodings | `stringr`, `stringi` | base R | Preserve original text; distinguish whitespace, case, Unicode, encoding, and semantic normalization |
| Dates and times | `lubridate`, `clock` | base `Date`/`POSIXct` | Detect ambiguous orders, time zones, partial dates, numeric date origins, daylight-saving transitions, and impossible dates |
| Categorical data | `forcats` | base factors, `labelled` | Detect spelling/case variants, unused levels, novel levels, ordering errors, labels, and invalid recoding |
| Missing data description | `naniar`, `VIM` | `visdat`, `mice` | Separate representation, pattern diagnosis, structural missingness, and modeling/imputation decisions |
| Names and routine diagnostics | `janitor` | `snakecase` | Name cleaning and duplicate detection remain proposals when meaning could change |
| Declarative validation | `pointblank`, `validate` | `checkmate`, `assertr` | Apply declared rules with thresholds and evidence; do not invent domain constraints |
| Schema and interchange | `jsonlite`, `jsonvalidate`, `yaml` | `vctrs` | Validate machine-readable findings, specifications, audit events, and stable types |
| Large and multi-file data | `arrow`, `duckdb` | `dbplyr`, `DBI`, `duckplyr` | Preserve lazy-query semantics, schemas, filters, and collection boundaries |
| Reproducible pipelines | `targets` | `renv`, `here`, `fs` | Capture dependency versions, inputs, outputs, seeds, paths, and invalidation rules |
| Data comparison and verification | `waldo`, `diffdf` | `digest`, `testthat` | Compare values, types, labels, order, tolerances, and analysis populations |
| Quality reporting | `quarto`, `rmarkdown` | `gt`, `reactable` | Generate human-readable reports from the same machine-readable findings |

This is a capability inventory, not a requirement to import every package.

## Initial implementation tiers

### Tier 1 — core reference stack

- base R for stable primitives and minimal dependencies;
- `readr` for explicit delimited parsing and problem capture;
- `dplyr` and `tidyr` for transparent transformations;
- `stringr`/`stringi` for text and encoding diagnostics;
- `lubridate` plus `clock` for date/time parsing and validation;
- `forcats` for categorical-level operations;
- `janitor` for names, tabulations, and duplicate exploration;
- `pointblank` or `validate` for declared validation rules;
- `testthat` and `waldo` for behavioral verification;
- `jsonlite` for audit and finding outputs;
- `renv` for dependency capture.

### Tier 2 — scale and interoperability

- `data.table` for large in-memory data;
- `arrow` for Parquet, multi-file datasets, and R/Python interchange;
- `duckdb`, `DBI`, and `dbplyr` for larger-than-memory and database workflows;
- `haven` for labelled statistical data files and tagged missing values.

### Tier 3 — specialized adapters

Add domain-specific packages only when the related skill or module is specified
and tested. Examples include clinical standards, geospatial data, survey
designs, record linkage, and specialized missing-data workflows.

## Package-selection questions

Before selecting an implementation, the Data Manager should ask:

- What is the source format and which metadata can be lost on import?
- Are types declared, inferred, labelled, or mixed?
- Can the data fit safely in memory?
- Is the operation eager, lazy, database-backed, or by-reference?
- Must R and Python exchange the data without type degradation?
- Is the task detection, validation, transformation, visualization, or modeling?
- What evidence and reversal path will be recorded?
- Does the operation depend on locale, encoding, time zone, or external state?

## Near-term build sequence

1. Import and parsing diagnostics, including explicit missing-value codes.
2. String and categorical profiling without automatic normalization.
3. Date/time candidate detection, ambiguity reporting, and approved parsing.
4. Declarative validation-rule execution and structured findings.
5. Approved transformation plans with before/after verification and audit events.
6. Missingness-pattern reporting, clearly separated from imputation.
7. Arrow/DuckDB adapters and R/Python interoperability fixtures.
8. Metadata-preservation fixtures plus targeted cross-engine validation cases.

## Primary documentation reviewed

- [readr: rectangular text import and parsing](https://readr.tidyverse.org/)
- [tidyverse package inventory](https://tidyverse.tidyverse.org/reference/tidyverse_packages.html)
- [janitor: examining and cleaning dirty data](https://sfirke.github.io/janitor/)
- [pointblank: validation and table metadata](https://rstudio.github.io/pointblank/)
- [data.table documentation](https://rdatatable.gitlab.io/data.table/)
- [Apache Arrow R package](https://arrow.apache.org/docs/r/)
- [DuckDB R client](https://duckdb.org/docs/current/clients/r)
