import pandas as pd

def load_matches(comp_id, season_id):
    url = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/{comp_id}/{season_id}.json"
    return pd.read_json(url)
