"""Conservative, auditable starter checks for tabular data."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

import pandas as pd


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Literal["info", "warning", "error"]
    status: Literal["observed", "needs_context", "proposed", "approved", "applied", "rejected"]
    message: str
    evidence: dict[str, Any]
    statistical_implication: str | None
    proposed_action: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InspectionResult:
    profile: dict[str, Any]
    findings: tuple[Finding, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def profile(data: pd.DataFrame) -> dict[str, Any]:
    """Return deterministic, JSON-friendly structural and quality summaries."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    return {
        "row_count": int(len(data)),
        "column_count": int(len(data.columns)),
        "columns": [str(column) for column in data.columns],
        "types": {str(column): str(dtype) for column, dtype in data.dtypes.items()},
        "missing_count": {
            str(column): int(count) for column, count in data.isna().sum().items()
        },
        "unique_count": {
            str(column): int(count)
            for column, count in data.nunique(dropna=False).items()
        },
        "duplicate_row_count": int(data.duplicated(keep=False).sum()),
    }


def inspect(data: pd.DataFrame) -> InspectionResult:
    """Profile data and report issues without applying transformations."""
    data_profile = profile(data)
    findings: list[Finding] = []

    duplicate_count = data_profile["duplicate_row_count"]
    if duplicate_count:
        findings.append(
            Finding(
                code="duplicate_rows",
                severity="warning",
                status="needs_context",
                message=f"{duplicate_count} rows participate in exact duplicate groups.",
                evidence={"duplicate_row_count": duplicate_count},
                statistical_implication=(
                    "Deleting legitimate repeated observations can change sample size, "
                    "variance estimates, and the analysis population."
                ),
                proposed_action=(
                    "Review the observational unit, candidate key, and repeat structure "
                    "before deciding whether any row is redundant."
                ),
            )
        )

    return InspectionResult(profile=data_profile, findings=tuple(findings))
