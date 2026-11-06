from pathlib import Path

import pandas as pd


def export_report(report: pd.DataFrame, output_path: str | Path) -> Path:
    """Write a validation report to CSV and return the resulting path."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(destination, index=False)
    return destination
