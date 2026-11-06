"""
Match visualisation template (StatsBomb shot data)

Design system
-------------
Canvas    near-black blue, flat (no panel boxes, less clutter)
Teams     one colour per team, used EVERYWHERE (maps, lines, bars, titles)
Goals     always gold stars, nothing else is gold
Size      marker size = xG, always
Text      big bold titles, small muted labels, left-aligned

Charts
------
plot_shot_map         vertical half-pitch, one pitch per team
plot_shot_map_combined both teams on one full pitch
plot_xg_race          cumulative xG over the match (the "who deserved it" chart)
plot_team_comparison  butterfly "tale of the tape" bars
plot_dashboard        all three on one poster
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Circle, Rectangle


# ---------------------------------------------------------
# DESIGN TOKENS
# ---------------------------------------------------------

BG = "#0b1117"
GRID = "#1c2a35"
TEXT = "#f2f5f7"
MUTED = "#8a9ba8"
GOLD = "#ffd166"

PITCH = "#0f2623"
PITCH_LINE = "#3d6b60"

TEAM_ORDER = ["Real Madrid", "Liverpool"]  # left -> right
TEAM_COLORS = {
    "Real Madrid": "#5fb4ff",
    "Liverpool": "#ff5a5f",
}
FALLBACK = ["#5fb4ff", "#ff5a5f", "#b69cff", "#5fe0b0"]

ON_TARGET = ["Goal", "Saved"]


def set_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "text.color": TEXT,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.edgecolor": GRID,
    })


set_style()


# ---------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------

def prepare_shots(events: pd.DataFrame) -> pd.DataFrame:
    """Select and clean shot events."""

    shots = events.loc[events["event_type"].eq("Shot")].copy()

    # drop penalty shoot-out shots (StatsBomb period 5)
    if "period" in shots.columns:
        shots = shots[pd.to_numeric(shots["period"], errors="coerce") < 5]

    for col in ["x", "y", "shot_xg", "minute", "second"]:
        if col in shots.columns:
            shots[col] = pd.to_numeric(shots[col], errors="coerce")

    shots = shots.dropna(subset=["x", "y", "team"])
    shots["shot_xg"] = shots["shot_xg"].fillna(0)
    shots["minute"] = shots["minute"].fillna(0)
    shots["second"] = shots["second"].fillna(0)
    shots["match_time"] = shots["minute"] + shots["second"] / 60
    shots["shot_outcome"] = shots["shot_outcome"].fillna("Unknown")
    return shots


def get_teams(shots):
    present = list(shots["team"].unique())
    ordered = [t for t in TEAM_ORDER if t in present]
    return ordered + sorted(t for t in present if t not in ordered)


def get_team_colors(teams):
    return {
        t: TEAM_COLORS.get(t, FALLBACK[i % len(FALLBACK)])
        for i, t in enumerate(teams)
    }


def team_stats(shots, team):
    s = shots[shots["team"] == team]
    n = len(s)
    xg = s["shot_xg"].sum()
    return {
        "Goals": int((s["shot_outcome"] == "Goal").sum()),
        "xG": xg,
        "Shots": n,
        "On target": int(s["shot_outcome"].isin(ON_TARGET).sum()),
        "Shots in box": int(((s["x"] >= 102) & s["y"].between(18, 62)).sum()),
        "Big chances (xG 0.3+)": int((s["shot_xg"] >= 0.3).sum()),
        "xG per shot": xg / n if n else 0,
    }


def xg_size(xg):
    """Marker area from xG. One rule for the whole project."""
    return 35 + np.clip(xg, 0, 1) * 1100


def goal_label(row):
    """'Bale 64'' if a player column exists, else just the minute."""
    minute = f"{int(row['minute'])}'"
    player = row.get("player") if hasattr(row, "get") else None
    if isinstance(player, str) and player:
        return f"{player.split()[-1]} {minute}"
    return minute


# ---------------------------------------------------------
# SHARED TEXT PIECES
# ---------------------------------------------------------

OUTLINE = lambda color=BG, w=3: [pe.withStroke(linewidth=w, foreground=color)]


