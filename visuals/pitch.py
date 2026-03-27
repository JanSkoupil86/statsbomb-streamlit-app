from mplsoccer import Pitch

def shot_map(events, team):
    pitch = Pitch()
    fig, ax = pitch.draw()

    shots = events[
        (events["type.name"] == "Shot") &
        (events["team.name"] == team) &
        (events["location"].notnull())
    ]

    x = shots["location"].apply(lambda x: x[0])
    y = shots["location"].apply(lambda x: x[1])

    pitch.scatter(x, y, ax=ax)

    return fig
