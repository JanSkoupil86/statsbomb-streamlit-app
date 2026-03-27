import json
import pandas as pd

def load_events(match_id):
    with open(f"data/events/{match_id}.json") as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    return df
