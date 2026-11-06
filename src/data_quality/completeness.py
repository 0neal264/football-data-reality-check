
import pandas as pd


def profile_event_field_completeness(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Measure field completeness only for event types
    where those fields are relevant.
    """

    field_requirements = {
        "shot_xg": "Shot",
        "shot_outcome": "Shot",
        "pass_end_x": "Pass",
        "pass_end_y": "Pass",
        "pass_length": "Pass",
    }

    results = []

    for field, event_type in field_requirements.items():

        relevant_events = df[
            df["event_type"] == event_type
        ]

        if field not in df.columns:
            results.append({
                "event_type": event_type,
                "field": field,
                "relevant_events": len(relevant_events),
                "missing_values": None,
                "completeness_percentage": None,
                "status": "Column missing",
            })
            continue

        total = len(relevant_events)
        missing = relevant_events[field].isna().sum()

        completeness = (
            (total - missing) / total * 100
            if total > 0 else None
        )

        results.append({
            "event_type": event_type,
            "field": field,
            "relevant_events": total,
            "missing_values": int(missing),
            "completeness_percentage": (
                round(completeness, 2)
                if completeness is not None else None
            ),
            "status": (
                "Complete" if missing == 0
                else "Missing values detected"
            ) if total > 0 else "No relevant events",
        })

    return pd.DataFrame(results)
