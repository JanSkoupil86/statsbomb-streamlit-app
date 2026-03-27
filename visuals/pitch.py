import plotly.graph_objects as go
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
import numpy as np

# =============================
# STATIC VERSION (WITH ⚽ ICONS)
# =============================
def get_ball_image():
    try:
        img_path = Path("assets/football.png")
        if img_path.exists():
            return plt.imread(img_path)
        return None
    except:
        return None


def shot_map_two_teams(events, team1, team2, color1, color2):
    pitch = Pitch()
    fig, ax = pitch.draw()

    ball_img = get_ball_image()

    def jitter(arr, scale=0.3):
        return arr + np.random.uniform(-scale, scale, size=len(arr))

    def plot_team(team, color):
        shots = events[
            (events["type.name"] == "Shot") &
            (events["team.name"] == team) &
            (events["location"].notnull())
        ]

        if shots.empty:
            return

        x = shots["location"].apply(lambda x: x[0])
        y = shots["location"].apply(lambda x: x[1])

        x = jitter(x)
        y = jitter(y)

        xg = shots["shot.statsbomb_xg"].fillna(0.01)
        sizes = xg * 900

        goals = shots["shot.outcome.name"] == "Goal"

        # Shots
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

        # Goals (⚽)
        for xi, yi in zip(x[goals], y[goals]):
            if ball_img is not None:
                image = OffsetImage(ball_img, zoom=0.03)
                ab = AnnotationBbox(image, (xi, yi), frameon=False)
                ax.add_artist(ab)

    plot_team(team1, color1)
    plot_team(team2, color2)

    ax.legend(loc="upper right")
    return fig


# =============================
# INTERACTIVE VERSION
# =============================
def shot_map_interactive(events, team1, team2, color1, color2):

    shots = events[events["type.name"] == "Shot"].copy()

    shots["x"] = shots["location"].apply(lambda x: x[0] if isinstance(x, list) else None)
    shots["y"] = shots["location"].apply(lambda x: x[1] if isinstance(x, list) else None)

    shots = shots.dropna(subset=["x", "y"])

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
                size=team_shots["shot.statsbomb_xg"].fillna(0.01) * 40,
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

    # Full pitch
    shapes = [
        dict(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(color="black")),
        dict(type="line", x0=60, y0=0, x1=60, y1=80, line=dict(color="black")),
        dict(type="circle", x0=50, y0=30, x1=70, y1=50, line=dict(color="black")),
        dict(type="rect", x0=0, y0=18, x1=18, y1=62, line=dict(color="black")),
        dict(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(color="black")),
        dict(type="rect", x0=0, y0=30, x1=6, y1=50, line=dict(color="black")),
        dict(type="rect", x0=114, y0=30, x1=120, y1=50, line=dict(color="black")),
    ]

    fig.update_layout(
        shapes=shapes,
        xaxis=dict(range=[0, 120], visible=False),
        yaxis=dict(range=[80, 0], visible=False),
        plot_bgcolor="white",
        height=600
    )

    return fig
