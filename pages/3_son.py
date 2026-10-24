"""Vue détail : ce que les variables audio changent vraiment à la popularité."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import ACCENT, AUDIO_FEATURES, GREY, filter_data, genre_stats, load_data

df = load_data()
seg = filter_data(df)

st.title("Le son pèse beaucoup moins que le genre sur la popularité")
st.write("Les budgets de production qui visent un « son qui marche » ont un rendement limité.")

if len(seg) < 100:
    st.warning("Trop peu de titres pour ces filtres : élargissez la sélection.")
    st.stop()


def by_decile(feature):
    """Popularité médiane pour chaque dixième des titres, du plus faible au plus élevé sur la variable."""
    decile = pd.qcut(seg[feature].rank(method="first"), 10, labels=range(1, 11))
    return seg.groupby(decile)["popularity"].median()


tab1, tab2 = st.tabs(["Amplitude des leviers", "Profil par variable"])

with tab1:
    st.subheader("Écart de popularité médiane obtenu en jouant sur chaque levier")
    # Variable audio : écart entre le meilleur et le pire décile.
    # Genre : écart entre un genre du 90e centile et un du 10e (on ignore les extrêmes).
    gaps = {label: by_decile(col).max() - by_decile(col).min() for col, label in AUDIO_FEATURES.items()}
    medians = genre_stats(seg)["popularite_mediane"]
    gaps["Genre"] = medians.quantile(0.9) - medians.quantile(0.1)

    levers = pd.DataFrame(gaps.items(), columns=["levier", "ecart"]).sort_values("ecart")
    levers["couleur"] = levers["levier"].eq("Genre")
    fig = px.bar(levers, x="ecart", y="levier", orientation="h", text_auto=".0f",
                 color="couleur", color_discrete_map={True: ACCENT, False: GREY},
                 labels={"ecart": "Écart de popularité médiane (points)", "levier": ""})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)
    st.caption("Sélectionnez au moins 5 genres pour que la barre « Genre » soit significative.")

with tab2:
    label = st.selectbox("Variable audio", list(AUDIO_FEATURES.values()))
    feature = next(col for col, name in AUDIO_FEATURES.items() if name == label)
    profile = by_decile(feature).reset_index()
    profile.columns = ["decile", "popularite_mediane"]
    fig = px.line(profile, x="decile", y="popularite_mediane", markers=True,
                  color_discrete_sequence=[ACCENT],
                  labels={"decile": f"Décile de « {label} » (1 = plus faible, 10 = plus élevé)",
                          "popularite_mediane": "Popularité médiane"})
    # Axe fixé de 0 à 100 pour ne pas exagérer de petites variations
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(fig)
