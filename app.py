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
# STATIC SHOT MAP (FIXED)
# =============================
def shot_map_two_teams(events, team1, team2, color1, color2):
    pitch = Pitch()
    fig, ax = pitch.draw()

    ball_img = get_ball_image()

    def jitter(arr, scale=0.25):
        return arr + np.random.uniform(-scale, scale, size=len(arr))

    def plot_team(team, color):
        shots = events[
            (events["type.name"] == "Shot") &
            (events["team.name"] == team) &
            (events["location"].notnull())
        ].copy()

        if shots.empty:
            return 0

        shots["x"] = shots["location"].apply(lambda x: x[0])
        shots["y"] = shots["location"].apply(lambda x: x[1])

        x = jitter(shots["x"])
        y = jitter(shots["y"])

        xg = shots["shot.statsbomb_xg"].fillna(0.01)

        # ✅ FIXED SIZE (balanced)
        sizes = (xg + 0.02) * 1400

        goals = shots["shot.outcome.name"] == "Goal"

        pitch.scatter(
            x, y,
            ax=ax,
            s=sizes,
            color=color,
            alpha=0.35,
            edgecolors="black",
            linewidth=0.6
        )

        # Goals
        for xi, yi in zip(x[goals], y[goals]):
            if ball_img is not None:
                image = OffsetImage(ball_img, zoom=0.03)
                ab = AnnotationBbox(image, (xi, yi), frameon=False)
                ax.add_artist(ab)

        return xg.sum()

    # Plot teams + get xG totals
    xg1 = plot_team(team1, color1)
    xg2 = plot_team(team2, color2)

    # =============================
    # CUSTOM LEGEND (xG bubbles)
    # =============================
    legend_x = 90
    legend_y = 10

    ax.scatter(legend_x, legend_y, s=300, color=color1, alpha=0.5)
    ax.text(legend_x + 2, legend_y, f"{team1} ({xg1:.2f} xG)", va='center')

    ax.scatter(legend_x, legend_y + 6, s=300, color=color2, alpha=0.5)
    ax.text(legend_x + 2, legend_y + 6, f"{team2} ({xg2:.2f} xG)", va='center')

    return fig


# =============================
# INTERACTIVE MAP (FIXED)
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
                # ✅ FIXED SIZE (bigger)
                size=team_shots["shot.statsbomb_xg"].fillna(0.01) * 60,
                color=color,
                opacity=0.75,
                line=dict(width=1, color="black")
            ),
            name=team,
            hovertext=hover_text,
            hoverinfo="text"
        ))

    plot_team(team1, color1)
    plot_team(team2, color2)

    # =============================
    # FULL PITCH (RESTORED)
    # =============================
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
