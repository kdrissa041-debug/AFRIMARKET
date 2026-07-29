# -*- coding: utf-8 -*-
"""Construit le notebook final AfriMarket_Analyse.ipynb via nbformat."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))

# =========================================================================
# 0. TITRE / CONTEXTE
# =========================================================================
md("""\
# Analyse strategique des donnees — AfriMarket

**Data Analyst :** Projet d'analyse e-commerce
**Periode couverte :** Juillet 2025 - Decembre 2025 (6 mois)
**Objectif :** Produire une analyse strategique complete permettant a la direction d'AfriMarket
de prendre des decisions business sur la performance commerciale, les categories de produits,
la geographie, le marketing et les clients.

---

### Sommaire
1. [Audit & Comprehension des donnees](#1)
2. [Data Cleaning](#2)
3. [Feature Engineering](#3)
4. [Analyses](#4)
   - 4.1 Performance globale
   - 4.2 Analyse par categorie
   - 4.3 Analyse geographique
   - 4.4 Analyse marketing
   - 4.5 Analyse clients
5. [Synthese des insights cles](#5)
6. [Recommandations strategiques](#6)
7. [Conclusion business](#7)
""")

code("""\
# Imports et configuration generale
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px

%matplotlib inline
sns.set_style("whitegrid")
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 160)

PALETTE = ["#2C5F8A", "#E07A3E", "#4C9F70", "#C44E52", "#8172B2", "#937860", "#DA8BC3", "#8C8C8C"]
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "axes.edgecolor": "#333333",
    "axes.grid": True, "grid.color": "#e0e0e0", "grid.linewidth": 0.6,
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
})

def money_fmt(x, pos):
    return f"{x/1000:.0f}k"

RAW_PATH = "../data/afrimarket_dataset_senior.csv"
FIG_DIR = "../figures"
""")

# =========================================================================
# 1. AUDIT
# =========================================================================
md("""\
<a id="1"></a>
## 1. Audit & Comprehension des donnees

Avant toute analyse, on commence par un audit systematique du dataset brut : structure,
types, valeurs manquantes, doublons et valeurs aberrantes. Cet audit conditionne toutes
les decisions de nettoyage prises a l'etape suivante.
""")

code("""\
df_raw = pd.read_csv(RAW_PATH, encoding="utf-8")
print("Dimensions :", df_raw.shape)
df_raw.head()
""")

code("""\
print("=== Types de donnees ===")
print(df_raw.dtypes)
""")

code("""\
print("=== Valeurs manquantes ===")
print(df_raw.isna().sum())
""")

md("""\
**Constat :** aucune valeur manquante explicite (NaN) n'est presente. En revanche, le dataset
contient des valeurs *invalides* qui jouent le meme role (prix negatifs, quantites nulles),
ce qui est plus insidieux qu'un NaN classique car cela ne remonte pas dans `isna()`.
""")

code("""\
print("=== Doublons ===")
print("Lignes dupliquees (toutes colonnes identiques) :", df_raw.duplicated().sum())
print("id_commande dupliques :", df_raw.duplicated(subset=['id_commande']).sum())
""")

code("""\
print("=== Incoherences categorielles ===")
for col in ["ville", "categorie", "statut_commande"]:
    print(f"\\n--- {col} ---")
    print(df_raw[col].value_counts())
""")

md("""\
**Problemes de qualite detectes :**
- `ville` : *Kinshassa* est une faute d'orthographe de *Kinshasa* (605 lignes concernees).
- `categorie` : *electronique* (minuscule, sans accent) est un doublon de *Électronique* (606 lignes).
- `statut_commande` : casse incoherente — *Livrée* / *retournée* / *Annulée*.
""")

code("""\
print("=== Valeurs aberrantes numeriques ===")
print("prix_unitaire <= 0 :", (df_raw['prix_unitaire'] <= 0).sum(), "lignes -> min =", df_raw['prix_unitaire'].min())
print("remise < 0 :", (df_raw['remise'] < 0).sum(), "lignes -> min =", df_raw['remise'].min())
print("quantite == 0 :", (df_raw['quantite'] == 0).sum(), "lignes")
print()
print(df_raw[["prix_unitaire", "quantite", "remise", "cout_livraison", "cout_marketing"]].describe())
""")

md("""\
**Resume de l'audit :**

| Probleme | Volume | Decision de traitement |
|---|---|---|
| Doublons exacts (id_commande) | 100 lignes | Suppression |
| Prix unitaire invalide (<=0, souvent -50) | 622 lignes | Imputation par la mediane de la categorie |
| Remise negative (-0.10) | 600 lignes | Valeur absolue (erreur de signe probable) |
| Quantite nulle | 600 lignes | Suppression (commande sans unite = non exploitable) |
| Ville mal orthographiee (Kinshassa) | 605 lignes | Correction -> Kinshasa |
| Categorie incoherente (electronique) | 606 lignes | Fusion -> Électronique |
| Statut avec casse incoherente | tout le dataset | Capitalisation uniforme |

Les dates (`date_commande`) sont deja au format ISO `YYYY-MM-DD` et ne necessitent qu'un
typage en `datetime`, sans correction de fond.
""")

# =========================================================================
# 2. DATA CLEANING
# =========================================================================
md("""\
<a id="2"></a>
## 2. Data Cleaning

On applique ici, dans l'ordre, chaque correction identifiee lors de l'audit pour produire
le dataset propre `df_clean`.
""")

code("""\
df_clean = df_raw.copy()
n_start = len(df_clean)

# --- 2.1 Doublons exacts ---
n_dup = df_clean.duplicated().sum()
df_clean = df_clean.drop_duplicates().copy()

# --- 2.2 Standardisation des dates ---
df_clean["date_commande"] = pd.to_datetime(df_clean["date_commande"], format="%Y-%m-%d", errors="coerce")

# --- 2.3 Villes mal orthographiees ---
df_clean["ville"] = df_clean["ville"].replace({"Kinshassa": "Kinshasa"}).str.strip()

# --- 2.4 Categories incoherentes ---
df_clean["categorie"] = df_clean["categorie"].replace({"electronique": "Électronique"}).str.strip()

# --- 2.5 Statuts : casse uniforme ---
df_clean["statut_commande"] = df_clean["statut_commande"].str.strip().str.capitalize()

# --- 2.6 Remises negatives : erreur de signe -> valeur absolue, bornee a la plage metier [0, 0.30] ---
n_remise_neg = (df_clean["remise"] < 0).sum()
df_clean["remise"] = df_clean["remise"].abs().clip(lower=0, upper=0.30)

# --- 2.7 Prix aberrants (<=0) : imputation par la mediane de la categorie ---
n_prix_invalid = (df_clean["prix_unitaire"] <= 0).sum()
df_clean.loc[df_clean["prix_unitaire"] <= 0, "prix_unitaire"] = np.nan
median_prix_cat = df_clean.groupby("categorie")["prix_unitaire"].transform("median")
df_clean["prix_unitaire"] = df_clean["prix_unitaire"].fillna(median_prix_cat)

# --- 2.8 Quantites nulles : commande non exploitable -> suppression ---
n_qty_zero = (df_clean["quantite"] == 0).sum()
df_clean = df_clean[df_clean["quantite"] > 0].copy()

df_clean["id_commande"] = df_clean["id_commande"].astype(str)
df_clean["id_client"] = df_clean["id_client"].astype(str)

n_end = len(df_clean)

print("=== RAPPORT DE NETTOYAGE ===")
print(f"Lignes de depart             : {n_start}")
print(f"Doublons exacts supprimes    : {n_dup}")
print(f"Remises negatives corrigees  : {n_remise_neg}")
print(f"Prix invalides imputes       : {n_prix_invalid}")
print(f"Quantites nulles supprimees  : {n_qty_zero}")
print(f"Lignes finales (df_clean)    : {n_end}  ({n_start - n_end} lignes supprimees au total)")
""")

code("""\
# Verification post-nettoyage
print("Villes :", sorted(df_clean['ville'].unique()))
print("Categories :", sorted(df_clean['categorie'].unique()))
print("Statuts :", sorted(df_clean['statut_commande'].unique()))
df_clean.describe()
""")

# =========================================================================
# 3. FEATURE ENGINEERING
# =========================================================================
md("""\
<a id="3"></a>
## 3. Feature Engineering

On enrichit `df_clean` avec les variables necessaires aux analyses business.

**Hypothese de marge brute par categorie** (le dataset ne contient pas de cout d'achat) :
on applique un taux de marge typique du secteur e-commerce, plus faible sur l'electronique
(marche tres concurrentiel sur les prix) et plus confortable sur la mode/beaute/maison.

| Categorie | Taux de marge brute suppose |
|---|---|
| Électronique | 15% |
| Mode | 45% |
| Beauté | 50% |
| Maison | 35% |
""")

code("""\
df_features = df_clean.copy()

TAUX_MARGE = {"Électronique": 0.15, "Mode": 0.45, "Beauté": 0.50, "Maison": 0.35}

# chiffre_affaires : revenu net de la remise
df_features["chiffre_affaires"] = df_features["prix_unitaire"] * df_features["quantite"] * (1 - df_features["remise"])

# marge_brute estimee
df_features["taux_marge"] = df_features["categorie"].map(TAUX_MARGE)
df_features["marge_brute"] = df_features["chiffre_affaires"] * df_features["taux_marge"]

# profit_net estime = marge brute - couts logistiques - couts marketing
df_features["profit_net"] = df_features["marge_brute"] - df_features["cout_livraison"] - df_features["cout_marketing"]

# mois de la commande
df_features["mois"] = df_features["date_commande"].dt.to_period("M").astype(str)

# indicateurs de statut
df_features["indicateur_retour"] = (df_features["statut_commande"] == "Retournée").astype(int)
df_features["indicateur_annulation"] = (df_features["statut_commande"] == "Annulée").astype(int)

# nombre de commandes par client (frequence d'achat sur la periode)
df_features["nombre_commandes_par_client"] = df_features.groupby("id_client")["id_commande"].transform("count")

# valeur_vie_client (CLV simplifiee) : CA reel cumule genere par le client (hors commandes annulees)
ca_reel = df_features.loc[df_features["statut_commande"] != "Annulée"].groupby("id_client")["chiffre_affaires"].sum()
df_features["valeur_vie_client"] = df_features["id_client"].map(ca_reel).fillna(0)

print("df_features :", df_features.shape)
df_features[["chiffre_affaires","marge_brute","profit_net","mois",
             "indicateur_retour","nombre_commandes_par_client","valeur_vie_client"]].describe()
""")

code("""\
# On sauvegarde le dataset complet (toutes commandes, y compris annulees) : c'est la base
# utilisee par le dashboard Streamlit. Pour le calcul du CA/marge/profit, on travaille en
# revanche sur df_valid, qui exclut les commandes annulees (aucun revenu reel encaisse).
df_valid = df_features[df_features["statut_commande"] != "Annulée"].copy()
df_features.to_csv("../data/df_features.csv", index=False, encoding="utf-8")
print("Dataset final sauvegarde : df_features.csv —", df_features.shape, "| valides (hors annulations) :", df_valid.shape)
""")

# =========================================================================
# 4. ANALYSES
# =========================================================================
md("""<a id="4"></a>
## 4. Analyses demandees""")

md("""### 4.1. Performance globale""")

code("""\
ca_total = df_valid["chiffre_affaires"].sum()
ca_net_hors_retours = df_valid.loc[df_valid["statut_commande"] != "Retournée", "chiffre_affaires"].sum()
profit_net_total = df_valid["profit_net"].sum()
panier_moyen = df_valid["chiffre_affaires"].mean()
taux_annulation = (df_features["statut_commande"] == "Annulée").mean() * 100
taux_retour = (df_features["statut_commande"] == "Retournée").mean() * 100

kpis = pd.DataFrame({
    "KPI": ["CA total (brut)", "CA net (hors retours)", "Profit net estime", "Panier moyen",
            "Taux d'annulation", "Taux de retour"],
    "Valeur": [f"{ca_total:,.0f} $", f"{ca_net_hors_retours:,.0f} $", f"{profit_net_total:,.0f} $",
               f"{panier_moyen:,.2f} $", f"{taux_annulation:.2f} %", f"{taux_retour:.2f} %"]
})
kpis
""")

code("""\
fig, ax = plt.subplots(figsize=(9, 5))
evo = df_valid.groupby("mois")["chiffre_affaires"].sum()
ax.plot(evo.index, evo.values, marker="o", color=PALETTE[0], linewidth=2)
ax.set_title("Evolution mensuelle du chiffre d'affaires (global)")
ax.set_ylabel("CA ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
plt.xticks(rotation=30)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/04_evolution_ca_mensuel.png", dpi=150)
plt.show()
""")

md("""\
**Lecture :** le CA mensuel oscille entre ~410k$ et ~460k$ sans tendance de croissance nette
sur les 6 mois — coherent avec le constat de la direction (« variations importantes du CA »).
Le detail par categorie ci-dessous permet d'expliquer ces variations.
""")

md("""### 4.2. Analyse par categorie

**Question strategique : quelle categorie doit etre priorisee ou optimisee ?**
""")

code("""\
cat_stats = df_valid.groupby("categorie").agg(
    CA=("chiffre_affaires", "sum"), marge=("marge_brute", "sum"),
    profit=("profit_net", "sum"), nb_commandes=("id_commande", "count"),
).round(2)
cat_stats["CA_%"] = (cat_stats["CA"] / cat_stats["CA"].sum() * 100).round(1)
cat_stats["taux_retour_%"] = (df_features.groupby("categorie")["indicateur_retour"].mean() * 100).round(2)
cat_stats.sort_values("CA", ascending=False)
""")

code("""\
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
cat_ca = cat_stats["CA"].sort_values(ascending=False)
bars = axes[0].bar(cat_ca.index, cat_ca.values, color=PALETTE[:len(cat_ca)])
axes[0].set_title("CA par categorie")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
for b in bars:
    axes[0].annotate(f"{b.get_height()/1000:.0f}k$", (b.get_x()+b.get_width()/2, b.get_height()), ha="center", va="bottom", fontsize=9)

retour_cat = (df_features.groupby("categorie")["indicateur_retour"].mean() * 100).sort_values(ascending=False)
bars2 = axes[1].bar(retour_cat.index, retour_cat.values, color=PALETTE[3])
axes[1].set_title("Taux de retour par categorie (%)")
for b in bars2:
    axes[1].annotate(f"{b.get_height():.1f}%", (b.get_x()+b.get_width()/2, b.get_height()), ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/02_03_ca_retour_categorie.png", dpi=150)
plt.show()
""")

code("""\
evo_cat = df_valid.groupby(["mois", "categorie"])["chiffre_affaires"].sum().unstack()
fig, ax = plt.subplots(figsize=(9, 5))
for i, col in enumerate(evo_cat.columns):
    ax.plot(evo_cat.index, evo_cat[col], marker="o", label=col, color=PALETTE[i % len(PALETTE)])
ax.set_title("Evolution mensuelle du CA par categorie")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
ax.legend()
plt.xticks(rotation=30)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/05_evolution_ca_categorie.png", dpi=150)
plt.show()
""")

md("""\
**Reponse a la question strategique :**
*Électronique* genere **74.6% du CA total** mais affiche le **taux de retour le plus eleve (13.8%)**
et la **marge la plus faible (15%)** — c'est la categorie a **optimiser en priorite** (qualite produit /
selection fournisseurs pour faire baisser les retours, qui rognent directement le profit).
A l'inverse, *Beauté* et *Mode* ont des marges elevees (45-50%) et des taux de retour faibles
(<7.5%) mais un poids commercial encore marginal (3% et 7.4% du CA) : ce sont les categories a
**prioriser pour la croissance**, car chaque dollar de CA supplementaire y est nettement plus
rentable que sur l'electronique.
""")

md("""### 4.3. Analyse geographique

**Question strategique : ou devons-nous investir davantage ?**
""")

code("""\
ville_stats = df_valid.groupby("ville").agg(
    CA=("chiffre_affaires", "sum"), profit=("profit_net", "sum"), nb_commandes=("id_commande", "count"),
).round(2)
ville_stats["taux_annulation_%"] = (df_features.groupby("ville")["indicateur_annulation"].mean() * 100).round(2)
ville_stats.sort_values("CA", ascending=False)
""")

code("""\
evo_ville = df_valid.groupby(["mois", "ville"])["chiffre_affaires"].sum().unstack()
premier_mois, dernier_mois = evo_ville.index.min(), evo_ville.index.max()
croissance = ((evo_ville.loc[dernier_mois] - evo_ville.loc[premier_mois]) / evo_ville.loc[premier_mois] * 100).round(1)
croissance = croissance.sort_values(ascending=False)
print(f"Croissance du CA {premier_mois} -> {dernier_mois} (%) :")
croissance
""")

code("""\
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ville_ca = ville_stats["CA"].sort_values()
axes[0].barh(ville_ca.index, ville_ca.values, color=PALETTE[1])
axes[0].set_title("CA par ville")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))

annul_ville = ville_stats["taux_annulation_%"].sort_values(ascending=False)
colors = [PALETTE[3] if v == annul_ville.max() else PALETTE[7] for v in annul_ville.values]
bars = axes[1].bar(annul_ville.index, annul_ville.values, color=colors)
axes[1].set_title("Taux d'annulation par ville (%)")
plt.setp(axes[1].get_xticklabels(), rotation=30, ha="right")
for b in bars:
    axes[1].annotate(f"{b.get_height():.1f}%", (b.get_x()+b.get_width()/2, b.get_height()), ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/06_07_ca_annulation_ville.png", dpi=150)
plt.show()
""")

code("""\
heat = df_valid.groupby(["ville", "mois"])["chiffre_affaires"].sum().unstack().fillna(0)
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(heat, cmap="YlOrRd", annot=False, ax=ax, cbar_kws={"label": "CA ($)"})
ax.set_title("Heatmap du CA mensuel par ville")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/08_heatmap_ca_ville_mois.png", dpi=150)
plt.show()
""")

md("""\
**Reponse a la question strategique :**
*Kinshasa* (32% du CA), *Abidjan* et *Dakar* sont les 3 marches les plus solides — a consolider.
Mais ce sont *Douala* (+76% de croissance sur la periode) et *Brazzaville* (+60%) qui montrent la
**dynamique de croissance la plus forte** : ce sont les marches ou investir davantage (marketing,
stock) pour capter la traction en cours. Point d'alerte : *Douala* cumule cette forte croissance
avec un **taux d'annulation de 12.9%**, largement au-dessus des autres villes (0-1%) — signe probable
d'un probleme operationnel local (paiement, livraison) qu'il faut corriger avant d'investir davantage,
sous peine de perdre les clients acquis. *Libreville* recule (-46%) et merite un diagnostic dedie.
""")

md("""### 4.4. Analyse marketing

**Question strategique : quel canal merite plus de budget ? Lequel doit etre optimise ou reduit ?**

Formule : `ROI = (Revenus - Cout marketing) / Cout marketing`
""")

code("""\
mkt_stats = df_valid.groupby("canal_marketing").agg(
    CA=("chiffre_affaires", "sum"), cout_marketing=("cout_marketing", "sum"), nb_commandes=("id_commande", "count"),
).round(2)
mkt_stats["ROI"] = ((mkt_stats["CA"] - mkt_stats["cout_marketing"]) / mkt_stats["cout_marketing"]).round(2)
client_canal = df_features.groupby(["id_client", "canal_marketing"])["id_commande"].count().reset_index()
retention = client_canal.groupby("canal_marketing")["id_commande"].apply(lambda x: (x > 1).mean() * 100).round(2)
mkt_stats["taux_retention_%"] = retention
mkt_stats.sort_values("ROI", ascending=False)
""")

code("""\
fig, ax = plt.subplots(figsize=(8, 5))
mkt_sorted = mkt_stats.sort_values("ROI", ascending=False)
colors = [PALETTE[2] if v == mkt_sorted["ROI"].max() else (PALETTE[3] if v == mkt_sorted["ROI"].min() else PALETTE[0]) for v in mkt_sorted["ROI"]]
bars = ax.bar(mkt_sorted.index, mkt_sorted["ROI"], color=colors)
ax.set_title("ROI par canal marketing")
ax.set_ylabel("ROI (x)")
for b in bars:
    ax.annotate(f"{b.get_height():.1f}x", (b.get_x()+b.get_width()/2, b.get_height()), ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/09_roi_canal_marketing.png", dpi=150)
plt.show()
""")

md("""\
**Reponse a la question strategique :**
*Email* a de loin le **meilleur ROI (231x)** pour un budget marginal (2.3k$ sur 6 mois) — canal
**sous-investi**, a scaler en priorite (le cout marginal d'un envoi supplementaire est quasi nul).
*Instagram Ads* genere le plus de CA et la meilleure retention (54%) mais avec un ROI plus faible
(24.7x) du fait d'un budget deja consequent (37k$) : canal a **maintenir**, mais a surveiller pour
eviter les rendements decroissants. *Influenceur* cumule le **ROI le plus faible (21.6x)** et la
**retention la plus faible (42%)** : c'est le canal a **optimiser ou reduire** en premier.
""")

md("""### 4.5. Analyse clients

**Question strategique : comment ameliorer la retention ?**
""")

code("""\
nb_clients = df_features["id_client"].nunique()
commandes_par_client = df_features.groupby("id_client")["id_commande"].count()
pct_recurrents = (commandes_par_client > 1).mean() * 100
print(f"Nombre total de clients        : {nb_clients}")
print(f"%% clients recurrents (>1 cmd)  : {pct_recurrents:.2f}%")
""")

code("""\
clv = df_valid.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False)
clv_cum_pct = clv.cumsum() / clv.sum() * 100
nb_clients_80 = (clv_cum_pct <= 80).sum() + 1
print(f"Clients generant 80%% du CA : {nb_clients_80} ({nb_clients_80/len(clv)*100:.1f}% de la base)")
print()
print("Top 10 clients (CA cumule) :")
clv.head(10)
""")

code("""\
clv_sorted = clv.reset_index(drop=True)
clv_cum_pct2 = clv_sorted.cumsum() / clv_sorted.sum() * 100
pct_clients = np.arange(1, len(clv_sorted)+1) / len(clv_sorted) * 100

fig, ax1 = plt.subplots(figsize=(9, 5))
ax1.plot(pct_clients, clv_cum_pct2.values, color=PALETTE[0], linewidth=2)
ax1.axhline(80, color=PALETTE[3], linestyle="--", linewidth=1, label="80% du CA")
idx_80 = (clv_cum_pct2 <= 80).sum()
x80 = pct_clients[idx_80]
ax1.axvline(x80, color=PALETTE[3], linestyle="--", linewidth=1)
ax1.annotate(f"{x80:.0f}% des clients\\n= 80% du CA", xy=(x80, 80), xytext=(x80+10, 55),
             arrowprops=dict(arrowstyle="->", color=PALETTE[3]))
ax1.set_title("Courbe de Pareto — concentration du CA par client")
ax1.set_xlabel("% des clients (tries par CA decroissant)")
ax1.set_ylabel("% du CA cumule")
ax1.legend(loc="lower right")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/10_pareto_clients.png", dpi=150)
plt.show()
""")

code("""\
def segment(n):
    if n == 1: return "Nouveau (1 commande)"
    elif n <= 5: return "Occasionnel (2-5)"
    else: return "Fidele (6+)"

seg = commandes_par_client.apply(segment).value_counts()
fig, ax = plt.subplots(figsize=(7, 6))
ax.pie(seg.values, labels=seg.index, autopct="%1.1f%%", colors=PALETTE[:len(seg)],
       wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax.set_title("Segmentation des clients par frequence d'achat")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/11_segmentation_clients.png", dpi=150)
plt.show()
seg
""")

md("""\
**Reponse a la question strategique :**
74% des clients sont deja recurrents (au moins 2 commandes) — la base est globalement fidele.
Le CA reste toutefois concentre : **32% des clients generent 80% du CA**. Avec 26% de clients
« nouveaux » a une seule commande, le principal levier de retention est de **convertir ce segment
en acheteurs recurrents** (ex : campagne de reactivation email a J+30, qui est justement le canal
au meilleur ROI identifie en 4.4), plutot que d'acquerir de nouveaux clients a tout prix.
""")

# =========================================================================
# 5. SYNTHESE
# =========================================================================
md("""\
<a id="5"></a>
## 5. Synthese des insights cles

1. **Électronique** = 74.6% du CA mais marge la plus faible (15%) et taux de retour le plus eleve (13.8%).
2. **Douala** connait la plus forte croissance (+76%) mais aussi le plus fort taux d'annulation (12.9%) — un probleme operationnel local freine potentiellement la croissance.
3. **Email** est le canal le plus rentable (ROI 231x) mais reste largement sous-finance face a Instagram Ads.
4. **32% des clients** generent 80% du CA — la base est fidele (74% de clients recurrents) mais le segment "nouveaux clients" (26%) est mal converti en recurrence.
5. Le **profit net global estime** (~410k$ sur 6 mois) reste nettement inferieur au potentiel du CA brut (~2.51M$), du fait de la marge structurellement faible de l'electronique.
""")

md("""\
<a id="6"></a>
## 6. Recommandations strategiques

**1. Reduire le taux de retour sur l'Électronique (13.8%)**
Auditer la qualite produit et la fiche descriptive (specifications, photos) des references
electronique les plus retournees ; renforcer le controle qualite fournisseur. Un retour
economise sur cette categorie a fort volume a un effet demultiplie sur le profit net.

**2. Investiguer et corriger le probleme operationnel a Douala**
Avant d'accroitre l'investissement marketing sur ce marche en forte croissance (+76%),
diagnostiquer la cause du taux d'annulation de 12.9% (paiement mobile ? delais de livraison ?)
pour ne pas acquerir des clients qui annulent immediatement.

**3. Reallouer le budget marketing vers l'Email et reduire l'Influenceur**
Multiplier le budget Email (ROI 231x, budget actuel marginal de 2.3k$) via une segmentation
plus fine des campagnes ; reduire ou renegocier les partenariats Influenceur (ROI le plus
faible : 21.6x, retention la plus faible : 42%).

**4. Lancer un programme de reactivation des clients "1 commande" (26% de la base)**
Cibler ce segment avec une campagne Email de relance a J+30 (canal au meilleur ROI) incluant
une offre sur Mode/Beaute (categories a marge elevee) pour transformer un one-shot en client
recurrent, sans diluer la marge sur l'electronique.

**5. Prioriser la croissance sur Mode et Beaute plutot que sur l'Electronique**
Ces deux categories combinent marge elevee (45-50%) et taux de retour faible (<7.5%) mais
ne representent que 10.4% du CA cumule : chaque dollar de budget marketing ou de stock
supplementaire y genere un profit net proportionnellement plus eleve que sur l'electronique.
""")

md("""\
<a id="7"></a>
## 7. Conclusion business orientee action

AfriMarket degage un chiffre d'affaires solide (2.51M$ sur 6 mois) mais sa rentabilite est
structurellement bridee par la dependance a l'Électronique, categorie a fort volume mais a
faible marge et fort taux de retour. La **priorite immediate** n'est pas de generer plus de CA,
mais de **proteger et augmenter le profit net** en (1) reduisant les retours electronique,
(2) resolvant le probleme operationnel de Douala avant d'y investir davantage, et
(3) reallouant une partie du budget marketing d'Influenceur vers l'Email et vers les
categories a marge elevee (Mode, Beaute). La base clients, deja fidele a 74%, offre un levier
de croissance rentable via la reactivation cible des acheteurs a commande unique — une strategie
moins couteuse et plus rentable qu'une acquisition massive de nouveaux clients.
""")

nb['cells'] = cells
nb['metadata'] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.14"},
}

with open(r"c:\\Users\\LENOVO\\Desktop\\PROJET PYTHON\\notebook\\AfriMarket_Analyse.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Notebook cree :", len(cells), "cellules")
