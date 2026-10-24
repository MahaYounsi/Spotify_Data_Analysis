"""Vue détail : mesurer ce que les caractéristiques audio changent vraiment."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import (
    ACCENT, AUDIO_FEATURES, MUTED, decile_profile, genre_table, get_segment, style_fig,
)

df, seg, filters = get_segment()

if len(seg) < 200:
    st.title("Ce que le son change à la popularité")
    st.warning("Moins de 200 titres correspondent aux filtres : élargissez la sélection.")
    st.stop()

# Amplitude de chaque levier, en points de popularité médiane :
# écart entre le meilleur et le pire décile d'une variable audio,
# comparé à l'écart entre genres (10e et 90e centiles des médianes, pour ignorer les extrêmes).
gaps = []
for col, label in AUDIO_FEATURES.items():
    prof = decile_profile(seg, col)
    gaps.append((label, prof["popularite_mediane"].max() - prof["popularite_mediane"].min()))
gaps = pd.DataFrame(gaps, columns=["levier", "ecart"])

genre_medians = genre_table(seg, filters["threshold"])["popularite_mediane"]
genre_gap = genre_medians.quantile(0.9) - genre_medians.quantile(0.1) if len(genre_medians) >= 5 else None
best_audio = gaps.loc[gaps["ecart"].idxmax()]

if genre_gap and best_audio["ecart"] > 0:
    st.title(f"Le genre pèse {genre_gap / best_audio['ecart']:.1f}× plus que le meilleur "
             "levier audio sur la popularité".replace(".", ",", 1))
else:
    st.title(f"À genre fixé, le son ne fait varier la popularité que de "
             f"{best_audio['ecart']:.0f} pts")
if genre_gap:
    st.markdown(
        f"Le levier audio le plus fort (**{best_audio['levier'].lower()}**) fait varier la "
        f"popularité médiane de **{best_audio['ecart']:.0f} pts** au maximum, "
        f"contre **{genre_gap:.0f} pts** entre genres. Les budgets de production ciblant "
        "un « son qui marche » ont un rendement limité."
    )
else:
    st.markdown(
        f"Dans la sélection, le levier audio le plus fort (**{best_audio['levier'].lower()}**) "
        f"fait varier la popularité médiane de **{best_audio['ecart']:.0f} pts** au maximum."
    )

tab_gap, tab_curve, tab_data = st.tabs(["Amplitude des leviers", "Profil par variable", "Tableau"])

with tab_gap:
    rows = gaps.copy()
    if genre_gap:
        rows = pd.concat([rows, pd.DataFrame([{"levier": "Genre (P10 → P90)", "ecart": genre_gap}])])
    rows = rows.sort_values("ecart")
    fig = go.Figure(go.Bar(
        x=rows["ecart"], y=rows["levier"], orientation="h",
        marker_color=[ACCENT if l.startswith("Genre") else MUTED for l in rows["levier"]],
        text=[f"{v:.0f} pts" for v in rows["ecart"]], textposition="outside",
        hovertemplate="%{y} : %{x:.0f} pts d'écart de popularité médiane<extra></extra>",
    ))
    fig.update_xaxes(title="Écart de popularité médiane (points)",
                     range=[0, rows["ecart"].max() * 1.15])
    st.subheader("Écart de popularité obtenu en jouant sur chaque levier")
    st.plotly_chart(style_fig(fig, 460), width="stretch")
    st.caption("Variables audio : écart entre le meilleur et le pire décile. "
               "Genre : écart entre un genre du 90e centile et un genre du 10e centile.")

with tab_curve:
    labels = {v: k for k, v in AUDIO_FEATURES.items()}
    choice = st.selectbox("Variable audio", list(labels), index=0)
    prof = decile_profile(seg, labels[choice])
    fig = go.Figure(go.Scatter(
        x=prof["decile"].astype(int), y=prof["popularite_mediane"], mode="lines+markers",
        line=dict(color=ACCENT, width=2), marker=dict(size=8),
        customdata=prof[["valeur_mediane"]],
        hovertemplate="Décile %{x} (valeur médiane %{customdata[0]:.2f})"
                      "<br>Popularité médiane : %{y:.0f}<extra></extra>",
    ))
    fig.add_hline(y=seg["popularity"].median(), line_width=1, line_color="gray",
                  annotation_text="Médiane du segment", annotation_position="bottom right")
    # Échelle 0–100 fixe : la platitude de la courbe est le message
    fig.update_yaxes(range=[0, 100], title="Popularité médiane")
    fig.update_xaxes(dtick=1, title=f"Décile de « {choice} » (1 = plus faible, 10 = plus élevé)")
    st.subheader(f"Popularité selon le niveau de « {choice} »")
    st.plotly_chart(style_fig(fig, 420), width="stretch")
    st.caption("Axe vertical fixé sur toute l'échelle de popularité (0–100) pour ne pas "
               "exagérer visuellement de petites variations.")

with tab_data:
    st.dataframe(
        gaps.sort_values("ecart", ascending=False), hide_index=True, width="stretch",
        column_config={
            "levier": "Variable audio",
            "ecart": st.column_config.NumberColumn("Écart max entre déciles (pts)", format="%.1f"),
        },
    )