def section_title(ax, text):
    ax.set_title(
        text, loc="left", color=MUTED, fontsize=11,
        fontweight="bold", pad=16,
    )


def add_title(fig, title, subtitle, y=0.965):
    fig.text(0.05, y, title, fontsize=22, fontweight="bold",
             color=TEXT, ha="left", va="top")
    fig.text(0.05, y - 0.055, subtitle, fontsize=11,
             color=MUTED, ha="left", va="top")


def add_footer(fig, text):
    fig.text(0.05, 0.02, text, fontsize=9, color=MUTED, ha="left")


# ---------------------------------------------------------
# PITCH + SHOT MAP (vertical half pitch, goal at the top)
# StatsBomb pitch is 120 x 80: x = length, y = width
# On the plot: horizontal axis = y, vertical axis = x
# ---------------------------------------------------------

def draw_pitch(ax):
    ax.add_patch(Rectangle((-2, 77), 84, 46, facecolor=PITCH,
                           edgecolor="none", zorder=0))

    # subtle grass stripes
    for i, x0 in enumerate(range(60, 120, 10)):
        if i % 2 == 0:
            ax.add_patch(Rectangle((0, x0), 80, 10, facecolor="white",
                                   edgecolor="none", alpha=0.025, zorder=0))

    line = dict(fill=False, edgecolor=PITCH_LINE, linewidth=1.3, zorder=1)
    ax.add_patch(Rectangle((0, 60), 80, 60, **line))        # outline
    ax.add_patch(Rectangle((18, 102), 44, 18, **line))      # penalty area
    ax.add_patch(Rectangle((30, 114), 20, 6, **line))       # six-yard box
    ax.add_patch(Arc((40, 108), 20, 20, theta1=217, theta2=323,
                     color=PITCH_LINE, lw=1.3, zorder=1))   # penalty arc
    ax.scatter([40], [108], s=8, color=PITCH_LINE, zorder=1)
    ax.plot([36, 44], [120, 120], color=TEXT, lw=4,
            solid_capstyle="butt", zorder=2)                # goal

    ax.set_xlim(-2, 82)
    ax.set_ylim(77, 122)
    ax.set_aspect("equal")
    ax.set_axis_off()


def draw_shot_map(ax, team_shots, team, color):
    draw_pitch(ax)

    misses = team_shots[team_shots["shot_outcome"] != "Goal"]
    goals = team_shots[team_shots["shot_outcome"] == "Goal"]

    # misses / saves: hollow-ish circles in team colour
    ax.scatter(
        misses["y"], misses["x"],
        s=xg_size(misses["shot_xg"]),
        facecolor=to_rgba(color, 0.22),
        edgecolor=to_rgba(color, 0.95),
        linewidth=1.4, zorder=5,
    )

    # goals: gold stars with a soft glow
    ax.scatter(
        goals["y"], goals["x"],
        s=xg_size(goals["shot_xg"]) * 0.9 + 220,
        marker="*", color=GOLD, edgecolor="white", linewidth=0.8,
        zorder=7,
        path_effects=[pe.withStroke(linewidth=9, foreground=GOLD, alpha=0.22)],
    )

    for _, g in goals.iterrows():
        dy = -18 if g["x"] > 110 else 17
        ax.annotate(
            goal_label(g), (g["y"], g["x"]),
            xytext=(0, dy), textcoords="offset points",
            ha="center", va="center", fontsize=9, fontweight="bold",
            color=TEXT, path_effects=OUTLINE(PITCH), zorder=8,
        )

    st = team_stats(team_shots.assign(team=team), team)
    ax.text(0, 1.075, team, transform=ax.transAxes, fontsize=17,
            fontweight="bold", color=color, ha="left", va="bottom")
    ax.text(
        0, 1.02, f"{st['Shots']} shots   ·   {st['Goals']} goals   ·   "
                 f"{st['xG']:.2f} xG",
        transform=ax.transAxes, fontsize=10.5, color=MUTED,
        ha="left", va="bottom",
    )


