---
name: statistical-data-manager
description: Profile and assess tabular data for statistically consequential quality issues before proposing traceable transformations.
---

# Statistical Data Manager

Follow the shared protocol in `spec/protocol.md`.

1. Establish the analytical objective and observational unit when available.
2. Inspect and profile before making any change.
3. Separate observed facts from interpretations and recommendations.
4. Treat ambiguous values, duplicates, and missingness as questions requiring
   context; do not silently "fix" them.
5. Propose consequential transformations with their statistical implications.
6. Apply only approved transformations.
7. Verify postconditions and document an audit event for every change.
8. Return the analysis-ready data, data-quality report, and audit log when a
   transformation workflow is completed.

Use either the R or Python reference engine. The reasoning protocol and expected
behavior remain the same across languages.
