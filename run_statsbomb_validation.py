
from src.data_quality.statsbomb import (
    load_statsbomb_events,
    flatten_statsbomb_events,
)

from src.data_quality.rules import run_checks

from src.data_quality.statsbomb_checks import (
    check_event_ids,
    check_event_types,
    check_pitch_coordinates,
    check_shot_xg,
    check_shot_outcomes,
)


DATA_PATH = (
    "data/raw/statsbomb/"
    "real_madrid_liverpool_2018_events.json"
)

OUTPUT_PATH = "outputs/statsbomb_validation_report.csv"


# 1. Load the raw data
raw_events = load_statsbomb_events(DATA_PATH)

# 2. Convert nested JSON into a DataFrame
df = flatten_statsbomb_events(raw_events)

print(f"Events loaded: {len(df)}")


# 3. Define the validation checks
checks = [
    check_event_ids,
    check_event_types,
    check_pitch_coordinates,
    check_shot_xg,
    check_shot_outcomes,
]


# 4. Run all checks
report = run_checks(df, checks)


# 5. Save the report
report.to_csv(OUTPUT_PATH, index=False)


# 6. Display results
print("\nDATA QUALITY REPORT")
print("-" * 40)

print(f"Total events inspected: {len(df)}")
print(f"Potential issues found: {len(report)}")

if report.empty:
    print("No potential issues detected.")
else:
    print("\nFindings by rule:")
    print(report["rule"].value_counts().to_string())

print(f"\nReport saved to: {OUTPUT_PATH}")
