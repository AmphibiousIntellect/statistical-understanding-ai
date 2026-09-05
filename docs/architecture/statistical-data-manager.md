# Statistical Data Manager architecture

The [R package strategy](r-package-strategy.md) maps package capabilities and
selection criteria while keeping the shared reasoning protocol package-agnostic.

The Statistical Data Manager is one coordinated statistical reasoning system
with two complementary execution engines.

```text
            Coordinator
                |
   shared reasoning, schemas, and audit layer
          /                         \
 R statistical engine       Python data/AI engine
          \                         /
        joint review and synthesis
```

The coordinator identifies the task, available context, statistical risk, and
required assurance. It assigns work to one or both engines, reconciles their
findings, and produces one traceable outcome.

## Complementary responsibilities

| R statistical engine | Python data/AI engine |
|---|---|
| Classical statistical methods | Data ingestion and engineering |
| Survival and longitudinal analysis | Large-scale processing |
| Mixed models and survey methods | Machine-learning and AI integration |
| Statistical diagnostics | APIs and workflow orchestration |
| Research-oriented reporting | Production schema validation |
| Specialized statistical packages | Unstructured and multimodal data |

These are routing preferences, not hard boundaries. The coordinator may select
either engine when its implementation, data support, or statistical method is
better suited to the task.

## Operating modes

### Collaborative mode

The default. R and Python perform different parts of one workflow and exchange
profiles, findings, proposals, and audit events through shared schemas.

### Native mode

One engine completes the task when collaboration would add complexity without
meaningful statistical or operational value.

### Independent validation mode

Both engines evaluate selected high-risk facts or decisions independently. A
disagreement becomes a finding requiring reconciliation or human review; it is
not silently averaged away.

## What must be shared

The engines must agree on common data facts, identifiers, finding semantics,
approval states, provenance, and audit structure. They must also follow the same
safety invariants: detection is not permission to mutate, ambiguity must remain
visible, and consequential changes require approval and verification.

They do not need identical algorithms, package choices, advanced capabilities,
or report wording. Cross-language equivalence is a targeted validation method,
not the product architecture.

A finding distinguishes observed evidence from its statistical implication and
any proposed action. Consequential transformations require explicit approval
and must produce an audit event regardless of which engine performs them.
