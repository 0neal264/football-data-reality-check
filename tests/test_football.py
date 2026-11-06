import pandas as pd

from src.data_quality.football import check_pitch_coordinates


def test_pitch_coordinates_flags_values_outside_configured_pitch():
    df = pd.DataFrame({"x": [10, 121], "y": [20, 40]})
    issues = check_pitch_coordinates(df)
    assert len(issues) == 1
    assert issues[0].column == "x"


def test_pitch_coordinates_does_not_treat_missing_values_as_out_of_bounds():
    df = pd.DataFrame({"x": [None], "y": [20]})
    assert check_pitch_coordinates(df) == []


def test_pitch_coordinates_reports_missing_coordinate_column():
    df = pd.DataFrame({"x": [10]})
    issues = check_pitch_coordinates(df)
    assert len(issues) == 1
    assert issues[0].column == "y"
