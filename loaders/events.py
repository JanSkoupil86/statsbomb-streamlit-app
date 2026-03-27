import json
import pandas as pd
from pathlib import Path

DATA_PATH = Path(r"C:\Users\Scoby\Downloads\open-data-master\data")

def load_events(match_id):
    file_path = DATA_PATH / "events" / f"{match_id}.json"

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    return pd.json_normalize(data)
