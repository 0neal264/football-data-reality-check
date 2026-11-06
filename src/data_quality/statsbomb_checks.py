
import pandas as pd

from src.data_quality.rules import ValidationIssue


def check_event_ids(df: pd.DataFrame) -> list[ValidationIssue]:
    """Check that event IDs are present and unique."""

    issues = []

    if "event_id" not in df.columns:
        return [
            ValidationIssue(
                rule="required_column",
                row_index="DATASET",
                column="event_id",
                message="Required column 'event_id' is missing.",
            )
        ]

    for index in df.index[df["event_id"].isna()]:
        issues.append(
            ValidationIssue(
                rule="missing_event_id",
                row_index=index,
                column="event_id",
                message="Event ID is missing.",
            )
        )

    duplicates = df["event_id"].duplicated(keep="first")

    for index in df.index[duplicates]:
        issues.append(
            ValidationIssue(
                rule="duplicate_event_id",
                row_index=index,
                column="event_id",
                message="Duplicate event ID found.",
                value=df.at[index, "event_id"],
            )
        )

    return issues


def check_event_types(df: pd.DataFrame) -> list[ValidationIssue]:
    """Check that every event has an event type."""

    if "event_type" not in df.columns:
        return [
            ValidationIssue(
                rule="required_column",
                row_index="DATASET",
                column="event_type",
                message="Required column 'event_type' is missing.",
            )
        ]

    issues = []

    for index, value in df["event_type"].items():
        if pd.isna(value) or not str(value).strip():
            issues.append(
                ValidationIssue(
                    rule="missing_event_type",
                    row_index=index,
                    column="event_type",
                    message="Event type is missing.",
                    value=value,
                )
            )

    return issues


def check_pitch_coordinates(
    df: pd.DataFrame,
) -> list[ValidationIssue]:
    """Check that available event coordinates are within pitch bounds."""

    issues = []

    required = ["x", "y"]

    for column in required:
        if column not in df.columns:
            issues.append(
                ValidationIssue(
                    rule="required_column",
                    row_index="DATASET",
                    column=column,
                    message=f"Required column '{column}' is missing.",
                )
            )

    if any(column not in df.columns for column in required):
        return issues

    for index, row in df.iterrows():
        x = row["x"]
        y = row["y"]

        # Some event types legitimately have no location.
        if pd.isna(x) and pd.isna(y):
            continue

        if pd.isna(x) or pd.isna(y):
            issues.append(
                ValidationIssue(
                    rule="incomplete_coordinates",
                    row_index=index,
                    column="x,y",
                    message="Only one of the two coordinates is available.",
                    value=f"x={x}, y={y}",
                )
            )
            continue

        try:
            x = float(x)
            y = float(y)
        except (TypeError, ValueError):
            issues.append(
                ValidationIssue(
                    rule="coordinate_type",
                    row_index=index,
                    column="x,y",
                    message="Coordinates must be numeric.",
                    value=f"x={x}, y={y}",
                )
            )
            continue

        if not (0 <= x <= 120 and 0 <= y <= 80):
            issues.append(
                ValidationIssue(
                    rule="coordinate_bounds",
                    row_index=index,
                    column="x,y",
                    message="Coordinates are outside the 120 x 80 pitch.",
                    value=f"x={x}, y={y}",
                )
            )

    return issues


def check_shot_xg(df: pd.DataFrame) -> list[ValidationIssue]:
    """Check that shot xG values are present and between 0 and 1."""

    required = ["event_type", "shot_xg"]

    for column in required:
        if column not in df.columns:
            return [
                ValidationIssue(
                    rule="required_column",
                    row_index="DATASET",
                    column=column,
                    message=f"Required column '{column}' is missing.",
                )
            ]

    shots = df[df["event_type"] == "Shot"]
    issues = []

    for index, value in shots["shot_xg"].items():

        if pd.isna(value):
            issues.append(
                ValidationIssue(
                    rule="missing_shot_xg",
                    row_index=index,
                    column="shot_xg",
                    message="Shot is missing its xG value.",
                )
            )
            continue

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            issues.append(
                ValidationIssue(
                    rule="shot_xg_type",
                    row_index=index,
                    column="shot_xg",
                    message="Shot xG must be numeric.",
                    value=value,
                )
            )
            continue

        if not 0 <= numeric_value <= 1:
            issues.append(
                ValidationIssue(
                    rule="shot_xg_range",
                    row_index=index,
                    column="shot_xg",
                    message="Shot xG must be between 0 and 1.",
                    value=value,
                )
            )

    return issues


def check_shot_outcomes(df: pd.DataFrame) -> list[ValidationIssue]:
    """Check that every shot has an outcome."""

    required = ["event_type", "shot_outcome"]

    for column in required:
        if column not in df.columns:
            return [
                ValidationIssue(
                    rule="required_column",
                    row_index="DATASET",
                    column=column,
                    message=f"Required column '{column}' is missing.",
                )
            ]

    shots = df[df["event_type"] == "Shot"]
    issues = []

    for index, value in shots["shot_outcome"].items():
        if pd.isna(value) or not str(value).strip():
            issues.append(
                ValidationIssue(
                    rule="missing_shot_outcome",
                    row_index=index,
                    column="shot_outcome",
                    message="Shot is missing its outcome.",
                    value=value,
                )
            )

    return issues
