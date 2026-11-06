
import pandas as pd


def calculate_team_statistics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate match statistics for each team."""

    teams = sorted(df["team"].dropna().unique())

    results = []

    for team in teams:

        team_events = df[df["team"] == team]

        # Passing statistics
        passes = team_events[
            team_events["event_type"] == "Pass"
        ]

        passes_attempted = len(passes)

        passes_completed = int(
            passes["pass_complete"].eq(True).sum()
        )

        pass_accuracy = (
            passes_completed / passes_attempted * 100
            if passes_attempted > 0 else 0
        )

        # Shooting statistics
        shots = team_events[
            team_events["event_type"] == "Shot"
        ]

        shots_taken = len(shots)

        goals = int(shots["is_goal"].sum())

        total_xg = shots["shot_xg"].sum()

        # Distinct possessions attributed to the team
        possessions = df.loc[
            df["possession_team"] == team,
            "possession",
        ].nunique()

        results.append({
            "team": team,
            "passes_attempted": passes_attempted,
            "passes_completed": passes_completed,
            "pass_accuracy_pct": round(pass_accuracy, 2),
            "shots": shots_taken,
            "goals": goals,
            "total_xg": round(total_xg, 3),
            "possessions": possessions,
        })

    return pd.DataFrame(results)