def shot_legend(fig, y=0.065):
    sizes = [0.05, 0.2, 0.5]
    handles = [
        Line2D([0], [0], marker="o", ls="none", markersize=np.sqrt(xg_size(v)),
               markerfacecolor=to_rgba("#aab8c2", 0.25),
               markeredgecolor="#aab8c2", label=f"xG {v}")
        for v in sizes
    ]
    handles.append(Line2D([0], [0], marker="*", ls="none", markersize=15,
                          markerfacecolor=GOLD, markeredgecolor="white",
                          label="Goal"))
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               labelcolor=MUTED, fontsize=10, handletextpad=0.6,
               columnspacing=2.4, bbox_to_anchor=(0.5, y - 0.04))


# ---------------------------------------------------------
# xG RACE
# ---------------------------------------------------------

def draw_xg_race(ax, shots, teams, colors):
    end = max(90, shots["match_time"].max()) + 1

    for i, team in enumerate(teams):
        s = shots[shots["team"] == team].sort_values("match_time")
        cum = np.cumsum(s["shot_xg"].values)
        xs = [0] + list(s["match_time"]) + [end]
        ys = [0] + list(cum) + [cum[-1] if len(cum) else 0]

        ax.step(xs, ys, where="post", color=colors[team], lw=2.8, zorder=3)
        ax.fill_between(xs, ys, step="post", color=colors[team],
                        alpha=0.08, zorder=2)

        # goals as gold stars on the line
        is_goal = (s["shot_outcome"] == "Goal").values
        if is_goal.any():
            gt = s["match_time"].values[is_goal]
            gy = cum[is_goal]
            ax.scatter(gt, gy, marker="*", s=260, color=GOLD,
                       edgecolor="white", linewidth=0.8, zorder=6,
                       path_effects=[pe.withStroke(linewidth=8,
                                                   foreground=GOLD, alpha=0.22)])
            for (_, row), x_, y_ in zip(s[is_goal].iterrows(), gt, gy):
                ax.annotate(goal_label(row), (x_, y_),
                            xytext=(0, 16 if i == 0 else -20),
                            textcoords="offset points", ha="center",
                            fontsize=9, fontweight="bold", color=TEXT,
                            path_effects=OUTLINE(BG), zorder=7)

        # final xG label at the end of the line
        ax.text(end + 1.0, ys[-1], f"{ys[-1]:.2f}", color=colors[team],
                fontsize=13, fontweight="bold", va="center")

    ax.axvline(45, color=MUTED, lw=1, ls=(0, (4, 4)), alpha=0.6, zorder=1)
    ax.text(45.8, ax.get_ylim()[1] * 0.98, "HT", color=MUTED, fontsize=9,
            va="top")

    ax.set_xlim(0, end + 7)
    ax.set_ylim(bottom=0)
    ax.set_xticks([0, 15, 30, 45, 60, 75, 90])
    ax.set_xlabel("Match minute", labelpad=8, fontsize=10)
    ax.set_ylabel("Cumulative xG", labelpad=8, fontsize=10)
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)

    handles = [Line2D([0], [0], color=colors[t], lw=3, label=t) for t in teams]
    ax.legend(handles=handles, loc="upper left", frameon=False,
              labelcolor=TEXT, fontsize=10)


# ---------------------------------------------------------
# TEAM COMPARISON (butterfly bars)
# ---------------------------------------------------------

