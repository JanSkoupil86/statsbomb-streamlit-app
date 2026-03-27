from mplsoccer import Pitch

def shot_map_two_teams(events, team1, team2, color1, color2):
    pitch = Pitch()
    fig, ax = pitch.draw()

    # Team 1 shots
    shots1 = events[
        (events["type.name"] == "Shot") &
        (events["team.name"] == team1) &
        (events["location"].notnull())
    ]

    x1 = shots1["location"].apply(lambda x: x[0])
    y1 = shots1["location"].apply(lambda x: x[1])

    pitch.scatter(x1, y1, ax=ax, color=color1, label=team1)

    # Team 2 shots
    shots2 = events[
        (events["type.name"] == "Shot") &
        (events["team.name"] == team2) &
        (events["location"].notnull())
    ]

    x2 = shots2["location"].apply(lambda x: x[0])
    y2 = shots2["location"].apply(lambda x: x[1])

    pitch.scatter(x2, y2, ax=ax, color=color2, label=team2)

    ax.legend()

    return fig
