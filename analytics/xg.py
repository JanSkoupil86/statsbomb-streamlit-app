def team_xg(events, team_name):
    shots = events[events["type.name"] == "Shot"]
    team_shots = shots[shots["team.name"] == team_name]

    if "shot.statsbomb_xg" not in team_shots:
        return 0

    return team_shots["shot.statsbomb_xg"].sum()
