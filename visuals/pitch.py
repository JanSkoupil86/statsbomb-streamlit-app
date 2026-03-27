import plotly.graph_objects as go
import pandas as pd

# -----------------------------
# MAIN FUNCTION (INTERACTIVE)
# -----------------------------
def shot_map_interactive(events, team1, team2, color1, color2):

    # Filter shots
    shots = events[events["type.name"] == "Shot"].copy()

    # Extract coordinates
    shots["x"] = shots["location"].apply(lambda x: x[0] if isinstance(x, list) else None)
    shots["y"] = shots["location"].apply(lambda x: x[1] if isinstance(x, list) else None)

    shots = shots.dropna(subset=["x", "y"])

    fig = go.Figure()

    def plot_team(team, color):
        team_shots = shots[shots["team.name"] == team]

        if team_shots.empty:
            return

        # Hover text
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

    # Plot both teams
    plot_team(team1, color1)
    plot_team(team2, color2)

    # -----------------------------
    # PITCH LAYOUT (StatsBomb dims)
    # -----------------------------
    fig.update_layout(
        xaxis=dict(range=[0, 120], showgrid=False, zeroline=False),
        yaxis=dict(range=[80, 0], showgrid=False, zeroline=False),  # flipped
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=600,
        showlegend=True
    )

    return fig
