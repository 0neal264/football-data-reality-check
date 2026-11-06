from pathlib import Path

import pandas as pd

from src.data_quality.football import check_pitch_coordinates
from src.data_quality.reporting import export_report
from src.data_quality.rules import (
    check_duplicate_values,
    check_missing_values,
    check_numeric_range,
    check_required_columns,
    run_checks,
)

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "sample_events.csv"
REPORT_PATH = ROOT / "outputs" / "validation_report.csv"


def main() -> None:
    """Load the demonstration data, run checks, and export findings."""
    df = pd.read_csv(DATA_PATH)

    checks = [
        lambda data: check_required_columns(
            data, ["event_id", "event_type", "player", "minute", "x", "y"]
        ),
        lambda data: check_missing_values(data, ["event_id", "player"]),
        lambda data: check_duplicate_values(data, "event_id"),
        lambda data: check_numeric_range(data, "minute", minimum=0, maximum=130),
        lambda data: check_pitch_coordinates(data),
    ]

    report = run_checks(df, checks)
    output_path = export_report(report, REPORT_PATH)

    print(f"Rows inspected: {len(df)}")
    print(f"Potential issues found: {len(report)}")
    print(f"Report written to: {output_path.relative_to(ROOT)}")
    if not report.empty:
        print("\nFindings by rule:")
        print(report.groupby("rule").size().to_string())


if __name__ == "__main__":
    main()
