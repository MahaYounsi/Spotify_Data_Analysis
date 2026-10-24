"""Vue synthèse : le message, les 3 KPIs et la preuve principale."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import ACCENT, AUDIO_FEATURES, GREY, HIT, audio_r2, filter_data, genre_r2, genre_stats, hit_rate, load_data

df = load_data()
seg = filter_data(df)

st.title("Sur Spotify, c'est le genre, pas le son, qui fait la popularité d'un titre")
st.write("**Pour l'équipe A&R** : avant d'optimiser la production d'un titre, choisissez le bon genre.")

if len(seg) < 100:
    st.warning("Trop peu de titres pour ces filtres : élargissez la sélection.")
    st.stop()

# --- Zone KPIs : chaque indicateur est comparé au catalogue complet ---
col1, col2, col3 = st.columns(3)
col1.metric(f"Taux de hit (popularité ≥ {HIT})", f"{hit_rate(seg):.0%}",
            f"{100 * (hit_rate(seg) - hit_rate(df)):+.1f} pts vs catalogue", border=True)
col2.metric("Popularité médiane", f"{seg['popularity'].median():.0f} / 100",
            f"{seg['popularity'].median() - df['popularity'].median():+.0f} pts vs catalogue", border=True)
col3.metric("Popularité expliquée par le genre", f"{genre_r2(seg):.0%}",
            f"vs {audio_r2(seg):.0%} par le son", delta_color="off", border=True)

# --- Zone détail ---
tab1, tab2, tab3 = st.tabs(["Genre vs son", "Où sont les hits", "Données"])

with tab1:
    st.subheader("Le genre explique plus de popularité que n'importe quelle variable audio")
    rows = [("Genre", genre_r2(seg)), ("Les 10 variables audio réunies", audio_r2(seg))]
    rows += [(label, audio_r2(seg, [col])) for col, label in AUDIO_FEATURES.items()]
    proof = pd.DataFrame(rows, columns=["facteur", "r2"]).sort_values("r2")
    proof["couleur"] = proof["facteur"].eq("Genre")
    fig = px.bar(proof, x="r2", y="facteur", orientation="h", text_auto=".0%",
                 color="couleur", color_discrete_map={True: ACCENT, False: GREY},
                 labels={"r2": "Part de la variance de popularité expliquée", "facteur": ""})
    fig.update_layout(showlegend=False, xaxis_tickformat=".0%")
    st.plotly_chart(fig)

with tab2:
    st.subheader(f"Les 15 genres qui produisent le plus de hits (popularité ≥ {HIT})")
    top = genre_stats(seg).nlargest(15, "taux_hit").sort_values("taux_hit")
    top["couleur"] = top["taux_hit"] > hit_rate(df)
    fig = px.bar(top, x="taux_hit", y="track_genre", orientation="h",
                 color="couleur", color_discrete_map={True: ACCENT, False: GREY},
                 labels={"taux_hit": "Taux de hit", "track_genre": ""})
    fig.add_vline(x=hit_rate(df), line_color="gray", annotation_text="Moyenne du catalogue")
    fig.update_layout(showlegend=False, xaxis_tickformat=".0%")
    st.plotly_chart(fig)
    st.caption("En bleu : genres au-dessus de la moyenne du catalogue.")

with tab3:
    st.subheader("Les 100 titres les plus populaires de la sélection")
    columns = ["track_name", "artists", "track_genre", "popularity"]
    st.dataframe(seg.drop_duplicates("track_id").nlargest(100, "popularity")[columns], hide_index=True)
