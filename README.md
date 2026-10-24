# Spotify : le genre fait le hit

Dashboard Streamlit multi-pages construit sur le [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset).

**Message** : sur Spotify, c'est le genre, et non le son, qui fait la popularité d'un titre.
**Audience** : équipe A&R / marketing d'un label indépendant.

- Cadrage : [cadrage.md](cadrage.md)
- Dashboard en ligne : `https://<à-compléter>.streamlit.app`

## Structure

```
app.py               point d'entrée : navigation + filtres de la sidebar
utils.py             chargement (@st.cache_data), filtres, calculs des KPIs
pages/1_synthese.py  vue synthèse : titre-message, 3 KPIs, preuve principale
pages/2_genres.py    vue détail : comparer les genres
pages/3_son.py       vue détail : poids des variables audio
data/dataset.csv     données brutes (Kaggle)
```

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```
