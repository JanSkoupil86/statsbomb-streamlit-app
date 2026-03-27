import streamlit as st
from loaders.competitions import load_competitions
from loaders.matches import load_matches
from utils.cache import cached_load_events
from analytics.xg import team_xg
from visuals.pitch import shot_map

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="wide")
st.title("⚽ StatsBomb Match Explorer")

# -----------------------------
# LOAD COMPETITIONS
# -----------------------------
try:
    comps = load_competitions()
except Exception:
    st.error("Failed to load competitions data")
    st.stop()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
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

# -----------------------------
# LOAD MATCHES
# -----------------------------
try:
    matches = load_matches(comp_id, season_id)
except Exception:
    st.error("Failed to load matches")
    st.stop()

match_labels = matches.apply(
    lambda x: f"{x['home_team.home_team_name']} vs {x['away_team.away_team_name']}",
    axis=1
)

match_choice = st.sidebar.selectbox("Match", match_labels)

match_index = match_labels[match_labels == match_choice].index[0]
match_row = matches.iloc[match_index]
match_id = match_row["match_id"]

# -----------------------------
# DISPLAY MATCH TITLE
# -----------------------------
st.subheader(f"{match_choice}")

# -----------------------------
# LOAD EVENTS (WITH SPINNER)
# -----------------------------
try:
    with st.spinner("Loading match data..."):
        events = cached_load_events(match_id)
except Exception:
    st.error("Failed to load match events")
    st.stop()

# -----------------------------
# TEAM SELECTION
# -----------------------------
teams = events["team.name"].dropna().unique()
team = st.sidebar.selectbox("Team", teams)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["Overview", "Shots"])

# -----------------------------
# OVERVIEW TAB
# -----------------------------
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Key Metrics")
        xg = team_xg(events, team)
        st.metric("Expected Goals (xG)", round(xg, 2))

    with col2:
        st.subheader("ℹ️ Info")
        st.write(f"Team: {team}")
        st.write(f"Match ID: {match_id}")

# -----------------------------
# SHOTS TAB
# -----------------------------
with tab2:
    st.subheader("🔥 Shot Map")

    try:
        fig = shot_map(events, team)
        st.pyplot(fig)
    except Exception:
        st.error("Failed to render shot map")
