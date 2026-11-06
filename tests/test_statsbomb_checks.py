
import pandas as pd

from src.data_quality.statsbomb_checks import (
    check_event_ids,
    check_event_types,
    check_pitch_coordinates,
    check_shot_xg,
    check_shot_outcomes,
)


def test_duplicate_event_ids_are_detected():
    df = pd.DataFrame({
        "event_id": ["a", "b", "a"]
    })

    issues = check_event_ids(df)

    assert len(issues) == 1
    assert issues[0].rule == "duplicate_event_id"
    assert issues[0].row_index == 2


def test_missing_event_type_is_detected():
    df = pd.DataFrame({
        "event_type": ["Pass", None]
    })

    issues = check_event_types(df)

    assert len(issues) == 1
    assert issues[0].row_index == 1


def test_coordinates_outside_pitch_are_detected():
    df = pd.DataFrame({
        "x": [60, 130],
        "y": [40, 90],
    })

    issues = check_pitch_coordinates(df)

    assert len(issues) == 1
    assert issues[0].rule == "coordinate_bounds"


def test_shot_xg_outside_range_is_detected():
    df = pd.DataFrame({
        "event_type": ["Shot", "Shot"],
        "shot_xg": [0.5, 1.5],
    })

    issues = check_shot_xg(df)

    assert len(issues) == 1
    assert issues[0].rule == "shot_xg_range"


def test_missing_shot_outcome_is_detected():
    df = pd.DataFrame({
        "event_type": ["Shot", "Pass"],
        "shot_outcome": [None, None],
    })

    issues = check_shot_outcomes(df)

    assert len(issues) == 1
    assert issues[0].rule == "missing_shot_outcome"
