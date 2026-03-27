import streamlit as st
from loaders.events import load_events

@st.cache_data
def cached_load_events(match_id):
    return load_events(match_id)
