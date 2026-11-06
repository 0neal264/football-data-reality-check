from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

import pandas as pd


@dataclass(frozen=True)
class ValidationIssue:
    """A single finding produced by a data-quality rule."""

    rule: str
    row_index: object
    column: str | None
    message: str
    value: object = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def check_required_columns(
    df: pd.DataFrame, required: list[str]
) -> list[ValidationIssue]:
    """Report required columns that are absent from a DataFrame."""
    return [
        ValidationIssue(
            rule="required_column",
            row_index="DATASET",
            column=column,
            message=f"Required column '{column}' is missing.",
        )
        for column in required
        if column not in df.columns
    ]


def check_missing_values(
    df: pd.DataFrame, columns: list[str] | None = None
) -> list[ValidationIssue]:
    """Find missing values in selected columns or all columns."""
    selected_columns = columns if columns is not None else list(df.columns)
    issues: list[ValidationIssue] = []

    for column in selected_columns:
        if column not in df.columns:
            issues.extend(check_required_columns(df, [column]))
            continue

        for row_index in df.index[df[column].isna()]:
            issues.append(
                ValidationIssue(
                    rule="missing_value",
                    row_index=row_index,
                    column=column,
                    message=f"Missing value in '{column}'.",
                )
            )
    return issues


def check_duplicate_values(
    df: pd.DataFrame, column: str
) -> list[ValidationIssue]:
    """Flag duplicate values after their first occurrence."""
    if column not in df.columns:
        return check_required_columns(df, [column])

    duplicate_mask = df[column].duplicated(keep="first")
    return [
        ValidationIssue(
            rule="duplicate_value",
            row_index=row_index,
            column=column,
            message=f"Duplicate value in '{column}'.",
            value=df.at[row_index, column],
        )
        for row_index in df.index[duplicate_mask]
    ]


def check_numeric_range(
    df: pd.DataFrame,
    column: str,
    minimum: float | None = None,
    maximum: float | None = None,
) -> list[ValidationIssue]:
    """Flag non-numeric and out-of-range non-null values."""
    if column not in df.columns:
        return check_required_columns(df, [column])

    numeric_values = pd.to_numeric(df[column], errors="coerce")
    issues: list[ValidationIssue] = []

    for row_index, original_value in df[column].items():
        if pd.isna(original_value):
            continue

        numeric_value = numeric_values.loc[row_index]
        if pd.isna(numeric_value):
            issues.append(
                ValidationIssue(
                    rule="numeric_type",
                    row_index=row_index,
                    column=column,
                    message=f"Value in '{column}' is not numeric.",
                    value=original_value,
                )
            )
            continue

        below_minimum = minimum is not None and numeric_value < minimum
        above_maximum = maximum is not None and numeric_value > maximum
        if below_minimum or above_maximum:
            issues.append(
                ValidationIssue(
                    rule="numeric_range",
                    row_index=row_index,
                    column=column,
                    message=(
                        f"Value in '{column}' is outside the allowed range "
                        f"[{minimum}, {maximum}]."
                    ),
                    value=original_value,
                )
            )

    return issues


def run_checks(
    df: pd.DataFrame,
    checks: list[Callable[[pd.DataFrame], list[ValidationIssue]]],
) -> pd.DataFrame:
    """Run validation functions and return findings in a standard format."""
    findings = [issue.to_dict() for check in checks for issue in check(df)]
    return pd.DataFrame(
        findings,
        columns=["rule", "row_index", "column", "message", "value"],
    )
