import pandas as pd

from src.data_quality.rules import (
    check_duplicate_values,
    check_missing_values,
    check_numeric_range,
    check_required_columns,
    run_checks,
)


def test_required_columns_reports_missing_column():
    df = pd.DataFrame({"event_id": [1]})
    issues = check_required_columns(df, ["event_id", "timestamp"])
    assert len(issues) == 1
    assert issues[0].column == "timestamp"


def test_missing_values_reports_row_and_column():
    df = pd.DataFrame({"player": ["A", None]})
    issues = check_missing_values(df)
    assert len(issues) == 1
    assert issues[0].row_index == 1
    assert issues[0].column == "player"


def test_duplicate_values_flags_later_occurrence():
    df = pd.DataFrame({"event_id": [1, 2, 1]})
    issues = check_duplicate_values(df, "event_id")
    assert len(issues) == 1
    assert issues[0].row_index == 2


def test_numeric_range_flags_out_of_range_and_non_numeric():
    df = pd.DataFrame({"score": [0.5, 1.2, "unknown", None]})
    issues = check_numeric_range(df, "score", minimum=0, maximum=1)
    assert [issue.rule for issue in issues] == ["numeric_range", "numeric_type"]


def test_run_checks_returns_standard_report_columns():
    df = pd.DataFrame({"id": [1, 1]})
    report = run_checks(df, [lambda data: check_duplicate_values(data, "id")])
    assert list(report.columns) == ["rule", "row_index", "column", "message", "value"]
    assert len(report) == 1
