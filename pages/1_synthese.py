"""Vue synthèse : le message, les 3 KPIs et la preuve principale."""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

HIT = 65  # popularité minimale d'un « hit » (top 10 % du catalogue)
AUDIO_FEATURES = {
    "danceability": "Dansabilité", "energy": "Énergie", "loudness": "Volume",
    "speechiness": "Part de parole", "acousticness": "Acoustique", "instrumentalness": "Instrumental",
    "liveness": "Live", "valence": "Positivité", "tempo": "Tempo", "duration_min": "Durée",
}

df = st.session_state["df"]
seg = st.session_state["seg"]


def genre_r2(data):
    """Part de la variance de popularité expliquée par le genre."""
    genre_mean = data.groupby("track_genre")["popularity"].transform("mean")
    return genre_mean.var() / data["popularity"].var()


def audio_r2(data, features=list(AUDIO_FEATURES)):
    """R² d'une régression linéaire de la popularité sur les variables audio."""
    X = np.column_stack([np.ones(len(data)), data[features]])
    y = data["popularity"].to_numpy()
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    return 1 - (y - X @ coef).var() / y.var()


st.title("Sur Spotify, c'est le genre, pas le son, qui fait la popularité d'un titre")
st.write("**Pour l'équipe A&R** : avant d'optimiser la production d'un titre, choisissez le bon genre.")

if len(seg) < 100:
    st.warning("Trop peu de titres pour ces filtres : élargissez la sélection.")
    st.stop()

# --- Zone KPIs : chaque indicateur est comparé au catalogue complet ---
seg_hit, all_hit = (seg["popularity"] >= HIT).mean(), (df["popularity"] >= HIT).mean()
seg_med, all_med = seg["popularity"].median(), df["popularity"].median()

col1, col2, col3 = st.columns(3)
col1.metric("Taux de hit", f"{seg_hit:.0%}", f"{100 * (seg_hit - all_hit):+.1f} pts vs catalogue",
            help=f"Part des titres avec une popularité ≥ {HIT}.", border=True)
col2.metric("Popularité médiane", f"{seg_med:.0f}", f"{seg_med - all_med:+.0f} pts vs catalogue",
            help="Sur une échelle de 0 à 100.", border=True)
col3.metric("Expliqué par le genre", f"{genre_r2(seg):.0%}", f"vs {audio_r2(seg):.0%} par le son",
            delta_color="off", help="Part de la variance de popularité expliquée.", border=True)

# --- Zone détail ---
tab1, tab2 = st.tabs(["Genre vs son", "Données"])

with tab1:
    st.subheader("Le genre explique plus de popularité que n'importe quelle variable audio")
    rows = [("Genre", genre_r2(seg)), ("Les 10 variables audio réunies", audio_r2(seg))]
    rows += [(label, audio_r2(seg, [col])) for col, label in AUDIO_FEATURES.items()]
    proof = pd.DataFrame(rows, columns=["facteur", "r2"]).sort_values("r2")
    proof["couleur"] = proof["facteur"].eq("Genre")
    fig = px.bar(proof, x="r2", y="facteur", orientation="h", text_auto=".0%",
                 color="couleur", color_discrete_map={True: "#2a78d6", False: "#b4b3ad"},
                 labels={"r2": "Part de la variance de popularité expliquée", "facteur": ""})
    fig.update_layout(showlegend=False, xaxis_tickformat=".0%")
    st.plotly_chart(fig)

with tab2:
    st.subheader("Les 100 titres les plus populaires de la sélection")
    columns = ["track_name", "artists", "track_genre", "popularity"]
    st.dataframe(seg.drop_duplicates("track_id").nlargest(100, "popularity")[columns], hide_index=True)
