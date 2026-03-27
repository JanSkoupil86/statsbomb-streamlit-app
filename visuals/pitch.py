from mplsoccer import Pitch
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
import numpy as np

# -----------------------------
# LOAD IMAGE
# -----------------------------
def get_ball_image():
    return plt.imread(Path("assets/football.png"))

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def shot_map_two_teams(events, team1, team2, color1, color2):
    pitch = Pitch()
    fig, ax = pitch.draw()

    ball_img = get_ball_image()

    def jitter(arr, scale=0.4):
        return arr + np.random.uniform(-scale, scale, size=len(arr))

    def plot_team(team, color):
        shots = events[
            (events["type.name"] == "Shot") &
            (events["team.name"] == team) &
            (events["location"].notnull())
        ]

        if shots.empty:
            return

        x = shots["location"].apply(lambda loc: loc[0]).astype(float)
        y = shots["location"].apply(lambda loc: loc[1]).astype(float)

        x = jitter(x)
        y = jitter(y)

        xg = shots.get("shot.statsbomb_xg", 0).fillna(0.01)
        sizes = xg * 900

        goals = shots["shot.outcome.name"] == "Goal"

        # MISSES
        pitch.scatter(
            x[~goals],
            y[~goals],
            ax=ax,
            s=sizes[~goals],
            color=color,
            alpha=0.35,
            edgecolors="black",
            linewidth=0.5,
            label=f"{team} Miss"
        )

        # GOALS (⚽ icons)
        for xi, yi in zip(x[goals], y[goals]):
            image = OffsetImage(ball_img, zoom=0.03)
            ab = AnnotationBbox(image, (xi, yi), frameon=False)
            ax.add_artist(ab)

    # Plot both teams
    plot_team(team1, color1)
    plot_team(team2, color2)

    # -----------------------------
    # CLEAN LEGEND
    # -----------------------------
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))

    ax.legend(unique.values(), unique.keys(), loc="upper right")

    # -----------------------------
    # ADD TEXT EXPLANATION
    # -----------------------------
    ax.text(
        60, 5,
        "⚽ = Goal | Bubble size = xG",
        ha="center",
        fontsize=10,
        color="black"
    )

    return fig
