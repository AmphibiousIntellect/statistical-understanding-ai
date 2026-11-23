"""Shared helpers for the draft v0.2 contract tests (test-only; not product code)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPO_ROOT = Path(__file__).resolve().parents[4]
V02 = REPO_ROOT / "schemas" / "v0.2"
EXAMPLES = V02 / "examples"
FIXTURES = REPO_ROOT / "skills" / "statistical-data-manager" / "fixtures"

SCHEMA_FILES = {
    "common": "common.schema.json",
    "finding": "finding.schema.json",
    "action": "action.schema.json",
    "approval": "approval.schema.json",
    "engine-result": "engine-result.schema.json",
    "audit-event": "audit-event.schema.json",
    "run-manifest": "run-manifest.schema.json",
    "trim-whitespace-action": "extensions/trim-whitespace.action.schema.json",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_schema(relative: str) -> dict[str, Any]:
    return load_json(V02 / relative)


def _build_registry() -> Registry:
    registry: Registry = Registry()
    for relative in SCHEMA_FILES.values():
        schema = load_schema(relative)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


REGISTRY = _build_registry()


def make_validator(relative: str) -> Draft202012Validator:
    """The only way tests build validators: Draft 2020-12 with format checking."""
    return Draft202012Validator(
        load_schema(relative),
        registry=REGISTRY,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def collect_errors(validator: Draft202012Validator, instance: Any) -> list[dict[str, str]]:
    return [
        {"validator": str(error.validator), "json_path": error.json_path, "message": error.message}
        for error in validator.iter_errors(instance)
    ]


def schema_for_example(name: str) -> str:
    """Valid examples are named `<schema-key>.<description>.json`."""
    key = name.split(".", 1)[0]
    return SCHEMA_FILES[key]


def canonical_json(document: Any) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def action_digest(action: dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON of the action document exactly as emitted."""
    return hashlib.sha256(canonical_json(action).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
