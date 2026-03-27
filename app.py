import streamlit as st
from utils.cache import cached_load_events
from analytics.xg import team_xg
from visuals.pitch import shot_map

st.set_page_config(layout="wide")

st.title("⚽ StatsBomb Analytics Dashboard")

# Sidebar
st.sidebar.header("Filters")
match_id = st.sidebar.text_input("Match ID")

if match_id:
    try:
        events = cached_load_events(match_id)

        teams = events["team.name"].dropna().unique()
        team = st.sidebar.selectbox("Select Team", teams)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Key Metrics")
            xg = team_xg(events, team)
            st.metric("xG", round(xg, 2))

        with col2:
            st.subheader("🔥 Shot Map")
            fig = shot_map(events, team)
            st.pyplot(fig)

    except FileNotFoundError:
        st.error("Match file not found. Check your match_id.")
