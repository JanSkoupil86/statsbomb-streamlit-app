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
# COLORIZE IMAGE (key trick)
# -----------------------------
def tint_image(img, color):
    # Normalize image
    img = img / 255 if img.max() > 1 else img.copy()

    tinted = img.copy()
    tinted[..., 0] *= color[0]
    tinted[..., 1] *= color[1]
    tinted[..., 2] *= color[2]

    return tinted

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def shot_map_two_teams(events, team1, team2, color1, color2):
    pitch = Pitch()
    fig, ax = pitch.draw()

    base_img = get_ball_image()

    def jitter(arr, scale=0.4):
        return arr + np.random.uniform(-scale, scale, size=len(arr))

    def plot_team(team, color_hex):
        color = plt.colors.to_rgb(color_hex)

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

        # -----------------------------
        # ALL SHOTS (bubbles)
        # -----------------------------
        pitch.scatter(
            x,
            y,
            ax=ax,
            s=sizes,
            color=color_hex,
            alpha=0.25,
            edgecolors="black",
            linewidth=0.5,
            label=team
        )

        # -----------------------------
        # GOALS (team-colored icons)
        # -----------------------------
        tinted_ball = tint_image(base_img, color)

        for xi, yi in zip(x[goals], y[goals]):
            image = OffsetImage(tinted_ball, zoom=0.035)
            ab = AnnotationBbox(image, (xi, yi), frameon=False)
            ax.add_artist(ab)

    # Plot both teams
    plot_team(team1, color1)
    plot_team(team2, color2)

    # -----------------------------
    # CLEAN LEGEND (teams only)
    # -----------------------------
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right")

    return fig
