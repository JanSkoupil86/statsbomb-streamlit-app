def shot_map_interactive(events, team1, team2, color1, color2):

    import plotly.graph_objects as go

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

    # -----------------------------
    # FULL PITCH SHAPES
    # -----------------------------
    shapes = []

    # Pitch outline
    shapes.append(dict(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(color="black")))

    # Halfway line
    shapes.append(dict(type="line", x0=60, y0=0, x1=60, y1=80, line=dict(color="black")))

    # Center circle
    shapes.append(dict(type="circle", x0=50, y0=30, x1=70, y1=50, line=dict(color="black")))

    # Left penalty box
    shapes.append(dict(type="rect", x0=0, y0=18, x1=18, y1=62, line=dict(color="black")))

    # Right penalty box
    shapes.append(dict(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(color="black")))

    # Left 6-yard box
    shapes.append(dict(type="rect", x0=0, y0=30, x1=6, y1=50, line=dict(color="black")))

    # Right 6-yard box
    shapes.append(dict(type="rect", x0=114, y0=30, x1=120, y1=50, line=dict(color="black")))

    # Left penalty spot
    shapes.append(dict(type="circle", x0=11-0.5, y0=40-0.5, x1=11+0.5, y1=40+0.5, fillcolor="black"))

    # Right penalty spot
    shapes.append(dict(type="circle", x0=109-0.5, y0=40-0.5, x1=109+0.5, y1=40+0.5, fillcolor="black"))

    # -----------------------------
    # LAYOUT
    # -----------------------------
    fig.update_layout(
        shapes=shapes,
        xaxis=dict(range=[0, 120], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[80, 0], showgrid=False, zeroline=False, visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=600,
        showlegend=True
    )

    return fig
