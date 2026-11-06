
from pathlib import Path

from src.data_quality.statsbomb import (
    load_statsbomb_events,
    flatten_statsbomb_events,
)

from src.data_quality.completeness import (
    profile_event_field_completeness,
)

from src.data_quality.profiling import (
    profile_missing_values,
    profile_event_types,
    profile_coordinates,
    profile_team_activity,
)


DATA_PATH = (
    "data/raw/statsbomb/"
    "real_madrid_liverpool_2018_events.json"
)

OUTPUT_DIR = Path("outputs/profiling")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# 1. Load and flatten the data
raw_events = load_statsbomb_events(DATA_PATH)
df = flatten_statsbomb_events(raw_events)

print(f"Events analysed: {len(df)}")


# 2. Generate profiling reports
reports = {
    "missing_values": profile_missing_values(df),
    "event_types": profile_event_types(df),
    "coordinates": profile_coordinates(df),
    "team_activity": profile_team_activity(df),
    "event_field_completeness": profile_event_field_completeness(df)
}


# 3. Save each report
for name, report in reports.items():
    output_path = OUTPUT_DIR / f"{name}.csv"
    report.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")


# 4. Display key findings
print("\nEVENT TYPE DISTRIBUTION")
print(reports["event_types"].head(10).to_string(index=False))

print("\nMISSING VALUES")
print(reports["missing_values"].to_string(index=False))

print("\nTEAM ACTIVITY")
print(reports["team_activity"].to_string(index=False))

print("\nCOORDINATE COMPLETENESS")
print(reports["coordinates"].head(15).to_string(index=False))

print("\nProfiling completed successfully.")
print("\nEVENT-SPECIFIC FIELD COMPLETENESS")

print(
    reports["event_field_completeness"].to_string(
        index=False
    )
)
