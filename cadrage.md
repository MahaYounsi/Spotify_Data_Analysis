# Cadrage : « Spotify : le genre fait le hit »

**Données** : [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) (Kaggle), 114 genres × 1 000 titres, titres à popularité 0 exclus (doublons). **Dashboard** : [spotify-genre-hit.streamlit.app](https://spotify-genre-hit.streamlit.app/)

## 1. Message clé

> **Sur Spotify, c'est le genre, et non le son, qui fait la popularité d'un titre : le genre en explique 38 %, les 10 caractéristiques audio réunies seulement 6 %.**

Arguments (pyramide de Minto) : ① le genre explique 6× plus que le son, et l'audio n'ajoute que +0,5 pt une fois le genre connu ; ② 11 genres sur 114 produisent 37 % des hits ; ③ prise seule, aucune variable audio n'explique plus de 4 % de la popularité.

## 2. Audience cible

**Équipe A&R / marketing d'un label indépendant**, qui décide quels artistes signer et où placer le budget (production ou promotion). Non spécialiste : réponse en 5 secondes (titre + KPIs), puis exploration de son segment par les filtres.

## 3. KPIs retenus

Pas de dimension temporelle dans le dataset : chaque KPI est contextualisé par **comparaison au catalogue complet**.

| KPI | Contexte | Pourquoi il est *actionable* |
|---|---|---|
| **Taux de hit** (% de titres à popularité ≥ 65, top 10 %) | écart vs catalogue (9,7 %) | Probabilité de succès d'une signature dans le segment : on signe là où il est élevé. |
| **Popularité médiane** | écart vs catalogue (39) | Attente réaliste pour un titre typique, non faussée par quelques tubes : calibre le budget de lancement. |
| **Part de popularité expliquée par le genre** (η²) | vs R² des variables audio (« ×6 ») | Arbitre le budget : l'effort doit porter sur le choix du répertoire plutôt que sur un « son qui marche ». |

**Écartés (*vanity*)** : nombre de titres ou d'artistes (volume sans décision associée), popularité maximale (exception non reproductible), moyennes de tempo ou de dansabilité (descriptives, sans lien avec le résultat).

## 4. Structure

- **Filtres (sidebar, partagés par toutes les pages)** : genres, paroles explicites.
- **Synthèse** : titre-message → **zone KPIs** (3 colonnes) → **zone détail** en onglets (*Genre vs son*, *Données*).
- **Détail : genres** : onglets *Taux de hit par genre*, *Potentiel vs risque*, *Tableau*.
