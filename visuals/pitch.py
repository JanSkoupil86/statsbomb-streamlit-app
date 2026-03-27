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
# FULL PITCH SHOT MAP
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

        # Extract coordinates
        shots["x"] = shots["location"].apply(lambda x: x[0])
        shots["y"] = shots["location"].apply(lambda x: x[1])

        # Slight jitter to reduce overlap
        x = jitter(shots["x"])
        y = jitter(shots["y"])

        # =============================
        # BIGGER BUBBLES (KEY CHANGE)
        # =============================
        xg = shots["shot.statsbomb_xg"].fillna(0.01)

        # Recommended scaling
        sizes = (xg + 0.03) * 2200

        # Identify goals
        goals = shots["shot.outcome.name"] == "Goal"

        # -----------------------------
        # ALL SHOTS
        # -----------------------------
        pitch.scatter(
            x,
            y,
            ax=ax,
            s=sizes,
            color=color,
            alpha=0.35,
            edgecolors="black",
            linewidth=0.6,
            label=team
        )

        # -----------------------------
        # GOALS (⚽ ICON)
        # -----------------------------
        for xi, yi in zip(x[goals], y[goals]):
            if ball_img is not None:
                image = OffsetImage(ball_img, zoom=0.035)
                ab = AnnotationBbox(image, (xi, yi), frameon=False)
                ax.add_artist(ab)
            else:
                # Fallback if image missing
                ax.scatter(xi, yi, color=color, edgecolor="black", s=120, zorder=5)

    # Plot both teams
    plot_team(team1, color1)
    plot_team(team2, color2)

    # -----------------------------
    # CLEAN LEGEND
    # -----------------------------
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right")

    return fig
