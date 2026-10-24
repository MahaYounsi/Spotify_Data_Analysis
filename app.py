"""Point d'entrée du dashboard : filtres de la sidebar et navigation entre les pages.

Lancer avec : streamlit run app.py
"""
import streamlit as st

from utils import load_data

st.set_page_config(page_title="Spotify : le genre fait le hit", page_icon="🎧", layout="wide")

df = load_data()

# Les filtres sont déclarés ici une seule fois : ils restent identiques sur toutes les pages.
with st.sidebar:
    st.header("Filtres")
    st.multiselect("Genres", sorted(df["track_genre"].unique()),
                   placeholder="Tous les genres", key="genres")
    st.radio("Paroles", ["Tous les titres", "Explicites", "Non explicites"], key="explicit")

page = st.navigation([
    st.Page("pages/1_synthese.py", title="Synthèse", icon="🎯"),
    st.Page("pages/2_genres.py", title="Détail : genres", icon="🏷️"),
    st.Page("pages/3_son.py", title="Détail : le son", icon="🎚️"),
])
page.run()
