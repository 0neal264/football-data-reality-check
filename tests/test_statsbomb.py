
import pandas as pd

from src.data_quality.statsbomb import flatten_statsbomb_events


def test_flatten_statsbomb_events_extracts_coordinates():
    events = [{
        "id": "event-1",
        "index": 1,
        "type": {"name": "Pass"},
        "team": {"name": "Liverpool"},
        "player": {"name": "James Milner"},
        "location": [60.0, 40.0],
        "pass": {
            "end_location": [32.1, 41.2],
            "recipient": {"name": "Dejan Lovren"},
            "length": 27.9,
        },
    }]

    result = flatten_statsbomb_events(events)

    assert result.iloc[0]["x"] == 60.0
    assert result.iloc[0]["y"] == 40.0
    assert result.iloc[0]["team"] == "Liverpool"
    assert result.iloc[0]["pass_recipient"] == "Dejan Lovren"


def test_flatten_statsbomb_events_handles_missing_location():
    events = [{
        "id": "event-2",
        "index": 2,
        "type": {"name": "Half Start"},
    }]

    result = flatten_statsbomb_events(events)

    assert pd.isna(result.iloc[0]["x"])
    assert pd.isna(result.iloc[0]["y"])
