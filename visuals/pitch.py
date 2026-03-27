from mplsoccer import Pitch
import matplotlib.pyplot as plt

def shot_map(events, team):
    pitch = Pitch()
    fig, ax = pitch.draw()

    shots = events[
        (events["type.name"] == "Shot") &
        (events["team.name"] == team)
    ]

    # Drop null locations
    shots = shots[shots["location"].notnull()]

    x = shots["location"].apply(lambda loc: loc[0])
    y = shots["location"].apply(lambda loc: loc[1])

    pitch.scatter(x, y, ax=ax)

    return fig
