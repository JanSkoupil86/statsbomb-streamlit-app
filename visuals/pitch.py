from mplsoccer import Pitch
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
import numpy as np
import matplotlib.colors as mcolors

# -----------------------------
# LOAD IMAGE SAFELY
# -----------------------------
def get_ball_image():
    try:
        img_path = Path("assets/football.png")
        if img_path.exists():
            return plt.imread(img_path)
        else:
            return None
    except Exception:
        return None

# -----------------------------
# TINT IMAGE (team color)
# -----------------------------
def tint_image(img, color):
    if img is None:
        return None

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

    # -----------------------------
    # JITTER FUNCTION
    # -----------------------------
    def jitter(arr, scale=0.4):
        return arr + np.random.uniform(-scale, scale, size=len(arr))

    def plot_team(team, color_hex):
        color = mcolors.to_rgb(color_hex)

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
        # GOALS (ICON OR FALLBACK)
        # -----------------------------
        tinted_ball = tint_image(base_img, color)

        for xi, yi in zip(x[goals], y[goals]):
            if tinted_ball is not None:
                image = OffsetImage(tinted_ball, zoom=0.035)
                ab = AnnotationBbox(image, (xi, yi), frameon=False)
                ax.add_artist(ab)
            else:
                # Fallback if image fails
                ax.scatter(xi, yi, color=color_hex, edgecolor="black", s=80, zorder=5)

    # Plot both teams
    plot_team(team1, color1)
    plot_team(team2, color2)

    # -----------------------------
    # CLEAN LEGEND (teams only)
    # -----------------------------
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right")

    # -----------------------------
    # EXPLANATION TEXT
    # -----------------------------
    ax.text(
        60, 5,
        "Bubble size = xG | ⚽ = Goal",
        ha="center",
        fontsize=10
    )

    return fig
