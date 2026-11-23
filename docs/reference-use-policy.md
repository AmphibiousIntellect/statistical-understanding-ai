# External reference use policy

SUAI is public and open source. Its specifications, examples, fixtures, and code
must be independently created and redistributable. This policy governs how
outside material may inform the project.

## Principles

1. **Independent specifications.** Write specifications from the underlying
   statistical and engineering principles and from public, citable sources.
   Do not reproduce another work's structure, prose, or examples.
2. **Original examples.** Examples, diagrams, exercises, and test cases are
   written for this repository.
3. **Synthetic fixtures.** Fixtures are small, synthetic, and contain no real
   people, organizations, or measurements. Do not derive fixtures from
   restricted data.
4. **Licensed dependencies.** Dependencies must carry a license compatible with
   the repository's MIT license and be declared in the project's manifests.
5. **No restricted or proprietary sources in public files.** Restricted and
   proprietary third-party material is not named, quoted, reproduced, or
   redistributed in the public repository. This includes manuals, training
   materials, benchmarks, proprietary test suites, and licensed datasets.
6. **No lightly paraphrased copying.** Rewording a restricted source is still
   copying. If a document or test could not be written without the source in
   front of you, do not contribute it.

## What to cite

Public references that informed a design (for example, documentation for an
open-source package or a published method) may be cited by title and link.
Citing a public source does not license copying it; follow the source's license.

## Contributor declaration

If a contribution was informed by restricted or proprietary references, the pull
request must:

- identify the **public** citations that support the content;
- confirm that its prose, examples, fixtures, and implementation were created
  independently of the restricted material;
- not name or describe the restricted material.

If you cannot make that confirmation, do not submit the contribution.

## Review

Maintainers may ask for the public sources behind a specification, example, or
fixture, and may decline or remove contributions that do not meet this policy.
Related boundaries are in the [open-core document](open-core.md) and the
[contributing guide](../CONTRIBUTING.md).
