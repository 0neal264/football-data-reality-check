
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_statsbomb_events(path: str | Path) -> list[dict]:
    """Load raw event data from a StatsBomb JSON file."""

    with open(path, encoding="utf-8") as file:
        return json.load(file)


def flatten_statsbomb_events(events: list[dict]) -> pd.DataFrame:
    """Convert nested StatsBomb events into a flat Pandas DataFrame."""

    rows = []

    for event in events:

        # Extract event location
        location = event.get("location") or [None, None]

        # Extract event type
        event_type = (event.get("type") or {}).get("name")

        # Extract team and player
        team = event.get("team") or {}
        player = event.get("player") or {}

        # Extract pass information
        pass_data = event.get("pass") or {}

        pass_end = pass_data.get("end_location") or [None, None]

        pass_outcome = (
            pass_data.get("outcome") or {}
        ).get("name")

        # StatsBomb records an outcome for unsuccessful passes.
        # No outcome on a pass indicates a completed pass.
        pass_complete = (
            pass_outcome is None
            if event_type == "Pass"
            else None
        )

        # Extract shot information
        shot_data = event.get("shot") or {}

        shot_outcome = (
            shot_data.get("outcome") or {}
        ).get("name")

        rows.append({

            # Event identification
            "event_id": event.get("id"),
            "event_index": event.get("index"),

            # Match timing
            "period": event.get("period"),
            "minute": event.get("minute"),
            "second": event.get("second"),

            # Event information
            "event_type": event_type,
            "team": team.get("name"),
            "player": player.get("name"),

            # Starting coordinates
            "x": location[0],
            "y": location[1],

            # Passing information
            "pass_end_x": pass_end[0],
            "pass_end_y": pass_end[1],
            "pass_recipient": (
                pass_data.get("recipient") or {}
            ).get("name"),
            "pass_length": pass_data.get("length"),
            "pass_outcome": pass_outcome,
            "pass_complete": pass_complete,

            # Shooting information
            "shot_xg": shot_data.get("statsbomb_xg"),
            "shot_outcome": shot_outcome,
            "is_goal": shot_outcome == "Goal",

            # Possession information
            "possession": event.get("possession"),
            "possession_team": (
                event.get("possession_team") or {}
            ).get("name"),

            # Event duration
            "duration": event.get("duration"),
        })

    return pd.DataFrame(rows)
