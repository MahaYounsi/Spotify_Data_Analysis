# Spotify : le genre fait le hit

Dashboard Streamlit multi-pages construit sur le [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset).

**Message** : sur Spotify, c'est le genre, et non le son, qui fait la popularité d'un titre.
**Audience** : équipe A&R / marketing d'un label indépendant.

- Cadrage : [cadrage.md](cadrage.md)
- Dashboard en ligne : [spotify-genre-hit.streamlit.app](https://spotify-genre-hit.streamlit.app/)

## Structure

```
app.py               point d'entrée : navigation + filtres de la sidebar
utils.py             chargement (@st.cache_data), filtres, calculs des KPIs
pages/1_synthese.py  vue synthèse : titre-message, 3 KPIs, preuve principale
pages/2_genres.py    vue détail : comparer les genres
pages/3_son.py       vue détail : poids des variables audio
data/dataset.csv     données brutes (Kaggle)
```

## Choix des graphiques

| Graphique | Pourquoi ce choix |
|---|---|
| Barres horizontales « variance expliquée » | Comparer des grandeurs, libellés longs lisibles. **Seule la barre Genre est en couleur d'accent**, tout le reste en gris : l'œil va au message (canal pré-attentif). |
| Barres de taux de hit + ligne « catalogue » | Classement immédiat ; la couleur distingue au-dessus / en dessous de la moyenne. |
| Nuage potentiel (hits) vs risque (titres sans audience) | Deux critères de décision simultanés ; quadrants par les moyennes, libellés directs seulement sur les cibles prioritaires. |
| Boîtes à moustaches | Montrent la dispersion : même un bon genre ne garantit pas le succès. |
| Courbe par décile, axe Y fixé à 0–100 | Ne pas exagérer de petites variations : la quasi-platitude *est* le message. |
| Tableaux (onglet dédié) | Équivalent accessible de chaque graphique et accès aux valeurs exactes. |

## Préparation des données et limites

- Suppression des titres à popularité 0 (14 %) : il s'agit surtout de doublons (rééditions, compilations), Spotify n'attribuant la popularité qu'à la version principale. Suppression de 1 ligne incomplète.
- Un titre peut apparaître dans plusieurs genres : il est compté dans chacun (logique « appartenance au genre »).
- Échantillon équilibré de 1 000 titres par genre : les volumes ne reflètent pas le poids réel des genres sur Spotify.
- Il s'agit d'associations, pas de causalité : un titre pop n'est pas populaire *parce qu'il* est pop, mais l'audience y est structurellement plus forte.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```
