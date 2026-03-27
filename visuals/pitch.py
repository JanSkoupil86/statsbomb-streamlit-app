import matplotlib.pyplot as plt
from mplsoccer import Pitch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
import numpy as np
import plotly.graph_objects as go

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
# STATIC FULL PITCH
# =============================
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
        ].copy()

        if shots.empty:
            return

        shots["x"] = shots["location"].apply(lambda x: x[0])
        shots["y"] = shots["location"].apply(lambda x: x[1])

        x = jitter(shots["x"])
        y = jitter(shots["y"])

        xg = shots["shot.statsbomb_xg"].fillna(0.01)
        sizes = (xg + 0.03) * 2200

        goals = shots["shot.outcome.name"] == "Goal"

        pitch.scatter(
            x, y,
            ax=ax,
            s=sizes,
            color=color,
            alpha=0.35,
            edgecolors="black",
            linewidth=0.6,
            label=team
        )

        for xi, yi in zip(x[goals], y[goals]):
            if ball_img is not None:
                image = OffsetImage(ball_img, zoom=0.035)
                ab = AnnotationBbox(image, (xi, yi), frameon=False)
                ax.add_artist(ab)

    plot_team(team1, color1)
    plot_team(team2, color2)

    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right")

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

    fig.update_layout(
        xaxis=dict(range=[0, 120], visible=False),
        yaxis=dict(range=[80, 0], visible=False),
        plot_bgcolor="white",
        height=600
    )

    return fig
