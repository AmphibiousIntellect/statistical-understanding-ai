# SUAI six-domain framework

Statistical understanding is the capacity to reason appropriately about data,
variation, uncertainty, evidence, and inference; recognize the assumptions and
limitations governing what can be learned; and adapt conclusions when those
conditions change.

The domains are interacting dimensions, not a linear maturity ladder. A system
may know statistical vocabulary while failing to inspect data correctly, or
produce executable code while exercising poor judgment.

| Domain | Central question | Example evidence |
|---|---|---|
| Data Management & Data Quality | Does the system understand the structure, provenance, and limitations of the data? | Detects a suspicious `999` without assuming it is an error |
| Statistical Knowledge & Problem Solving | Does it know and correctly apply statistical concepts and methods? | Selects and computes an appropriate method |
| Statistical Reasoning with Data | Can it connect empirical structure to analysis and evidence? | Recognizes dependence in repeated observations |
| Uncertainty & Probabilistic Reasoning | Does it represent uncertainty coherently and communicate limits? | Distinguishes absence of evidence from evidence of absence |
| Causal vs. Associational Reasoning | Does it distinguish association, prediction, and causal effects? | Refuses an unsupported causal interpretation |
| Statistical Judgment | Can it decide what is defensible and when more information or human review is needed? | Requests the estimand or missingness assumptions before proceeding |

Each domain document supplies a working definition, observable capabilities,
and candidate benchmark patterns. These are public research constructs, not a
claim that a single score fully captures statistical understanding.
