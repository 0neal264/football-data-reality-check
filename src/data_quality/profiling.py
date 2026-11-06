
import pandas as pd


def profile_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate missing values and percentages for every column."""

    profile = pd.DataFrame({
        "column": df.columns,
        "missing_count": df.isna().sum().values,
        "missing_percentage": (
            df.isna().mean().values * 100
        ).round(2),
        "data_type": df.dtypes.astype(str).values,
    })

    return profile.sort_values(
        "missing_percentage",
        ascending=False,
    )


def profile_event_types(df: pd.DataFrame) -> pd.DataFrame:
    """Count events by event type."""

    result = (
        df["event_type"]
        .value_counts(dropna=False)
        .rename_axis("event_type")
        .reset_index(name="event_count")
    )

    result["percentage"] = (
        result["event_count"] / len(df) * 100
    ).round(2)

    return result


def profile_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """Analyse coordinate availability by event type."""

    result = (
        df.groupby("event_type", dropna=False)
        .agg(
            total_events=("event_id", "size"),
            x_available=("x", "count"),
            y_available=("y", "count"),
        )
        .reset_index()
    )

    result["both_coordinates_available"] = (
        df.assign(
            both_coordinates=(
                df["x"].notna() & df["y"].notna()
            )
        )
        .groupby("event_type", dropna=False)[
            "both_coordinates"
        ]
        .sum()
        .values
    )

    result["coordinate_completeness_pct"] = (
        result["both_coordinates_available"]
        / result["total_events"] * 100
    ).round(2)

    return result.sort_values(
        "total_events",
        ascending=False,
    )


def profile_team_activity(df: pd.DataFrame) -> pd.DataFrame:
    """Count recorded events by team."""

    result = (
        df.groupby("team", dropna=False)
        .agg(
            total_events=("event_id", "size"),
            unique_players=("player", "nunique"),
        )
        .reset_index()
    )

    result["event_percentage"] = (
        result["total_events"] / len(df) * 100
    ).round(2)

    return result.sort_values(
        "total_events",
        ascending=False,
    )
