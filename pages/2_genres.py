"""Vue détail : comparer les genres pour décider où signer."""
import plotly.graph_objects as go
import streamlit as st

from utils import (
    ACCENT, FLOP_THRESHOLD, MUTED, genre_table, get_segment, hit_rate, pct, style_fig,
)

df, seg, filters = get_segment()
threshold = filters["threshold"]

if seg["track_genre"].nunique() < 2:
    st.title("Comparer les genres")
    st.info("Sélectionnez au moins deux genres (ou aucun pour tout le catalogue).")
    st.stop()

table = genre_table(seg, threshold)
cat_hit = hit_rate(df, threshold)
cat_flop = (df["popularity"] < FLOP_THRESHOLD).mean()

# Concentration des hits : part des hits produite par le premier dixième des genres
ranked = table.assign(hits=table["titres"] * table["taux_hit"]).sort_values("taux_hit", ascending=False)
n_top = max(1, round(len(ranked) / 10))
top_share = ranked["hits"].head(n_top).sum() / max(ranked["hits"].sum(), 1)

st.title(f"{n_top} genre{'s' if n_top > 1 else ''} sur {len(ranked)} "
         f"produi{'sent' if n_top > 1 else 't'} "
         f"{pct(top_share)} des hits")
st.markdown("Les hits ne sont pas répartis au hasard : le choix du genre d'une signature "
            "fixe à la fois son **potentiel** (taux de hit) et son **risque** (titres sans audience).")

tab_rank, tab_risk, tab_dist, tab_data = st.tabs(
    ["Taux de hit par genre", "Potentiel vs risque", "Distribution", "Tableau"]
)

with tab_rank:
    t = table.sort_values("taux_hit")
    fig = go.Figure(go.Bar(
        x=t["taux_hit"], y=t["genre"], orientation="h",
        marker_color=[ACCENT if v > cat_hit else MUTED for v in t["taux_hit"]],
        customdata=t[["titres", "popularite_mediane"]],
        hovertemplate="%{y}<br>%{x:.1%} de hits<br>Popularité médiane : %{customdata[1]:.0f}"
                      "<br>%{customdata[0]} titres<extra></extra>",
    ))
    fig.add_vline(x=cat_hit, line_width=1, line_color="gray",
                  annotation_text=f"Catalogue : {pct(cat_hit)}", annotation_position="top")
    fig.update_xaxes(tickformat=".0%", title=f"Part des titres avec popularité ≥ {threshold}")
    st.plotly_chart(style_fig(fig, max(360, 18 * len(t))), width="stretch")
    st.caption("En bleu : genres au-dessus de la moyenne du catalogue.")

with tab_risk:
    good = (table["taux_hit"] > cat_hit) & (table["taux_flop"] < cat_flop)
    fig = go.Figure(go.Scatter(
        x=table["taux_flop"], y=table["taux_hit"], mode="markers",
        marker=dict(size=10, color=[ACCENT if g else MUTED for g in good],
                    opacity=0.85),
        text=table["genre"],
        hovertemplate="%{text}<br>Hits : %{y:.1%}<br>Sans audience : %{x:.1%}<extra></extra>",
    ))
    # Libellés directs uniquement sur les meilleurs genres
    best = table[good].nlargest(8, "taux_hit")
    fig.add_trace(go.Scatter(
        x=best["taux_flop"], y=best["taux_hit"], mode="text", text=best["genre"],
        textposition="middle right", hoverinfo="skip",
    ))
    fig.add_hline(y=cat_hit, line_width=1, line_color="gray")
    fig.add_vline(x=cat_flop, line_width=1, line_color="gray")
    fig.update_xaxes(tickformat=".0%", title=f"Risque : part de titres sans audience (popularité < {FLOP_THRESHOLD})")
    fig.update_yaxes(tickformat=".0%", title=f"Potentiel : taux de hit (≥ {threshold})")
    st.subheader("Les genres en haut à gauche combinent fort potentiel et faible risque")
    st.plotly_chart(style_fig(fig, 520), width="stretch")
    st.caption("Lignes grises : moyennes du catalogue. En bleu : genres meilleurs que la "
               "moyenne sur les deux axes, cibles prioritaires de signature.")

with tab_dist:
    n_show = st.slider("Nombre de genres affichés (classés par popularité médiane)", 5, 30, 12)
    order = table.nlargest(n_show, "popularite_mediane")["genre"].tolist()
    sub = seg[seg["track_genre"].isin(order)]
    fig = go.Figure()
    for g in reversed(order):
        fig.add_trace(go.Box(
            x=sub.loc[sub["track_genre"] == g, "popularity"], name=g, orientation="h",
            marker_color=ACCENT, line_width=1.5, boxpoints=False,
        ))
    fig.add_vline(x=threshold, line_width=1, line_color="gray",
                  annotation_text=f"Seuil de hit ({threshold})", annotation_position="top")
    fig.update_xaxes(range=[0, 100], title="Popularité")
    st.subheader("Même dans les meilleurs genres, la popularité reste très dispersée")
    st.plotly_chart(style_fig(fig, max(360, 34 * n_show)), width="stretch")

with tab_data:
    st.dataframe(
        table.sort_values("taux_hit", ascending=False), hide_index=True, width="stretch",
        column_config={
            "genre": "Genre",
            "titres": "Titres",
            "popularite_mediane": st.column_config.NumberColumn("Popularité médiane", format="%.0f"),
            "taux_hit": st.column_config.ProgressColumn(
                f"Taux de hit (≥ {threshold})", min_value=0, max_value=1, format="percent"),
            "taux_flop": st.column_config.ProgressColumn(
                f"Sans audience (< {FLOP_THRESHOLD})", min_value=0, max_value=1, format="percent"),
        },
    )
