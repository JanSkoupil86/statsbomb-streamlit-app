import plotly.graph_objects as go
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
import numpy as np

# =============================
# LOAD BALL IMAGE
# =============================
def get_ball_image():
    try:
        img_path = Path("assets/football.png")
        if img_path.exists():
            return plt.imread(img_path)
        return None
    except:
        return None


# =============================
# STATIC HALF-PITCH (BEST VISUAL)
# =============================
def shot_map_two_teams(events, team1, team2, color1, color2):
    pitch = Pitch(half=True)
    fig, ax = pitch.draw()

    ball_img = get_ball_image()

    def plot_team(team, color):
        shots = events[
            (events["type.name"] == "Shot") &
            (events["team.name"] == team) &
            (events["location"].notnull())
        ].copy()

        if shots.empty:
            return

        # Extract coordinates
        shots["x"] = shots["location"].apply(lambda x: x[0])
        shots["y"] = shots["location"].apply(lambda x: x[1])

        # Flip all shots to attacking direction
        shots.loc[shots["x"] < 60, "x"] = 120 - shots["x"]
        shots.loc[shots["y"] < 40, "y"] = 80 - shots["y"]

        x = shots["x"]
        y = shots["y"]

        # xG sizing
        xg = shots["shot.statsbomb_xg"].fillna(0.01)
        sizes = xg * 900

        # Identify goals
        goals = shots["shot.outcome.name"] == "Goal"

        # Plot all shots
        pitch.scatter(
            x, y,
            ax=ax,
            s=sizes,
            color=color,
            alpha=0.3,
            edgecolors="black",
            linewidth=0.5,
            label=team
        )

        # Plot goals as ⚽ icons
        for xi, yi in zip(x[goals], y[goals]):
            if ball_img is not None:
                image = OffsetImage(ball_img, zoom=0.035)
                ab = AnnotationBbox(image, (xi, yi), frameon=False)
                ax.add_artist(ab)

    plot_team(team1, color1)
    plot_team(team2, color2)

    ax.legend(loc="upper right")
    return fig


# =============================
# INTERACTIVE HALF-PITCH (PLOTLY)
# =============================
def shot_map_interactive(events, team1, team2, color1, color2):

    shots = events[events["type.name"] == "Shot"].copy()

    # Extract coordinates safely
    shots["x"] = shots["location"].apply(lambda x: x[0] if isinstance(x, list) else None)
    shots["y"] = shots["location"].apply(lambda x: x[1] if isinstance(x, list) else None)

    shots = shots.dropna(subset=["x", "y"])

    # Flip shots to attacking direction
    shots.loc[shots["x"] < 60, "x"] = 120 - shots["x"]
    shots.loc[shots["y"] < 40, "y"] = 80 - shots["y"]

    fig = go.Figure()

    def plot_team(team, color):
        team_shots = shots[shots["team.name"] == team]

        if team_shots.empty:
            return

        hover_text = (
            "Player: " + team_shots["player.name"].fillna("Unknown") +
            "<br>xG: " + team_shots["shot.statsbomb_xg"].fillna(0).round(3).astype(str) +
            "<br>Minute: " + team_shots["minute"].astype(str) +
            "<br>Outcome: " + team_shots["shot.outcome.name"].fillna("Unknown")
        )

        fig.add_trace(go.Scatter(
            x=team_shots["x"],
            y=team_shots["y"],
            mode="markers",
            marker=dict(
                size=team_shots["shot.statsbomb_xg"].fillna(0.01) * 50,
                color=color,
                opacity=0.7,
                line=dict(width=1, color="black")
            ),
            name=team,
            hovertext=hover_text,
            hoverinfo="text"
        ))

    plot_team(team1, color1)
    plot_team(team2, color2)

    # -----------------------------
    # HALF PITCH SHAPES
    # -----------------------------
    shapes = [
        # Pitch boundary
        dict(type="rect", x0=60, y0=0, x1=120, y1=80, line=dict(color="black")),
        # Penalty box
        dict(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(color="black")),
        # 6-yard box
        dict(type="rect", x0=114, y0=30, x1=120, y1=50, line=dict(color="black")),
        # Penalty spot
        dict(type="circle", x0=109-0.5, y0=40-0.5, x1=109+0.5, y1=40+0.5, fillcolor="black"),
        # Arc
        dict(type="circle", x0=100, y0=30, x1=120, y1=50, line=dict(color="black")),
    ]

    fig.update_layout(
        shapes=shapes,
        xaxis=dict(range=[60, 120], visible=False),
        yaxis=dict(range=[80, 0], visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=600,
        showlegend=True
    )

    return fig
