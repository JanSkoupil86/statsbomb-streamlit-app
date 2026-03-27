import plotly.graph_objects as go
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd

# -----------------------------
# STATIC VERSION
# -----------------------------
def shot_map_two_teams(events, team1, team2, color1, color2):
    pitch = Pitch()
    fig, ax = pitch.draw()

    shots = events[events["type.name"] == "Shot"]

    for team, color in [(team1, color1), (team2, color2)]:
        team_shots = shots[shots["team.name"] == team]

        if team_shots.empty:
            continue

        x = team_shots["location"].apply(lambda x: x[0])
        y = team_shots["location"].apply(lambda x: x[1])

        sizes = team_shots["shot.statsbomb_xg"].fillna(0.01) * 900

        pitch.scatter(
            x, y,
            ax=ax,
            s=sizes,
            color=color,
            alpha=0.4,
            edgecolors="black",
            linewidth=0.5,
            label=team
        )

    ax.legend(loc="upper right")
    return fig


# -----------------------------
# INTERACTIVE VERSION
# -----------------------------
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
                opacity=0.6,
                line=dict(width=1, color="black")
            ),
            name=team,
            hovertext=hover_text,
            hoverinfo="text"
        ))

    plot_team(team1, color1)
    plot_team(team2, color2)

    fig.update_layout(
        xaxis=dict(range=[0, 120], showgrid=False, zeroline=False),
        yaxis=dict(range=[80, 0], showgrid=False, zeroline=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=600,
        showlegend=True
    )

    return fig
