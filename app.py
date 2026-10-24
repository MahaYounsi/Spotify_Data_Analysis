"""Point d'entrée du dashboard : données, filtres de la sidebar et navigation.

Lancer avec : streamlit run app.py
"""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Spotify : le genre fait le hit", page_icon="🎧", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("data/dataset.csv", index_col=0).dropna()
    # Popularité 0 = surtout des doublons (rééditions, compilations) : on les retire
    df = df[df["popularity"] > 0].copy()
    df["duration_min"] = df["duration_ms"] / 60_000
    return df


df = load_data()

# Filtres déclarés ici une seule fois : ils restent identiques sur toutes les pages
with st.sidebar:
    st.header("Filtres")
    genres = st.multiselect("Genres", sorted(df["track_genre"].unique()), placeholder="Tous les genres")
    explicit = st.radio("Paroles", ["Tous les titres", "Explicites", "Non explicites"])

seg = df
if genres:
    seg = seg[seg["track_genre"].isin(genres)]
if explicit == "Explicites":
    seg = seg[seg["explicit"]]
elif explicit == "Non explicites":
    seg = seg[~seg["explicit"]]

# Données transmises aux pages : catalogue complet et sélection filtrée
st.session_state["df"] = df
st.session_state["seg"] = seg

page = st.navigation([
    st.Page("pages/1_synthese.py", title="Synthèse", icon="🎯"),
    st.Page("pages/2_genres.py", title="Détail : genres", icon="🏷️"),
])
page.run()
