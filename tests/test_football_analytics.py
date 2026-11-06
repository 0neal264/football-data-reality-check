
import pandas as pd

from src.data_quality.football_analytics import calculate_team_statistics


def test_calculate_team_statistics():
    df = pd.DataFrame([
        {
            "team": "Liverpool",
            "event_type": "Pass",
            "pass_complete": True,
            "is_goal": False,
            "shot_xg": None,
            "possession": 1,
            "possession_team": "Liverpool",
        },
        {
            "team": "Liverpool",
            "event_type": "Pass",
            "pass_complete": False,
            "is_goal": False,
            "shot_xg": None,
            "possession": 1,
            "possession_team": "Liverpool",
        },
        {
            "team": "Liverpool",
            "event_type": "Shot",
            "pass_complete": None,
            "is_goal": True,
            "shot_xg": 0.5,
            "possession": 2,
            "possession_team": "Liverpool",
        },
        {
            "team": "Real Madrid",
            "event_type": "Pass",
            "pass_complete": True,
            "is_goal": False,
            "shot_xg": None,
            "possession": 3,
            "possession_team": "Real Madrid",
        },
        {
            "team": "Real Madrid",
            "event_type": "Shot",
            "pass_complete": None,
            "is_goal": False,
            "shot_xg": 0.3,
            "possession": 3,
            "possession_team": "Real Madrid",
        },
    ])

    result = calculate_team_statistics(df)

    liverpool = result[result["team"] == "Liverpool"].iloc[0]
    madrid = result[result["team"] == "Real Madrid"].iloc[0]

    assert liverpool["passes_attempted"] == 2
    assert liverpool["passes_completed"] == 1
    assert liverpool["pass_accuracy_pct"] == 50.0
    assert liverpool["shots"] == 1
    assert liverpool["goals"] == 1
    assert liverpool["total_xg"] == 0.5
    assert liverpool["possessions"] == 2

    assert madrid["passes_attempted"] == 1
    assert madrid["passes_completed"] == 1
    assert madrid["pass_accuracy_pct"] == 100.0
    assert madrid["shots"] == 1
    assert madrid["goals"] == 0
    assert madrid["total_xg"] == 0.3
    assert madrid["possessions"] == 1