def draw_comparison(ax, shots, teams, colors):
    a, b = teams[:2]
    stats = pd.DataFrame({t: team_stats(shots, t) for t in (a, b)})
    rows = list(stats.index)
    n = len(rows)

    for i, row in enumerate(rows):
        y = n - 1 - i
        va, vb = stats.loc[row, a], stats.loc[row, b]
        m = max(va, vb) or 1
        fmt = (lambda v: f"{v:.2f}") if row in ("xG", "xG per shot") \
            else (lambda v: f"{int(v)}")

        # faint tracks so bars read as proportions
        ax.barh(y, -1, height=0.3, color=GRID, zorder=1)
        ax.barh(y, 1, height=0.3, color=GRID, zorder=1)

        ax.barh(y, -va / m, height=0.3, color=colors[a], zorder=2)
        ax.barh(y, vb / m, height=0.3, color=colors[b], zorder=2)

        ax.text(-1.04, y, fmt(va), ha="right", va="center", fontsize=13,
                fontweight="bold", color=colors[a] if va >= vb else MUTED)
        ax.text(1.04, y, fmt(vb), ha="left", va="center", fontsize=13,
                fontweight="bold", color=colors[b] if vb >= va else MUTED)
        ax.text(0, y + 0.34, row.upper(), ha="center", va="bottom",
                fontsize=8.5, color=MUTED, fontweight="bold")

    ax.text(-1, n + 0.15, a, color=colors[a], fontsize=14,
            fontweight="bold", ha="left", va="bottom")
    ax.text(1, n + 0.15, b, color=colors[b], fontsize=14,
            fontweight="bold", ha="right", va="bottom")

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.6, n + 0.7)
    ax.set_axis_off()
    return stats


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

def save_figure(fig, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved: {output_path}")


FOOTER = "Data: StatsBomb Open Data   ·   xG = StatsBomb expected goals"
TITLE = "2018 Champions League Final"


# ---------------------------------------------------------
# PUBLIC CHART FUNCTIONS
# ---------------------------------------------------------

def plot_shot_map(events, output_path, title=TITLE):
    shots = prepare_shots(events)
    teams = get_teams(shots)[:2]
    colors = get_team_colors(teams)

    fig, axes = plt.subplots(1, 2, figsize=(13, 7.2))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.76, bottom=0.14,
                        wspace=0.1)

    for ax, team in zip(axes, teams):
        draw_shot_map(ax, shots[shots["team"] == team], team, colors[team])

    add_title(fig, f"{title}: shot map",
              "Every shot, sized by expected goals (xG)")
    shot_legend(fig, y=0.1)
    add_footer(fig, FOOTER)
    save_figure(fig, output_path)
    return shots


def plot_xg_race(events, output_path, title=TITLE):
    shots = prepare_shots(events)
    teams = get_teams(shots)[:2]
    colors = get_team_colors(teams)

    fig, ax = plt.subplots(figsize=(13, 6.5))
    plt.subplots_adjust(left=0.07, right=0.94, top=0.76, bottom=0.14)

    draw_xg_race(ax, shots, teams, colors)

    add_title(fig, f"{title}: the xG race",
              "How much danger each team built up, minute by minute")
    add_footer(fig, FOOTER)
    save_figure(fig, output_path)
    return shots


def plot_team_comparison(events, output_path, title=TITLE):
    shots = prepare_shots(events)
    teams = get_teams(shots)[:2]
    colors = get_team_colors(teams)

    fig, ax = plt.subplots(figsize=(11, 7.5))
    plt.subplots_adjust(left=0.06, right=0.94, top=0.76, bottom=0.08)

    stats = draw_comparison(ax, shots, teams, colors)

    add_title(fig, f"{title}: tale of the tape",
              "Bars are scaled within each row, so longer = more")
    add_footer(fig, FOOTER)
    save_figure(fig, output_path)
    return stats


