"""Vue synthèse : le message, les 3 KPIs et la preuve principale."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import (
    ACCENT, AUDIO_FEATURES, MUTED, audio_r2, genre_eta2, genre_table, get_segment,
    hit_rate, pct, pts, style_fig,
)

df, seg, filters = get_segment()
threshold = filters["threshold"]

st.title("Sur Spotify, c'est le genre, pas le son, qui fait la popularité d'un titre")
st.markdown(
    "**Pour l'équipe A&R** : avant d'optimiser la production d'un titre, "
    "choisissez le bon genre. C'est là que se joue l'essentiel de l'audience."
)

if len(seg) < 50:
    st.warning("Moins de 50 titres correspondent aux filtres : élargissez la sélection.")
    st.stop()

# --- Zone KPIs ---------------------------------------------------------------
seg_hit, cat_hit = hit_rate(seg, threshold), hit_rate(df, threshold)
seg_med, cat_med = seg["popularity"].median(), df["popularity"].median()
eta2, r2 = genre_eta2(seg), audio_r2(seg)

k1, k2, k3 = st.columns(3)
k1.metric(
    f"Taux de hit (popularité ≥ {threshold})",
    pct(seg_hit),
    pts(100 * (seg_hit - cat_hit)) + " vs catalogue",
    help=f"Part des titres du segment au-dessus du seuil. Catalogue : {pct(cat_hit)}.",
    border=True,
)
k2.metric(
    "Popularité médiane",
    f"{seg_med:.0f} / 100",
    pts(seg_med - cat_med) + " vs catalogue",
    help=f"Médiane du catalogue complet : {cat_med:.0f}.",
    border=True,
)
if pd.notna(eta2):
    k3.metric(
        "Popularité expliquée par le genre",
        pct(eta2),
        f"vs {pct(r2)} par le son (×{eta2 / r2:.0f})" if r2 > 0 else None,
        delta_color="off",
        help="Part de la variance de popularité expliquée par le genre (η²), comparée au R² "
             "des 10 variables audio réunies (régression linéaire).",
        border=True,
    )
else:
    k3.metric(
        "Popularité expliquée par le son",
        pct(r2),
        "dans ce genre (10 variables audio)",
        delta_color="off",
        help="Un seul genre sélectionné : on mesure ce que le son explique à genre fixé.",
        border=True,
    )

# --- Zone détail -------------------------------------------------------------
tab_proof, tab_hits, tab_data = st.tabs(["Genre vs son", "Où sont les hits", "Données"])

with tab_proof:
    rows = [("Genre", eta2), ("Les 10 variables audio réunies", r2)]
    rows += [(label, audio_r2(seg, [col])) for col, label in AUDIO_FEATURES.items()]
    proof = pd.DataFrame(rows, columns=["facteur", "r2"]).dropna().sort_values("r2")
    colors = [ACCENT if f == "Genre" else MUTED for f in proof["facteur"]]

    st.subheader("Le genre explique bien plus de popularité que n'importe quel réglage du son")
    fig = go.Figure(go.Bar(
        x=proof["r2"], y=proof["facteur"], orientation="h", marker_color=colors,
        text=[pct(v) for v in proof["r2"]], textposition="outside",
        hovertemplate="%{y} : %{x:.1%} de la variance expliquée<extra></extra>",
    ))
    fig.update_xaxes(tickformat=".0%", title="Part de la variance de popularité expliquée",
                     range=[0, max(proof["r2"].max() * 1.15, 0.05)])
    st.plotly_chart(style_fig(fig, 460), width="stretch")
    st.caption(
        "Lecture : connaître le genre d'un titre permet de prédire une bien plus grande part "
        "de sa popularité que connaître toutes ses caractéristiques audio. "
        "Sélectionnez un seul genre pour voir ce que le son explique à genre fixé."
    )

with tab_hits:
    table = genre_table(seg, threshold).sort_values("taux_hit", ascending=False).head(15)
    table = table.sort_values("taux_hit")
    colors = [ACCENT if v > cat_hit else MUTED for v in table["taux_hit"]]

    st.subheader(f"Les genres qui produisent le plus de hits (popularité ≥ {threshold})")
    fig = go.Figure(go.Bar(
        x=table["taux_hit"], y=table["genre"], orientation="h", marker_color=colors,
        customdata=table[["titres"]],
        hovertemplate="%{y} : %{x:.1%} de hits<br>%{customdata[0]} titres<extra></extra>",
    ))
    fig.add_vline(x=cat_hit, line_width=1, line_color="gray",
                  annotation_text=f"Catalogue : {pct(cat_hit)}", annotation_position="top")
    fig.update_xaxes(tickformat=".0%", title="Taux de hit")
    st.plotly_chart(style_fig(fig, 480), width="stretch")
    st.caption("En bleu : genres au-dessus du taux de hit moyen du catalogue. "
               "Top 15 de la sélection courante.")

with tab_data:
    st.subheader("Titres les plus populaires du segment")
    top = (seg.sort_values("popularity", ascending=False)
              .drop_duplicates("track_id")
              .head(100)[["track_name", "artists", "track_genre", "popularity", "explicit"]])
    st.dataframe(
        top, hide_index=True, width="stretch",
        column_config={
            "track_name": "Titre", "artists": "Artiste(s)", "track_genre": "Genre",
            "popularity": st.column_config.ProgressColumn(
                "Popularité", min_value=0, max_value=100, format="%d"),
            "explicit": "Explicite",
        },
    )
