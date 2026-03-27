from mplsoccer import Pitch
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# -----------------------------
# LOAD FOOTBALL IMAGE
# -----------------------------
def get_ball_image():
    return plt.imread("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Soccerball.svg/120px-Soccerball.svg.png")

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def shot_map_two_teams(events, team1, team2, color1, color2):
    pitch = Pitch()
    fig, ax = pitch.draw()

    ball_img = get_ball_image()

    # -----------------------------
    # HELPER FUNCTION
    # -----------------------------
    def plot_team_shots(team, color):
        shots = events[
            (events["type.name"] == "Shot") &
            (events["team.name"] == team) &
            (events["location"].notnull())
        ]

        if shots.empty:
            return

        x = shots["location"].apply(lambda loc: loc[0])
        y = shots["location"].apply(lambda loc: loc[1])

        xg = shots.get("shot.statsbomb_xg", 0)
        sizes = xg.fillna(0.01) * 1200

        goals = shots["shot.outcome.name"] == "Goal"

        # -----------------------------
        # MISSES (BUBBLES)
        # -----------------------------
        pitch.scatter(
            x[~goals],
            y[~goals],
            ax=ax,
            s=sizes[~goals],
            color=color,
            alpha=0.4,
            edgecolors="black",
            linewidth=0.5,
            label=f"{team} Miss"
        )

        # -----------------------------
        # GOALS (IMAGE ICON)
        # -----------------------------
        for xi, yi, si in zip(x[goals], y[goals], sizes[goals]):
            image = OffsetImage(ball_img, zoom=max(0.02, si / 4000))
            ab = AnnotationBbox(image, (xi, yi), frameon=False)
            ax.add_artist(ab)

    # -----------------------------
    # PLOT BOTH TEAMS
    # -----------------------------
    plot_team_shots(team1, color1)
    plot_team_shots(team2, color2)

    # -----------------------------
    # LEGEND CLEANUP
    # -----------------------------
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right")

    return fig
