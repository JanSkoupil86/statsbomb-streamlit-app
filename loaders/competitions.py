import pandas as pd
from pathlib import Path

DATA_PATH = Path(r"C:\Users\Scoby\Downloads\open-data-master\data")

def load_competitions():
    return pd.read_json(DATA_PATH / "competitions.json")
