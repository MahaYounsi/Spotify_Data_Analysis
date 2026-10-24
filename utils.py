"""Fonctions partagées : chargement des données, filtres et calculs."""
import numpy as np
import pandas as pd
import streamlit as st

DATA_PATH = "data/dataset.csv"

HIT = 65   # popularité minimale d'un « hit » (top 10 % du catalogue)
FLOP = 20  # en dessous : titre sans audience

# Une couleur d'accent pour ce qui porte le message, du gris pour le reste
ACCENT = "#2a78d6"
GREY = "#b4b3ad"

AUDIO_FEATURES = {
    "danceability": "Dansabilité",
    "energy": "Énergie",
    "loudness": "Volume",
    "speechiness": "Part de parole",
    "acousticness": "Acoustique",
    "instrumentalness": "Instrumental",
    "liveness": "Live",
    "valence": "Positivité",
    "tempo": "Tempo",
    "duration_min": "Durée",
}


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, index_col=0).dropna()
    # Popularité 0 = surtout des doublons (rééditions, compilations) : on les retire
    df = df[df["popularity"] > 0].copy()
    df["duration_min"] = df["duration_ms"] / 60_000
    return df


def filter_data(df):
    """Applique les filtres choisis dans la sidebar (voir app.py)."""
    genres = st.session_state["genres"]
    explicit = st.session_state["explicit"]
    if genres:
        df = df[df["track_genre"].isin(genres)]
    if explicit == "Explicites":
        df = df[df["explicit"]]
    elif explicit == "Non explicites":
        df = df[~df["explicit"]]
    return df


def hit_rate(df):
    return (df["popularity"] >= HIT).mean()


def genre_r2(df):
    """Part de la variance de popularité expliquée par le genre."""
    genre_mean = df.groupby("track_genre")["popularity"].transform("mean")
    return genre_mean.var() / df["popularity"].var()


def audio_r2(df, features=list(AUDIO_FEATURES)):
    """R² d'une régression linéaire de la popularité sur les variables audio."""
    X = np.column_stack([np.ones(len(df)), df[features]])
    y = df["popularity"].to_numpy()
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    return 1 - (y - X @ coef).var() / y.var()


def genre_stats(df):
    """Une ligne par genre : nombre de titres, popularité médiane, taux de hit et de flop."""
    return (
        df.groupby("track_genre")["popularity"]
        .agg(
            titres="size",
            popularite_mediane="median",
            taux_hit=lambda s: (s >= HIT).mean(),
            taux_flop=lambda s: (s < FLOP).mean(),
        )
        .reset_index()
    )