def plot_dashboard(events, output_path, title=TITLE):
    """Everything on one poster."""
    shots = prepare_shots(events)
    teams = get_teams(shots)[:2]
    colors = get_team_colors(teams)
    a, b = teams
    goals = {t: team_stats(shots, t)["Goals"] for t in teams}

    fig = plt.figure(figsize=(16, 12.5))
    gs = fig.add_gridspec(
        2, 2, height_ratios=[1.0, 1],
        left=0.05, right=0.95, top=0.80, bottom=0.10,
        hspace=0.3, wspace=0.12,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_race = fig.add_subplot(gs[1, 0])
    ax_tape = fig.add_subplot(gs[1, 1])

    for ax, team in zip((ax_a, ax_b), teams):
        draw_shot_map(ax, shots[shots["team"] == team], team, colors[team])
    draw_xg_race(ax_race, shots, teams, colors)
    section_title(ax_race, "THE xG RACE")
    draw_comparison(ax_tape, shots, teams, colors)
    section_title(ax_tape, "TALE OF THE TAPE")

    # scoreboard header
    fig.text(0.42, 0.93, a, fontsize=30, fontweight="bold",
             color=colors[a], ha="right", va="center")
    fig.text(0.5, 0.93, f"{goals[a]} – {goals[b]}", fontsize=34,
             fontweight="bold", color=TEXT, ha="center", va="center")
    fig.text(0.58, 0.93, b, fontsize=30, fontweight="bold",
             color=colors[b], ha="left", va="center")
    fig.text(0.5, 0.885, title.upper() + "   ·   SHOT ANALYSIS",
             fontsize=11, color=MUTED, ha="center", va="center")

    shot_legend(fig, y=0.075)
    add_footer(fig, FOOTER)
    save_figure(fig, output_path)
    return shots



# ---------------------------------------------------------
# COMBINED SHOT MAP (both teams on one full pitch)
# Team A attacks the right goal, team B is mirrored and attacks the left.
# Colour = team, marker shape = outcome, gold star = goal, size = xG.
# ---------------------------------------------------------

OUTCOME_MARKERS = {
    "Saved": "o",
    "Saved Off Target": "o",
    "Saved to Post": "o",
    "Blocked": "s",
    "Off T": "X",
    "Wayward": "X",
    "Post": "D",
    "Unknown": "o",
}
OUTCOME_LEGEND = [
    ("Saved", "o"), ("Blocked", "s"), ("Off target", "X"), ("Post", "D"),
]


def draw_full_pitch(ax):
    ax.add_patch(Rectangle((-4, -4), 128, 88, facecolor=PITCH,
                           edgecolor="none", zorder=0))
    for i, x0 in enumerate(range(0, 120, 10)):
        if i % 2 == 0:
            ax.add_patch(Rectangle((x0, 0), 10, 80, facecolor="white",
                                   edgecolor="none", alpha=0.025, zorder=0))

    line = dict(fill=False, edgecolor=PITCH_LINE, linewidth=1.3, zorder=1)
    ax.add_patch(Rectangle((0, 0), 120, 80, **line))
    ax.plot([60, 60], [0, 80], color=PITCH_LINE, lw=1.3, zorder=1)
    ax.add_patch(Circle((60, 40), 10, **line))
    ax.scatter([60], [40], s=8, color=PITCH_LINE, zorder=1)

    for x_edge, box_x, six_x, spot, arc_c, t1, t2 in [
        (120, 102, 114, 108, (108, 40), 127, 233),
        (0, 0, 0, 12, (12, 40), -53, 53),
    ]:
        ax.add_patch(Rectangle((box_x, 18), 18, 44, **line))
        ax.add_patch(Rectangle((six_x, 30), 6, 20, **line))
        ax.add_patch(Arc(arc_c, 20, 20, theta1=t1, theta2=t2,
                         color=PITCH_LINE, lw=1.3, zorder=1))
        ax.scatter([spot], [40], s=8, color=PITCH_LINE, zorder=1)
        ax.plot([x_edge, x_edge], [36, 44], color=TEXT, lw=4,
                solid_capstyle="butt", zorder=2)

    ax.set_xlim(-4, 124)
    ax.set_ylim(-4, 84)
    ax.set_aspect("equal")
    ax.set_axis_off()


def draw_combined_shot_map(ax, shots, teams, colors):
    draw_full_pitch(ax)

    for i, team in enumerate(teams[:2]):
        s = shots[shots["team"] == team]
        color = colors[team]
        # team A attacks right as-is; team B is mirrored to attack left
        px = s["x"] if i == 0 else 120 - s["x"]
        py = s["y"] if i == 0 else 80 - s["y"]
        s = s.assign(px=px, py=py)

        for outcome, grp in s[s["shot_outcome"] != "Goal"].groupby("shot_outcome"):
            ax.scatter(
                grp["px"], grp["py"], s=xg_size(grp["shot_xg"]),
                marker=OUTCOME_MARKERS.get(outcome, "o"),
                facecolor=to_rgba(color, 0.35),
                edgecolor=to_rgba(color, 0.95),
                linewidth=1.3, zorder=5,
            )

        goals = s[s["shot_outcome"] == "Goal"]
        ax.scatter(
            goals["px"], goals["py"],
            s=xg_size(goals["shot_xg"]) * 0.9 + 260, marker="*",
            facecolor=GOLD, edgecolor=color, linewidth=2.0, zorder=7,
            path_effects=[pe.withStroke(linewidth=9, foreground=GOLD,
                                        alpha=0.22)],
        )
        for _, g in goals.iterrows():
            dy = -19 if g["py"] < 40 else 19
            ax.annotate(
                goal_label(g), (g["px"], g["py"]),
                xytext=(0, dy), textcoords="offset points",
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color=TEXT, path_effects=OUTLINE(PITCH), zorder=8,
            )

        # title sits over the half this team attacks
        st = team_stats(shots, team)
        ha, x_pos = ("right", 1.0) if i == 0 else ("left", 0.0)
        arrow = "attacking  \u2192" if i == 0 else "\u2190  attacking"
        ax.text(x_pos, 1.075, team, transform=ax.transAxes, fontsize=19,
                fontweight="bold", color=color, ha=ha, va="bottom")
        ax.text(
            x_pos, 1.025,
            f"{st['Shots']} shots   \u00b7   {st['Goals']} goals   \u00b7   "
            f"{st['xG']:.2f} xG",
            transform=ax.transAxes, fontsize=11, color=MUTED, ha=ha,
            va="bottom",
        )
        ax.text(x_pos, -0.035, arrow, transform=ax.transAxes, fontsize=10,
                color=color, ha=ha, va="top", fontweight="bold", alpha=0.9)


def combined_legend(fig, y=0.03):
    grey = "#aab8c2"
    handles = [
        Line2D([0], [0], marker=m, ls="none", markersize=9,
               markerfacecolor=to_rgba(grey, 0.35), markeredgecolor=grey,
               label=name)
        for name, m in OUTCOME_LEGEND
    ]
    handles.append(Line2D([0], [0], marker="*", ls="none", markersize=15,
                          markerfacecolor=GOLD, markeredgecolor="white",
                          label="Goal"))
    for v in [0.05, 0.2, 0.5]:
        handles.append(Line2D([0], [0], marker="o", ls="none",
                              markersize=np.sqrt(xg_size(v)),
                              markerfacecolor=to_rgba(grey, 0.2),
                              markeredgecolor=grey, label=f"xG {v}"))
    fig.legend(handles=handles, loc="lower center", ncol=8, frameon=False,
               labelcolor=MUTED, fontsize=10, handletextpad=0.5,
               columnspacing=1.8, bbox_to_anchor=(0.5, y))


def plot_shot_map_combined(events, output_path, title=TITLE):
    """Both teams on one full pitch, each attacking its own end."""
    shots = prepare_shots(events)
    teams = get_teams(shots)[:2]
    colors = get_team_colors(teams)
    goals = {t: team_stats(shots, t)["Goals"] for t in teams}

    fig, ax = plt.subplots(figsize=(14, 8.8))
    plt.subplots_adjust(left=0.04, right=0.96, top=0.76, bottom=0.15)

    draw_combined_shot_map(ax, shots, teams, colors)

    fig.text(0.04, 0.965, f"{title}: shot map", fontsize=22,
             fontweight="bold", color=TEXT, ha="left", va="top")
    fig.text(0.04, 0.915,
             f"{teams[0]} {goals[teams[0]]} \u2013 {goals[teams[1]]} "
             f"{teams[1]}   \u00b7   every shot, each team attacking its own "
             f"end, sized by xG",
             fontsize=11, color=MUTED, ha="left", va="top")

    combined_legend(fig, y=0.06)
    add_footer(fig, FOOTER)
    save_figure(fig, output_path)
    return shots


# keep the old name working
plot_shot_timeline = plot_xg_race


if __name__ == "__main__":
    # events = pd.read_csv("events.csv")
    # plot_dashboard(events, "outputs/dashboard.png")
    pass