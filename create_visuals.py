from src.data_quality.statsbomb import (
    load_statsbomb_events,
    flatten_statsbomb_events,
)

from src.data_quality.visualisations import (  # or match_viz
    plot_shot_map,
    plot_team_comparison,
    plot_xg_race,
    plot_dashboard,
)

DATA_PATH = (
    "data/raw/statsbomb/"
    "real_madrid_liverpool_2018_events.json"
)
OUTPUT_DIR = "outputs"

# Load the real match data
events = load_statsbomb_events(DATA_PATH)
df = flatten_statsbomb_events(events)
print(f"Events loaded: {len(df)}")

# Generate all visualisations
shots = plot_shot_map(df, f"{OUTPUT_DIR}/shot_map.png")
summary = plot_team_comparison(df, f"{OUTPUT_DIR}/team_comparison.png")
plot_xg_race(df, f"{OUTPUT_DIR}/xg_race.png")
plot_dashboard(df, f"{OUTPUT_DIR}/dashboard.png")

print("\nTEAM COMPARISON")
print(summary.round(2))

print(f"\nTotal shots analysed: {len(shots)}")
print("All visualisations generated successfully.")