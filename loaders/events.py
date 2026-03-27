import requests
import pandas as pd

def load_events(match_id):
    url = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json"
    
    r = requests.get(url)
    data = r.json()
    
    return pd.json_normalize(data)
