import pandas as pd
from pathlib import Path

DATA_PATH = Path(r"C:\Users\Scoby\Downloads\open-data-master\data")

def load_matches(comp_id, season_id):
    path = DATA_PATH / "matches" / str(comp_id) / f"{season_id}.json"
    return pd.read_json(path)
