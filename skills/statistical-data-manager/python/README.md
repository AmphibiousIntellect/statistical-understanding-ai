# Python reference implementation

Behavior is evaluated using the shared fixtures and
[`evaluation/rubric.md`](../evaluation/rubric.md).

Install from this directory with `python -m pip install -e .`, then run
`python -m unittest discover -s tests`. The starter API provides `profile()` and `inspect()` for pandas data
frames. It reports ambiguous duplicate rows but never deletes them.

Within the coordinated system, Python is expected to lead data ingestion,
large-scale processing, AI/ML integration, APIs, orchestration, and production
validation. It exchanges findings and audit events with R through shared
contracts rather than duplicating every R capability.
