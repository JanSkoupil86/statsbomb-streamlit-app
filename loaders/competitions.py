import pandas as pd

def load_competitions():
    url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json"
    return pd.read_json(url)
