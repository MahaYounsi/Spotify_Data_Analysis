"""Vue détail : comparer les genres pour décider où signer."""
import plotly.express as px
import streamlit as st

HIT = 65   # popularité minimale d'un « hit »
FLOP = 20  # en dessous : titre sans audience
COLORS = {True: "#2a78d6", False: "#b4b3ad"}  # bleu = ce qui porte le message, gris = le reste

df = st.session_state["df"]
seg = st.session_state["seg"]

st.title("Les hits se concentrent dans une poignée de genres")
st.write("Le genre d'une signature fixe à la fois son **potentiel** (taux de hit) "
         "et son **risque** (titres sans audience).")

# Une ligne par genre : nombre de titres, popularité médiane, taux de hit et de flop
stats = (
    seg.groupby("track_genre")["popularity"]
    .agg(titres="size", popularite_mediane="median",
         taux_hit=lambda s: (s >= HIT).mean(), taux_flop=lambda s: (s < FLOP).mean())
    .reset_index()
)
avg_hit = (df["popularity"] >= HIT).mean()
avg_flop = (df["popularity"] < FLOP).mean()

tab1, tab2, tab3 = st.tabs(["Taux de hit par genre", "Potentiel vs risque", "Tableau"])

with tab1:
    ranked = stats.sort_values("taux_hit")
    ranked["couleur"] = ranked["taux_hit"] > avg_hit
    fig = px.bar(ranked, x="taux_hit", y="track_genre", orientation="h",
                 color="couleur", color_discrete_map=COLORS,
                 labels={"taux_hit": f"Part des titres avec popularité ≥ {HIT}", "track_genre": ""},
                 height=max(400, 18 * len(ranked)))
    fig.add_vline(x=avg_hit, line_color="gray", annotation_text="Moyenne du catalogue")
    fig.update_layout(showlegend=False, xaxis_tickformat=".0%")
    st.plotly_chart(fig)
    st.caption("En bleu : genres au-dessus de la moyenne du catalogue.")

with tab2:
    st.subheader("Cibles prioritaires : beaucoup de hits, peu de titres sans audience")
    stats["cible"] = (stats["taux_hit"] > avg_hit) & (stats["taux_flop"] < avg_flop)
    fig = px.scatter(stats, x="taux_flop", y="taux_hit", hover_name="track_genre",
                     color="cible", color_discrete_map=COLORS,
                     labels={"taux_flop": f"Risque : part de titres à popularité < {FLOP}",
                             "taux_hit": f"Potentiel : taux de hit (≥ {HIT})"},
                     height=520)
    fig.add_hline(y=avg_hit, line_color="gray")
    fig.add_vline(x=avg_flop, line_color="gray")
    fig.update_layout(showlegend=False, xaxis_tickformat=".0%", yaxis_tickformat=".0%")
    st.plotly_chart(fig)
    st.caption("Lignes grises : moyennes du catalogue. En bleu : genres meilleurs que la moyenne "
               "sur les deux axes. Survolez un point pour voir le genre.")

with tab3:
    st.dataframe(stats.drop(columns="cible").sort_values("taux_hit", ascending=False), hide_index=True)
