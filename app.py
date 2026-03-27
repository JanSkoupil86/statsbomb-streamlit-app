import streamlit as st
from loaders.competitions import load_competitions
from loaders.matches import load_matches
from utils.cache import cached_load_events
from analytics.xg import team_xg

# Static + Interactive visuals
from visuals.pitch import shot_map_two_teams
from visuals.pitch import shot_map_interactive

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
    comps["competition_name"].dropna().unique()
)

comp_df = comps[comps["competition_name"] == competition]

season = st.sidebar.selectbox(
    "Season",
    comp_df["season_name"].dropna().unique()
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
    st.error("Failed to load matches data")
    st.stop()

# -----------------------------
# MATCH LABEL (nested JSON fix)
# -----------------------------
def get_match_label(row):
    home = row.get("home_team", {}).get("home_team_name", "Unknown")
    away = row.get("away_team", {}).get("away_team_name", "Unknown")
    return f"{home} vs {away}"

match_labels = matches.apply(get_match_label, axis=1)

match_choice = st.sidebar.selectbox("Match", match_labels)

match_index = match_labels[match_labels == match_choice].index[0]
match_row = matches.iloc[match_index]
match_id = match_row["match_id"]

# -----------------------------
# DISPLAY MATCH TITLE
# -----------------------------
st.subheader(match_choice)

# -----------------------------
# LOAD EVENTS
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
teams = list(events["team.name"].dropna().unique())

team1 = st.sidebar.selectbox("Team 1", teams, index=0)
team2 = st.sidebar.selectbox(
    "Team 2",
    teams,
    index=1 if len(teams) > 1 else 0
)

if team1 == team2:
    st.warning("Please select two different teams.")
    st.stop()

# -----------------------------
# COLOR PICKERS
# -----------------------------
color1 = st.sidebar.color_picker("Team 1 Color", "#1f77b4")
color2 = st.sidebar.color_picker("Team 2 Color", "#d62728")

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs(["Overview", "Shot Map", "Interactive"])

# -----------------------------
# OVERVIEW TAB
# -----------------------------
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 xG Comparison")

        xg1 = team_xg(events, team1)
        xg2 = team_xg(events, team2)

        st.metric(f"{team1} xG", round(xg1, 2))
        st.metric(f"{team2} xG", round(xg2, 2))

    with col2:
        st.subheader("ℹ️ Match Info")
        st.write(f"Match ID: {match_id}")
        st.write(f"Teams: {team1} vs {team2}")

# -----------------------------
# STATIC SHOT MAP
# -----------------------------
with tab2:
    st.subheader("🔥 Shot Map (xG-weighted, goals highlighted)")

    try:
        fig = shot_map_two_teams(events, team1, team2, color1, color2)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Failed to render shot map: {e}")

# -----------------------------
# INTERACTIVE SHOT MAP
# -----------------------------
with tab3:
    st.subheader("🖱️ Interactive Shot Map (hover for details)")

    try:
        fig = shot_map_interactive(events, team1, team2, color1, color2)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render interactive map: {e}")
