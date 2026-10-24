"""Point d'entrée : navigation multi-pages et filtres partagés dans la sidebar.

Lancer avec :  streamlit run app.py
"""
import streamlit as st

from utils import load_data

st.set_page_config(page_title="Spotify : le genre fait le hit", page_icon="🎧", layout="wide")

df = load_data()

# Les filtres sont déclarés ici (et non dans chaque page) pour rester identiques
# quand on passe d'une vue à l'autre.
with st.sidebar:
    st.header("Filtres")
    genres = st.multiselect(
        "Genres",
        options=sorted(df["track_genre"].cat.categories),
        placeholder="Tous les genres (114)",
        help="Laisser vide pour analyser tout le catalogue.",
        key="f_genres",
    )
    explicit = st.radio(
        "Paroles explicites",
        ["Tous les titres", "Explicites uniquement", "Non explicites uniquement"],
        key="f_explicit",
    )
    duration = st.slider(
        "Durée du titre (min)", 0.5, 10.0, (0.5, 10.0), step=0.5, key="f_duration"
    )
    with st.expander("Paramètres"):
        threshold = st.slider(
            "Seuil de « hit » (popularité ≥)", 40, 90, 65, step=5, key="f_threshold",
            help="65 correspond aux 10 % de titres les plus populaires du catalogue.",
        )

st.session_state["filters"] = {
    "genres": genres,
    "explicit": explicit,
    "duration": duration,
    "threshold": threshold,
}

pg = st.navigation(
    [
        st.Page("pages/1_synthese.py", title="Synthèse", icon="🎯", default=True),
        st.Page("pages/2_genres.py", title="Détail : genres", icon="🏷️"),
        st.Page("pages/3_son.py", title="Détail : le son", icon="🎚️"),
    ]
)

with st.sidebar:
    st.divider()
    st.caption(
        f"Source : Spotify Tracks Dataset (Kaggle, maharshipandya) : "
        f"{len(df):,} titres × genre après nettoyage.".replace(",", " ")
    )

pg.run()
