
from pathlib import Path

from src.data_quality.statsbomb import (
    load_statsbomb_events,
    flatten_statsbomb_events,
)

from src.data_quality.football_analytics import (
    calculate_team_statistics,
)


# File locations
DATA_PATH = (
    "data/raw/statsbomb/"
    "real_madrid_liverpool_2018_events.json"
)

OUTPUT_PATH = Path(
    "outputs/football_team_statistics.csv"
)


def main():
    # 1. Load raw StatsBomb events
    raw_events = load_statsbomb_events(DATA_PATH)

    # 2. Flatten nested JSON into a DataFrame
    df = flatten_statsbomb_events(raw_events)

    print(f"Events loaded: {len(df)}")

    # 3. Calculate team statistics
    statistics = calculate_team_statistics(df)

    # 4. Save results
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    statistics.to_csv(OUTPUT_PATH, index=False)

    # 5. Display results
    print("\nFOOTBALL ANALYTICS")
    print("=" * 55)

    print(
        statistics.to_string(
            index=False
        )
    )

    print("\nREPORT SUMMARY")
    print("-" * 55)

    print(
        f"Teams analysed: {len(statistics)}"
    )

    print(
        f"Total shots: {statistics['shots'].sum()}"
    )

    print(
        f"Total goals: {statistics['goals'].sum()}"
    )

    print(
        f"Total passes: {statistics['passes_attempted'].sum()}"
    )

    print(
        f"Total xG: {statistics['total_xg'].sum():.3f}"
    )

    print(f"\nSaved report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
