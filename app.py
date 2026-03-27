import streamlit as st
from loaders.competitions import load_competitions
from loaders.matches import load_matches
from utils.cache import cached_load_events
from analytics.xg import team_xg
from visuals.pitch import shot_map

st.set_page_config(layout="wide")
st.title("⚽ StatsBomb Dashboard")

# Load competitions
comps = load_competitions()

# Sidebar
st.sidebar.header("Filters")

competition = st.sidebar.selectbox(
    "Competition",
    comps["competition_name"].unique()
)

comp_df = comps[comps["competition_name"] == competition]

season = st.sidebar.selectbox(
    "Season",
    comp_df["season_name"].unique()
)

selected = comp_df[
    (comp_df["competition_name"] == competition) &
    (comp_df["season_name"] == season)
]

comp_id = selected["competition_id"].iloc[0]
season_id = selected["season_id"].iloc[0]

# Matches
matches = load_matches(comp_id, season_id)

match_labels = matches.apply(
    lambda x: f"{x['home_team.home_team_name']} vs {x['away_team.away_team_name']}",
    axis=1
)

match_choice = st.sidebar.selectbox("Match", match_labels)

match_row = matches.iloc[match_labels[match_labels == match_choice].index[0]]
match_id = match_row["match_id"]

# Events
events = cached_load_events(match_id)

teams = events["team.name"].dropna().unique()
team = st.sidebar.selectbox("Team", teams)

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("xG")
    st.metric("Expected Goals", round(team_xg(events, team), 2))

with col2:
    st.subheader("Shot Map")
    fig = shot_map(events, team)
    st.pyplot(fig)
