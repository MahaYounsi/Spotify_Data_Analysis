"""Chargement, filtrage et calculs partagés par toutes les pages du dashboard."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "dataset.csv"

# Variables audio fournies par l'API Spotify (libellés affichés dans le dashboard)
AUDIO_FEATURES = {
    "danceability": "Dansabilité",
    "energy": "Énergie",
    "loudness": "Volume (dB)",
    "speechiness": "Part de parole",
    "acousticness": "Acoustique",
    "instrumentalness": "Instrumental",
    "liveness": "Live",
    "valence": "Positivité (valence)",
    "tempo": "Tempo (BPM)",
    "duration_min": "Durée (min)",
}

# Hiérarchie visuelle : une seule couleur d'accent pour ce qui porte le message,
# un gris neutre pour le contexte.
ACCENT = "#2a78d6"
MUTED = "#b4b3ad"
FLOP_THRESHOLD = 20  # en dessous : titre sans audience


@st.cache_data(show_spinner="Chargement des données Spotify…")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, index_col=0)
    df = df.dropna(subset=["artists", "album_name", "track_name"])
    # Popularité = 0 : essentiellement des doublons (rééditions, compilations) de titres
    # connus, Spotify n'attribuant la popularité qu'à la version principale. On les exclut.
    df = df[df["popularity"] > 0].copy()
    df["duration_min"] = df["duration_ms"] / 60_000
    df["track_genre"] = df["track_genre"].astype("category")
    return df.drop(columns=["duration_ms"])


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    mask = df["duration_min"].between(*filters["duration"])
    if filters["genres"]:
        mask &= df["track_genre"].isin(filters["genres"])
    if filters["explicit"] == "Explicites uniquement":
        mask &= df["explicit"]
    elif filters["explicit"] == "Non explicites uniquement":
        mask &= ~df["explicit"]
    out = df[mask].copy()
    out["track_genre"] = out["track_genre"].cat.remove_unused_categories()
    return out


def get_filters() -> dict:
    return st.session_state["filters"]


def get_segment() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Renvoie (catalogue complet, segment filtré, filtres)."""
    df = load_data()
    filters = get_filters()
    return df, apply_filters(df, filters), filters


# --- Indicateurs -------------------------------------------------------------

def hit_rate(df: pd.DataFrame, threshold: int) -> float:
    return float((df["popularity"] >= threshold).mean()) if len(df) else float("nan")


def genre_eta2(df: pd.DataFrame) -> float:
    """Part de la variance de popularité expliquée par le genre (eta²)."""
    if df["track_genre"].nunique() < 2:
        return float("nan")
    y = df["popularity"]
    group_means = df.groupby("track_genre", observed=True)["popularity"].transform("mean")
    return float(((group_means - y.mean()) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def audio_r2(df: pd.DataFrame, features: list[str] | None = None) -> float:
    """R² d'une régression linéaire de la popularité sur les variables audio."""
    features = features or list(AUDIO_FEATURES)
    if len(df) <= len(features) + 1:
        return float("nan")
    X = np.column_stack([np.ones(len(df)), df[features].to_numpy(dtype=float)])
    y = df["popularity"].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(1 - (y - X @ coef).var() / y.var())


def genre_table(df: pd.DataFrame, threshold: int) -> pd.DataFrame:
    return (
        df.groupby("track_genre", observed=True)
        .agg(
            titres=("popularity", "size"),
            popularite_mediane=("popularity", "median"),
            taux_hit=("popularity", lambda s: (s >= threshold).mean()),
            taux_flop=("popularity", lambda s: (s < FLOP_THRESHOLD).mean()),
        )
        .reset_index()
        .rename(columns={"track_genre": "genre"})
    )


def decile_profile(df: pd.DataFrame, feature: str) -> pd.DataFrame:
    """Popularité médiane par décile d'une variable audio (déciles d'effectifs égaux)."""
    deciles = pd.qcut(df[feature].rank(method="first"), 10, labels=range(1, 11))
    return (
        df.groupby(deciles, observed=True)
        .agg(valeur_mediane=(feature, "median"), popularite_mediane=("popularity", "median"))
        .reset_index(names="decile")
    )


# --- Mise en forme -----------------------------------------------------------

def style_fig(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=30, t=10, b=10),
        barcornerradius=4,
        bargap=0.25,
        showlegend=False,
        hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=False)
    return fig


def pct(x: float) -> str:
    return "—" if pd.isna(x) else f"{x:.0%}".replace("%", " %")


def pts(x: float) -> str:
    return f"{x:+.1f} pts".replace(".", ",")
