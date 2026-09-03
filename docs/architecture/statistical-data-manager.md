# Statistical Data Manager architecture

The skill has one conceptual specification and two execution engines.

```text
Shared protocol and schemas
          |
   statistical reasoning
      /           \
 R reference   Python reference
      \           /
 shared fixtures and behavioral tests
```

Both engines produce a profile and a list of findings. A finding distinguishes
the observed evidence from its statistical implication and any proposed action.
Consequential transformations require explicit approval and must produce an
audit event. Cross-language parity means equivalent decisions and outputs where
language differences do not make equivalence impossible; it does not require
identical internal code.
