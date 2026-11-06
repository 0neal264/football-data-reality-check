from __future__ import annotations

import pandas as pd

from src.data_quality.rules import ValidationIssue, check_required_columns


def check_pitch_coordinates(
    df: pd.DataFrame,
    x_column: str = "x",
    y_column: str = "y",
    pitch_length: float = 120.0,
    pitch_width: float = 80.0,
) -> list[ValidationIssue]:
    """Flag football event coordinates outside configured pitch bounds.

    Confirm the coordinate convention and pitch dimensions for the selected
    data provider before using this rule on real match data.
    """
    missing_columns = check_required_columns(df, [x_column, y_column])
    if missing_columns:
        return missing_columns

    issues: list[ValidationIssue] = []
    for row_index, row in df.iterrows():
        for column, upper_bound in (
            (x_column, pitch_length),
            (y_column, pitch_width),
        ):
            original_value = row[column]
            if pd.isna(original_value):
                continue  # Missing values are reported by the generic rule.

            numeric_value = pd.to_numeric(
                pd.Series([original_value]), errors="coerce"
            ).iloc[0]
            if pd.isna(numeric_value):
                issues.append(
                    ValidationIssue(
                        rule="coordinate_type",
                        row_index=row_index,
                        column=column,
                        message=f"Coordinate '{column}' is not numeric.",
                        value=original_value,
                    )
                )
            elif numeric_value < 0 or numeric_value > upper_bound:
                issues.append(
                    ValidationIssue(
                        rule="coordinate_bounds",
                        row_index=row_index,
                        column=column,
                        message=(
                            f"Coordinate '{column}' must be between "
                            f"0 and {upper_bound}."
                        ),
                        value=original_value,
                    )
                )

    return issues
