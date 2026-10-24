# Document de cadrage : dashboard « Spotify : le genre fait le hit »

**Dataset** : [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) (Kaggle) : 114 000 titres, 114 genres × 1 000 titres, popularité 0–100 et 10 variables audio.
**Déploiement** : [spotify-genre-hit.streamlit.app](https://spotify-genre-hit.streamlit.app/)

## 1. Message clé (sommet de la pyramide de Minto)

> **Sur Spotify, c'est le genre, et non le son, qui fait la popularité d'un titre : le genre en explique 38 %, les 10 caractéristiques audio réunies seulement 6 %.**

| Argument (niveau 2) | Preuve (niveau 3) | Où dans le dashboard |
|---|---|---|
| Le genre explique la popularité bien mieux que le son | η² genre = 38 % vs R² audio = 6 %. Une fois le genre connu, l'audio n'ajoute que +0,5 pt | Synthèse › *Genre vs son* |
| Les hits sont concentrés dans peu de genres | 11 genres sur 114 produisent 37 % des hits ; 13 genres n'en produisent aucun | Détail genres |
| Optimiser le son a un rendement limité | Meilleur levier audio : 16 pts de popularité médiane, contre 39 pts entre genres | Détail son |

## 2. Audience cible

**Équipe A&R / marketing d'un label indépendant.** Elle décide *quels artistes signer* et *où placer le budget* (production vs promotion). Elle n'est pas data scientist : elle a besoin d'une réponse en 5 secondes (titre + KPIs), puis de la possibilité de creuser son segment (filtres).

## 3. KPIs retenus (3 maximum, toujours contextualisés)

Le dataset n'a pas de dimension temporelle (popularité relevée à une date unique) : le contexte se fait donc par **comparaison au catalogue complet** plutôt que par tendance.

| KPI | Contexte affiché | Pourquoi il est *actionable* |
|---|---|---|
| **Taux de hit** : % de titres avec popularité ≥ 65 (top 10 %) | écart en points vs catalogue (9,7 %) | Mesure directement la probabilité de succès d'une signature dans le segment : on signe là où il est le plus élevé. |
| **Popularité médiane** | écart vs médiane catalogue (39) | Donne l'attente réaliste pour un titre *typique*, sans être tirée par quelques tubes : sert à calibrer le budget de lancement. |
| **Part de popularité expliquée par le genre** (η²) | comparée au R² des variables audio (« ×6 ») | Arbitre le budget : si le genre pèse 6× plus que le son, l'effort doit porter sur le choix du répertoire, pas sur le « son qui marche ». |

**Écartés car *vanity metrics*** : nombre de titres ou d'artistes (volume, n'aide à aucune décision) ; popularité maximale / titre n°1 (exception non reproductible) ; moyennes de tempo ou de dansabilité (descriptives, sans lien avec le résultat) ; popularité moyenne (déformée par les extrêmes, remplacée par la médiane).

## 4. Structure prévue

- **Sidebar (filtres partagés par toutes les pages)** : genres (multi-sélection), paroles explicites, durée du titre, seuil de « hit » (paramètre avancé).
- **Page Synthèse** : titre-message → **zone KPIs** (3 colonnes) → **zone détail** en onglets : *Genre vs son*, *Où sont les hits*, *Données*.
- **Page Détail : genres** : titre dynamique (concentration des hits) → onglets *Taux de hit par genre*, *Potentiel vs risque*, *Distribution*, *Tableau*.
- **Page Détail : le son** : titre dynamique (rapport genre / meilleur levier audio) → onglets *Amplitude des leviers*, *Profil par variable*, *Tableau*.

## 5. Choix des graphiques

| Graphique | Pourquoi ce choix |
|---|---|
| Barres horizontales « variance expliquée » | Comparer des grandeurs, libellés longs lisibles. **Seule la barre Genre est en couleur d'accent**, tout le reste en gris : l'œil va au message (canal pré-attentif). |
| Barres de taux de hit + ligne « catalogue » | Classement immédiat ; la couleur distingue au-dessus / en dessous de la moyenne. |
| Nuage potentiel (hits) vs risque (titres sans audience) | Deux critères de décision simultanés ; quadrants par les moyennes, libellés directs seulement sur les cibles prioritaires. |
| Boîtes à moustaches | Montrent la dispersion : même un bon genre ne garantit pas le succès. |
| Courbe par décile, axe Y fixé à 0–100 | Ne pas exagérer de petites variations : la quasi-platitude *est* le message. |
| Tableaux (onglet dédié) | Équivalent accessible de chaque graphique et accès aux valeurs exactes. |

## 6. Préparation des données et limites

- Suppression des titres à popularité 0 (14 %) : il s'agit surtout de doublons (rééditions, compilations), Spotify n'attribuant la popularité qu'à la version principale. Suppression de 1 ligne incomplète.
- Un titre peut apparaître dans plusieurs genres : il est compté dans chacun (logique « appartenance au genre »).
- Échantillon équilibré de 1 000 titres par genre : les volumes ne reflètent pas le poids réel des genres sur Spotify.
- Il s'agit d'associations, pas de causalité : un titre pop n'est pas populaire *parce qu'il* est pop, mais l'audience y est structurellement plus forte.
