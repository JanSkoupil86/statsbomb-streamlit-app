def team_xg(events, team):
    shots = events[events["type.name"] == "Shot"]
    shots = shots[shots["team.name"] == team]

    if "shot.statsbomb_xg" not in shots:
        return 0

    return shots["shot.statsbomb_xg"].sum()
