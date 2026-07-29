# 📊 AfriMarket — Analyse Stratégique des Données

Analyse de données de bout en bout pour **AfriMarket**, une plateforme e-commerce panafricaine, réalisée dans le cadre d'une mission de Data Analyst : audit et nettoyage d'un jeu de données réel (doublons, erreurs de saisie, valeurs aberrantes), feature engineering, analyses business (performance globale, catégories, villes, marketing, clients), visualisations, dashboard interactif et livrables de reporting (résumé exécutif, présentation direction).

## Sommaire

- [Contexte](#contexte)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Pipeline de données](#pipeline-de-données)
- [Dashboard Streamlit](#dashboard-streamlit)
- [Notebook d'analyse](#notebook-danalyse)
- [Livrables](#livrables)
- [Insights clés & recommandations](#insights-clés--recommandations)

## Contexte

AfriMarket est une entreprise e-commerce présente dans plusieurs villes africaines francophones, avec 4 catégories de produits (Électronique, Mode, Beauté, Maison). La direction a identifié plusieurs signaux à investiguer :

- de fortes variations du chiffre d'affaires d'un mois à l'autre,
- un taux de retour préoccupant sur certains produits,
- des dépenses marketing élevées sans visibilité claire sur leur rentabilité,
- des écarts de performance importants entre les villes.

La mission consiste à exploiter le jeu de données brut de 6 mois d'activité (`data/afrimarket_dataset_senior.csv`, volontairement bruité : doublons, erreurs de saisie, valeurs aberrantes) pour produire :

1. un notebook d'analyse propre, structuré et commenté,
2. un résumé exécutif (4-5 pages) pour la direction,
3. un dashboard interactif,
4. 5 recommandations stratégiques,
5. une conclusion business orientée action.

Le brief complet de la mission est disponible dans `Python - Analyse AfriMarket.docx`.

## Structure du projet

```
.
├── assets/                     Logo et éléments graphiques de marque
├── dashboard/
│   └── app.py                  Dashboard interactif Streamlit
├── data/
│   ├── afrimarket_dataset_senior.csv   Jeu de données brut (source)
│   ├── df_clean.csv                    Données nettoyées
│   └── df_features.csv                 Données enrichies (features métier)
├── figures/                     Graphiques générés (PNG + HTML interactifs Plotly)
│   └── brand/                  Version des graphiques aux couleurs AfriMarket (pour les rapports)
├── notebook/
│   └── AfriMarket_Analyse.ipynb   Notebook d'analyse complet (7 sections)
├── reports/
│   ├── Resume_Executif_AfriMarket.docx / .pdf   Résumé exécutif
│   └── AfriMarket_Presentation_Direction.pptx   Présentation direction (13 slides)
├── scripts/                     Pipeline complet : audit → nettoyage → features → analyses → visualisations → rapports
├── Python - Analyse AfriMarket.docx   Brief / cahier des charges de la mission
└── requirements.txt
```

## Installation

Prérequis : Python 3.10+.

```bash
pip install -r requirements.txt
```

`requirements.txt` couvre les dépendances du dashboard (Streamlit, pandas, numpy, plotly). Pour rejouer l'intégralité du pipeline (scripts d'analyse, notebook, génération des rapports Word/PowerPoint), installez en plus :

```bash
pip install matplotlib seaborn python-docx python-pptx Pillow nbformat
```

## Utilisation

Le jeu de données nettoyé et enrichi (`data/df_features.csv`) est déjà fourni : vous pouvez directement explorer le notebook ou lancer le dashboard sans rejouer le pipeline.

**Explorer l'analyse complète :**
```bash
jupyter notebook notebook/AfriMarket_Analyse.ipynb
```

**Lancer le dashboard interactif :**
```bash
streamlit run dashboard/app.py
```
Accessible ensuite sur [http://localhost:8501](http://localhost:8501).

**Consulter les livrables de synthèse :** voir le dossier [`reports/`](reports/).

## Pipeline de données

Les scripts du dossier `scripts/` reproduisent, étape par étape, l'ensemble du pipeline d'analyse. Ce sont des scripts autonomes (pas d'arguments en ligne de commande) à exécuter dans l'ordre suivant :

| # | Script | Rôle | Entrée → Sortie |
|---|--------|------|------------------|
| 1 | `01_audit.py` | Audit qualité des données brutes (types, valeurs manquantes, doublons, incohérences) | `afrimarket_dataset_senior.csv` → rapport console |
| 2 | `02_cleaning.py` | Nettoyage : dédoublonnage, correction des villes/catégories/statuts, remises négatives, prix invalides, quantités nulles | → `data/df_clean.csv` |
| 3 | `03_features.py` | Feature engineering : CA, marge, profit net estimé, indicateurs de retour/annulation, valeur vie client | → `data/df_features.csv` |
| 4 | `04_analysis_performance.py` | Performance globale (CA, profit, panier moyen, taux d'annulation/retour) | rapport console |
| 5 | `05_analysis_categorie_ville_marketing_clients.py` | Analyses par catégorie, ville, canal marketing et clients (Pareto, segmentation) | rapport console |
| 6 | `06_visualisations_matplotlib.py` | 12 graphiques Matplotlib | → `figures/*.png` |
| 7 | `07_visualisations_seaborn_plotly.py` | Heatmap de corrélation, boxplot (Seaborn) + graphiques interactifs (Plotly) | → `figures/*.png` et `.html` |
| 8 | `08_visualisations_brand.py` | Version aux couleurs de marque AfriMarket des graphiques clés | → `figures/brand/*.png` |
| — | `build_notebook.py` | Génère `notebook/AfriMarket_Analyse.ipynb` | |
| — | `build_executive_summary.py` | Génère le résumé exécutif Word | → `reports/Resume_Executif_AfriMarket.docx` |
| — | `build_pptx.py` | Génère la présentation direction PowerPoint | → `reports/AfriMarket_Presentation_Direction.pptx` |

> ⚠️ Les scripts `01` à `08` utilisent des chemins absolus codés en dur (`c:\Users\...\PROJET PYTHON\...`). Adaptez ces chemins si vous déplacez le projet.

### Problèmes de qualité corrigés lors du nettoyage

| Problème | Volume | Correction appliquée |
|---|---|---|
| Doublons exacts | 100 lignes | Suppression |
| Ville mal orthographiée ("Kinshassa") | 605 lignes | Renommée en "Kinshasa" |
| Catégorie incohérente ("electronique") | 606 lignes | Normalisée en "Électronique" |
| Casse incohérente des statuts | — | Uniformisée |
| Remises négatives | 600 lignes | Valeur absolue + plafonnées à 30% |
| Prix unitaire invalide (≤ 0) | 622 lignes | Imputé par la médiane de la catégorie |
| Quantité nulle | 600 lignes | Lignes supprimées |

## Dashboard Streamlit

`dashboard/app.py` propose une exploration interactive des données filtrable par période, ville, catégorie, canal marketing et statut de commande, organisée en 6 onglets :

1. **Vue d'ensemble** — KPIs globaux, évolution mensuelle du CA, répartition par catégorie/ville
2. **Catégories** — performance et rentabilité par catégorie
3. **Géographie** — performance par ville, heatmap CA par ville/mois
4. **Marketing** — ROI et rétention par canal
5. **Clients** — analyse Pareto 80/20, segmentation, top 10 clients
6. **Recommandations** — synthèse des 5 recommandations stratégiques

Un export CSV des données filtrées est disponible en bas de page.

## Notebook d'analyse

`notebook/AfriMarket_Analyse.ipynb` (généré par `scripts/build_notebook.py`) suit la structure demandée par le brief :

1. Audit & compréhension des données
2. Data cleaning
3. Feature engineering
4. Analyses demandées (4.1 performance globale, 4.2 catégories, 4.3 géographie, 4.4 marketing, 4.5 clients)
5. Synthèse des insights clés
6. Recommandations stratégiques
7. Conclusion business orientée action

## Livrables

- **`reports/Resume_Executif_AfriMarket.docx` / `.pdf`** — résumé exécutif de 4 pages destiné à la direction
- **`reports/AfriMarket_Presentation_Direction.pptx`** — présentation de 13 slides (contexte, méthodologie, résultats par axe, recommandations, conclusion)
- **`figures/`** — l'ensemble des graphiques générés, dont deux visualisations interactives Plotly (`15_plotly_evolution_ville.html`, `16_plotly_treemap_ca.html`)

## Insights clés & recommandations

- **Électronique** génère 74,6% du CA mais affiche la marge la plus faible (15%) et le taux de retour le plus élevé (13,8%) → catégorie à optimiser en priorité.
- **Mode et Beauté** ont de fortes marges (45-50%) et peu de retours, mais ne représentent qu'environ 10% du CA → axes de croissance à développer.
- **Douala** connaît la plus forte croissance (+76%) mais aussi le taux d'annulation le plus élevé (12,9%) → problème opérationnel à résoudre avant d'investir davantage.
- **Email** offre le meilleur ROI marketing (231x) pour un budget minime → canal sous-exploité à renforcer, contrairement à **Influenceur** (ROI le plus faible, rétention la plus basse).
- **32% des clients génèrent 80% du CA** (loi de Pareto) ; 26% des clients sont des acheteurs uniques → levier de rétention prioritaire via une campagne de réactivation.

Les 5 recommandations stratégiques détaillées sont disponibles dans le notebook, le résumé exécutif et le dashboard (onglet *Recommandations*).
