from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_quality.statsbomb import (
    load_statsbomb_events,
    flatten_statsbomb_events,
)
from src.data_quality.football_analytics import (
    calculate_team_statistics,
)


# ---------- Configuration ----------

st.set_page_config(
    page_title="MatchLab | Football Data Review",
    layout="wide",
)

DATA_PATH = Path(
    "data/raw/statsbomb/real_madrid_liverpool_2018_events.json"
)
REPORT_PATH = Path("outputs/statsbomb_validation_report.csv")

TEAM_COLORS = {
    "Real Madrid": "#2563EB",
    "Liverpool": "#DC2626",
}

TEXT = "#172033"
MUTED = "#667085"
GRID = "#E4E7EC"
PITCH = "#F5F8F6"
GOAL_COLOR = "#D99A16"

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            letter-spacing: -0.025em;
        }

        [data-testid="stMetric"] {
            border: 1px solid #E4E7EC;
            border-radius: 12px;
            padding: 16px;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.85rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Data ----------

@st.cache_data(show_spinner="Loading match data...")
def load_match_data(path_string, modified_ns):
    path = Path(path_string)

    raw_events = load_statsbomb_events(path)
    events = flatten_statsbomb_events(raw_events)

    # Read the original schema for shot-specific fields.
    with path.open(encoding="utf-8") as handle:
        original_events = json.load(handle)

    rows = []

    for event in original_events:
        if event.get("type", {}).get("name") != "Shot":
            continue

        shot = event.get("shot", {})
        location = event.get("location") or []

        rows.append(
            {
                "event_id": event.get("id"),
                "team": event.get("team", {}).get("name"),
                "player": event.get("player", {}).get("name"),
                "period": event.get("period"),
                "minute": event.get("minute"),
                "second": event.get("second"),
                "x": location[0] if len(location) >= 2 else None,
                "y": location[1] if len(location) >= 2 else None,
                "xg": shot.get("statsbomb_xg"),
                "outcome": shot.get("outcome", {}).get("name"),
                "body_part": shot.get("body_part", {}).get("name"),
                "shot_type": shot.get("type", {}).get("name"),
            }
        )

    columns = [
        "event_id", "team", "player", "period", "minute", "second",
        "x", "y", "xg", "outcome", "body_part", "shot_type",
    ]
    shots = pd.DataFrame(rows, columns=columns)

    for column in ["period", "minute", "second", "x", "y", "xg"]:
        shots[column] = pd.to_numeric(shots[column], errors="coerce")

    return events, shots


def chart_style(fig, height=340):
    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(family="Arial, sans-serif", color=TEXT),
        margin=dict(l=15, r=15, t=35, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


def render_chart(fig, key):
    st.plotly_chart(
        fig,
        use_container_width=True,
        theme=None,
        config={
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        },
        key=key,
    )


def csv_bytes(frame):
    return frame.to_csv(index=False).encode("utf-8")


def xg_total(frame):
    if frame.empty or not frame["xg"].notna().any():
        return None
    return frame["xg"].sum(min_count=1)


def format_xg(value):
    return "Unavailable" if value is None or pd.isna(value) else f"{value:.2f}"


# ---------- Shot map ----------

def build_shot_map(team_shots, team):
    fig = go.Figure()
    line = dict(color="#AAB8AF", width=1.4)

    # Rotated attacking half:
    # horizontal axis = original y; vertical axis = original x.
    for x0, y0, x1, y1 in [
        (0, 60, 80, 120),
        (18, 102, 62, 120),
        (30, 114, 50, 120),
        (36, 120, 44, 122),
    ]:
        fig.add_shape(
            type="rect",
            x0=x0, y0=y0, x1=x1, y1=y1,
            line=line,
        )

    fig.add_shape(
        type="circle",
        x0=39.6, x1=40.4,
        y0=107.6, y1=108.4,
        line=line,
        fillcolor=line["color"],
    )

    valid = team_shots.loc[
        team_shots["x"].between(60, 120)
        & team_shots["y"].between(0, 80)
    ].copy()

    valid["plot_x"] = 80 - valid["y"]
    valid["plot_y"] = valid["x"]
    valid["xg_label"] = valid["xg"].map(
        lambda value: "Unavailable" if pd.isna(value) else f"{value:.3f}"
    )
    valid["time_label"] = valid.apply(
        lambda row: (
            f"{int(row['minute'])}:{int(row['second']):02d}"
            if pd.notna(row["minute"]) and pd.notna(row["second"])
            else "Unknown"
        ),
        axis=1,
    )

    for is_goal, label, color in [
        (False, "Other shots", TEAM_COLORS.get(team, "#2563EB")),
        (True, "Goals", GOAL_COLOR),
    ]:
        subset = valid.loc[valid["outcome"].eq("Goal") == is_goal]

        if subset.empty:
            continue

        custom = subset[
            ["player", "time_label", "outcome", "xg_label", "body_part"]
        ].fillna("Unknown").to_numpy()

        fig.add_trace(
            go.Scatter(
                x=subset["plot_x"],
                y=subset["plot_y"],
                mode="markers",
                name=label,
                customdata=custom,
                marker=dict(
                    # Shared scale across both team panels.
                    size=10 + 32 * subset["xg"].fillna(0).clip(0, 1).pow(0.5),
                    color=color,
                    opacity=0.9 if is_goal else 0.65,
                    line=dict(color="white", width=1.5),
                    symbol="diamond" if is_goal else "circle",
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Time: %{customdata[1]}<br>"
                    "Outcome: %{customdata[2]}<br>"
                    "xG: %{customdata[3]}<br>"
                    "Body part: %{customdata[4]}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        height=440,
        margin=dict(l=10, r=10, t=10, b=35),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PITCH,
        font=dict(color=TEXT),
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.04,
        ),
        xaxis=dict(
            range=[-3, 83],
            visible=False,
            fixedrange=True,
            constrain="domain",
        ),
        yaxis=dict(
            range=[58, 124],
            visible=False,
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1,
        ),
    )

    return fig, len(team_shots) - len(valid)


# ---------- Load and validate app inputs ----------

if not DATA_PATH.exists():
    st.error(f"Match data not found: {DATA_PATH}")
    st.stop()

try:
    df, all_shots = load_match_data(
        str(DATA_PATH),
        DATA_PATH.stat().st_mtime_ns,
    )
    team_stats = calculate_team_statistics(df)
except Exception as exc:
    st.error("The match data could not be loaded or processed.")
    st.exception(exc)
    st.stop()

required_stats = {
    "team", "shots", "goals", "passes_attempted", "pass_accuracy_pct"
}
missing_stats = required_stats - set(team_stats.columns)

if missing_stats or "event_type" not in df.columns:
    st.error(
        "Unexpected input schema. Missing team-stat columns: "
        f"{sorted(missing_stats)}. "
        f"Event type available: {'event_type' in df.columns}."
    )
    st.stop()

teams = team_stats["team"].dropna().unique().tolist()

# Exclude penalty shootouts from the default shot analysis.
match_shots = all_shots.loc[all_shots["period"].ne(5)].copy()


# ---------- Sidebar ----------

with st.sidebar:
    st.markdown("### MatchLab")
    st.caption("Football event analysis and data review")

    st.divider()

    st.markdown("#### Dataset")
    st.write("Real Madrid vs Liverpool")
    st.caption("2018 Champions League Final")
    st.caption("Source: StatsBomb Open Data")

    st.markdown("#### Review scope")
    st.write("Event data: loaded")
    st.write("Tracking data: not included")
    st.write("Video verification: not performed in this app")

    st.divider()

    st.download_button(
        "Export event data",
        data=csv_bytes(df),
        file_name="match_events.csv",
        mime="text/csv",
    )


# ---------- Header ----------

st.caption("MATCHLAB / FOOTBALL DATA REVIEW")
st.title("Real Madrid vs Liverpool")
st.write(
    "2018 Champions League Final · "
    "Match analysis, event exploration and validation evidence"
)

metrics = st.columns(4)
metrics[0].metric("Events", f"{len(df):,}")
metrics[1].metric("Shots", len(match_shots))
metrics[2].metric("Shot-event goals", int(match_shots["outcome"].eq("Goal").sum()))
metrics[3].metric("Expected goals", format_xg(xg_total(match_shots)))

st.caption(
    "Shot-event goals count shots with outcome 'Goal'; "
    "this is not a general-purpose score calculation and excludes own goals. "
    "Penalty-shootout shots are excluded from shot analysis."
)

overview_tab, shots_tab, events_tab, quality_tab = st.tabs(
    ["Match overview", "Shot analysis", "Event explorer", "Data quality"]
)


# ---------- Overview ----------

with overview_tab:
    st.subheader("Team comparison")
    st.caption("Compare metrics separately rather than mixing different units.")

    left, right = st.columns(2)

    with left:
        st.markdown("#### Pass accuracy")

        fig = px.bar(
            team_stats,
            x="pass_accuracy_pct",
            y="team",
            color="team",
            orientation="h",
            color_discrete_map=TEAM_COLORS,
            text="pass_accuracy_pct",
            labels={"pass_accuracy_pct": "Pass accuracy (%)", "team": ""},
        )
        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
        )
        chart_style(fig)
        fig.update_layout(showlegend=False)
        fig.update_xaxes(range=[0, 110], ticksuffix="%")
        render_chart(fig, "pass_accuracy")

    with right:
        st.markdown("#### Shooting volume")

        counts = pd.DataFrame(
            [
                {
                    "team": team,
                    "Shots": len(match_shots.loc[match_shots["team"].eq(team)]),
                    "Goals": int(
                        match_shots.loc[
                            match_shots["team"].eq(team), "outcome"
                        ].eq("Goal").sum()
                    ),
                }
                for team in teams
            ]
        )

        fig = px.bar(
            counts,
            x="team",
            y=["Shots", "Goals"],
            barmode="group",
            color_discrete_map={"Shots": "#94A3B8", "Goals": "#2563EB"},
            labels={"value": "Count", "team": "", "variable": ""},
        )
        chart_style(fig)
        render_chart(fig, "shooting_volume")

    with st.expander("View calculated team statistics"):
        st.dataframe(team_stats, hide_index=True, use_container_width=True)

    st.info(
        "Interpretation boundary: this dashboard describes event records. "
        "It does not estimate team shape or continuous player movement."
    )


# ---------- Shot analysis ----------

with shots_tab:
    st.subheader("Where did the chances come from?")
    st.caption(
        "Both teams attack upward. Marker size increases with xG; "
        "gold diamonds identify goals. Hover for event details."
    )

    available_periods = sorted(
        match_shots["period"].dropna().astype(int).unique().tolist()
    )
    selected_periods = st.multiselect(
        "Periods",
        options=available_periods,
        default=available_periods,
        key="shot_periods",
    )
    visible_shots = match_shots.loc[
        match_shots["period"].isin(selected_periods)
    ]

    columns = st.columns(max(len(teams), 1))

    for column, team in zip(columns, teams):
        with column:
            team_shots = visible_shots.loc[
                visible_shots["team"].eq(team)
            ]

            st.markdown(f"### {team}")

            a, b, c = st.columns(3)
            a.metric("Shots", len(team_shots))
            b.metric("Goals", int(team_shots["outcome"].eq("Goal").sum()))
            c.metric("xG", format_xg(xg_total(team_shots)))

            fig, excluded = build_shot_map(team_shots, team)
            render_chart(fig, f"shot_map_{team}")

            if excluded:
                st.warning(
                    f"{excluded} shot(s) not plotted: coordinates are missing "
                    "or outside the displayed attacking half. "
                    "They remain included in the totals."
                )

    st.caption(
        "Missing xG values use the minimum marker size. "
        "Reported xG totals sum available values only."
    )

    with st.expander("Inspect shot records"):
        st.dataframe(
            visible_shots,
            hide_index=True,
            use_container_width=True,
        )
        st.download_button(
            "Export selected shots",
            data=csv_bytes(visible_shots),
            file_name="selected_shots.csv",
            mime="text/csv",
        )


# ---------- Event explorer ----------

with events_tab:
    st.subheader("Inspect the underlying events")
    st.caption(
        "Filter records before investigating an unexpected number or sequence."
    )

    filtered = df.copy()
    filters = st.columns(3)

    with filters[0]:
        if "team" in df.columns:
            selected_teams = st.multiselect(
                "Teams",
                sorted(df["team"].dropna().astype(str).unique()),
            )
            if selected_teams:
                filtered = filtered.loc[
                    filtered["team"].astype(str).isin(selected_teams)
                ]

    with filters[1]:
        selected_types = st.multiselect(
            "Event types",
            sorted(df["event_type"].dropna().astype(str).unique()),
        )
        if selected_types:
            filtered = filtered.loc[
                filtered["event_type"].astype(str).isin(selected_types)
            ]

    with filters[2]:
        if "minute" in df.columns:
            minutes = pd.to_numeric(df["minute"], errors="coerce")
            if minutes.notna().any():
                bounds = (int(minutes.min()), int(minutes.max()))
                if bounds[0] < bounds[1]:
                    selected_minutes = st.slider(
                        "Match minute",
                        min_value=bounds[0],
                        max_value=bounds[1],
                        value=bounds,
                    )
                    filtered_minutes = pd.to_numeric(
                        filtered["minute"], errors="coerce"
                    )
                    filtered = filtered.loc[
                        filtered_minutes.between(*selected_minutes)
                    ]

    st.caption(f"{len(filtered):,} of {len(df):,} events selected")

    preferred = [
        "event_id", "id", "period", "minute", "second",
        "team", "player", "event_type",
    ]
    available = [column for column in preferred if column in filtered.columns]

    show_all = st.checkbox("Show all columns")
    st.dataframe(
        filtered if show_all else filtered[available],
        hide_index=True,
        use_container_width=True,
    )

    st.download_button(
        "Export filtered events",
        data=csv_bytes(filtered),
        file_name="filtered_events.csv",
        mime="text/csv",
    )


# ---------- Data quality ----------

with quality_tab:
    st.subheader("Validation evidence")
    st.caption(
        "A report is evidence to investigate—not automatic proof "
        "that the dataset is correct."
    )

    if not REPORT_PATH.exists():
        st.warning(
            "No validation report is available. "
            "Run run_statsbomb_validation.py to generate it."
        )
    else:
        try:
            report = pd.read_csv(REPORT_PATH)
        except pd.errors.EmptyDataError:
            report = None
            st.warning(
                "The report file has no readable columns. "
                "Generate a report with headers, including when there are no findings."
            )
        except Exception as exc:
            report = None
            st.error(f"Could not read validation report: {exc}")

        if report is not None:
            st.metric("Report rows", len(report))
            st.caption(
                "Rows are not labelled as failed checks because the report "
                "schema and row meaning have not been specified."
            )

            if report.empty:
                st.info(
                    "The report contains no rows. This does not, by itself, "
                    "establish which checks ran or whether they passed."
                )
            else:
                st.dataframe(
                    report,
                    hide_index=True,
                    use_container_width=True,
                )

            st.download_button(
                "Export validation report",
                data=csv_bytes(report),
                file_name="validation_report.csv",
                mime="text/csv",
            )

    st.markdown("#### Review limitations")
    st.markdown(
        "- No match-video verification has been performed by this app.\n"
        "- No continuous tracking data is included.\n"
        "- A flagged record requires investigation before calling it an error.\n"
        "- Validation coverage depends on the checks implemented upstream."
    )

st.divider()
st.caption(
    "Independent portfolio project · StatsBomb Open Data · "
    "Not affiliated with Veo · No video-validation claims implied"
)