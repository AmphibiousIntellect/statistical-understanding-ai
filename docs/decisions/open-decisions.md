# Open decisions

Items that are recorded but deliberately not resolved. Each is a review item, not
a change.

## 1. Ownership and publication of the schema `$id` base

- **Status:** unresolved.
- **Context:** The schemas use the base `https://amphibiousintellect.org/suai/`
  in their `$id` values, including the draft v0.2 files under `/v0.2/`. It has not
  been confirmed that the project controls or will publish that domain.
- **Current handling:** No `$id` was changed and no replacement was invented. The
  draft v0.2 schemas reuse the existing base so they stay consistent. All `$ref`
  resolution in tests is local and offline.
- **Needed:** A statement of who owns the domain and whether schemas will be
  published there. Until then no consumer should rely on the URLs resolving.
- **Blocks:** promotion of the v0.2 contracts (see `schemas/v0.2/README.md`).

## 2. Contact address in `DESCRIPTION`

- **Status:** unresolved.
- **Context:** `skills/statistical-data-manager/r/DESCRIPTION` contains an
  author contact address. Whether that address is intended to be public has not
  been confirmed.
- **Current handling:** Left exactly as it is, and not copied anywhere else in the
  repository.
- **Needed:** The maintainers' confirmation that the address is intended to be
  public, or a different public contact.

## 3. Value capture for real data

- **Status:** noted for a later decision.
- **Context:** Draft actions support several `value_capture_policy` options so
  that raw before-and-after values are never required. The synthetic examples use
  record references only. A policy for real (non-synthetic) data has not been
  defined.
- **Needed:** Before any real-data use, decide which policies are acceptable and
  the hashing method (hashes of low-entropy values can be guessed without a
  keyed or salted method).
