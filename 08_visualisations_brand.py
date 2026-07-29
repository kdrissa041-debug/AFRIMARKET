# -*- coding: utf-8 -*-
"""Regenere les visualisations cles avec la charte graphique AfriMarket (rouge/anthracite)
pour usage dans le PowerPoint et le rapport PDF."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

IN_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\df_features.csv"
FIG_DIR = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\figures\brand"
os.makedirs(FIG_DIR, exist_ok=True)

# --- Charte graphique AfriMarket (extraite du logo) ---
RED = "#C42D1C"
RED_DARK = "#8E2013"
TERRACOTTA = "#E0725F"
GRAY = "#3F3F3F"
GRAY_LIGHT = "#8C8C8C"
GRAY_PALE = "#D9D9D9"

CAT_COLORS = {"Mode": RED, "Électronique": GRAY, "Beauté": TERRACOTTA, "Maison": GRAY_LIGHT}

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "axes.edgecolor": GRAY,
    "axes.grid": True, "grid.color": "#EAEAEA", "grid.linewidth": 0.7,
    "font.size": 12, "font.family": "Calibri" if "Calibri" in [f.name for f in matplotlib.font_manager.fontManager.ttflist] else "sans-serif",
    "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlecolor": GRAY,
    "text.color": GRAY, "axes.labelcolor": GRAY, "xtick.color": GRAY, "ytick.color": GRAY,
})

df = pd.read_csv(IN_PATH, parse_dates=["date_commande"], encoding="utf-8")
df_valid = df[df["statut_commande"] != "Annulée"].copy()

def money_fmt(x, pos):
    return f"{x/1000:.0f}k"

def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/{name}.png", dpi=200, facecolor="white")
    plt.close(fig)

# 1. CA par categorie
cat_ca = df_valid.groupby("categorie")["chiffre_affaires"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 4.2))
colors = [CAT_COLORS[c] for c in cat_ca.index]
bars = ax.bar(cat_ca.index, cat_ca.values, color=colors, width=0.6)
ax.set_title("Chiffre d'affaires par categorie")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
for b in bars:
    ax.annotate(f"{b.get_height()/1000:.0f}k$", (b.get_x()+b.get_width()/2, b.get_height()),
                ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "01_ca_categorie")

# 2. Taux de retour par categorie (meme ordre que le graphique CA pour comparaison visuelle directe)
retour_cat = (df.groupby("categorie")["indicateur_retour"].mean() * 100).reindex(cat_ca.index)
fig, ax = plt.subplots(figsize=(7, 4.2))
colors = [RED if v == retour_cat.max() else GRAY_LIGHT for v in retour_cat.values]
bars = ax.bar(retour_cat.index, retour_cat.values, color=colors, width=0.6)
ax.set_title("Taux de retour par categorie (%)")
for b in bars:
    ax.annotate(f"{b.get_height():.1f}%", (b.get_x()+b.get_width()/2, b.get_height()),
                ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "02_retour_categorie")

# 3. Evolution mensuelle CA par categorie
evo_cat = df_valid.groupby(["mois", "categorie"])["chiffre_affaires"].sum().unstack()
fig, ax = plt.subplots(figsize=(9, 4.5))
for col in evo_cat.columns:
    ax.plot(evo_cat.index, evo_cat[col], marker="o", label=col, color=CAT_COLORS[col], linewidth=2.5)
ax.set_title("Evolution mensuelle du CA par categorie")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18))
ax.spines[["top", "right"]].set_visible(False)
plt.xticks(rotation=20)
save(fig, "03_evolution_categorie")

# 4. CA par ville
ville_ca = df_valid.groupby("ville")["chiffre_affaires"].sum().sort_values()
fig, ax = plt.subplots(figsize=(7, 5))
colors = [RED if v == ville_ca.max() else GRAY_LIGHT for v in ville_ca.values]
ax.barh(ville_ca.index, ville_ca.values, color=colors)
ax.set_title("Chiffre d'affaires par ville")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
ax.spines[["top", "right"]].set_visible(False)
save(fig, "04_ca_ville")

# 5. Taux d'annulation par ville (Douala en evidence)
annul_ville = (df.groupby("ville")["indicateur_annulation"].mean() * 100).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7.5, 4.2))
colors = [RED if v == annul_ville.max() else GRAY_PALE for v in annul_ville.values]
bars = ax.bar(annul_ville.index, annul_ville.values, color=colors)
ax.set_title("Taux d'annulation par ville (%)")
plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
for b in bars:
    if b.get_height() > 1:
        ax.annotate(f"{b.get_height():.1f}%", (b.get_x()+b.get_width()/2, b.get_height()),
                    ha="center", va="bottom", fontsize=10, fontweight="bold", color=RED)
ax.spines[["top", "right"]].set_visible(False)
save(fig, "05_annulation_ville")

# 6. ROI par canal marketing
mkt = df_valid.groupby("canal_marketing").agg(CA=("chiffre_affaires","sum"), cout=("cout_marketing","sum"))
mkt["ROI"] = (mkt["CA"] - mkt["cout"]) / mkt["cout"]
mkt = mkt.sort_values("ROI", ascending=False)
fig, ax = plt.subplots(figsize=(7, 4.2))
colors = [RED if v == mkt["ROI"].max() else (GRAY if v == mkt["ROI"].min() else GRAY_LIGHT) for v in mkt["ROI"]]
bars = ax.bar(mkt.index, mkt["ROI"], color=colors, width=0.6)
ax.set_title("ROI par canal marketing")
for b in bars:
    ax.annotate(f"{b.get_height():.1f}x", (b.get_x()+b.get_width()/2, b.get_height()),
                ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "06_roi_marketing")

# 7. Pareto clients
clv = df_valid.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False).reset_index(drop=True)
clv_cum_pct = clv.cumsum() / clv.sum() * 100
pct_clients = np.arange(1, len(clv)+1) / len(clv) * 100
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.plot(pct_clients, clv_cum_pct.values, color=RED, linewidth=3)
ax.axhline(80, color=GRAY, linestyle="--", linewidth=1)
idx_80 = (clv_cum_pct <= 80).sum()
x80 = pct_clients[idx_80]
ax.axvline(x80, color=GRAY, linestyle="--", linewidth=1)
ax.annotate(f"{x80:.0f}% des clients = 80% du CA", xy=(x80, 80), xytext=(x80+8, 45),
            arrowprops=dict(arrowstyle="->", color=GRAY), fontsize=10, fontweight="bold", color=GRAY)
ax.set_title("Courbe de Pareto — concentration du CA par client")
ax.set_xlabel("% des clients")
ax.set_ylabel("% du CA cumule")
ax.spines[["top", "right"]].set_visible(False)
save(fig, "07_pareto_clients")

# 8. Segmentation clients (donut)
commandes_par_client = df.groupby("id_client")["id_commande"].count()
def segment(n):
    if n == 1: return "Nouveau (1 cmd)"
    elif n <= 5: return "Occasionnel (2-5)"
    else: return "Fidele (6+)"
seg = commandes_par_client.apply(segment).value_counts()
seg_colors = [GRAY_LIGHT, RED, GRAY]
fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(seg.values, labels=seg.index, autopct="%1.0f%%",
       colors=seg_colors, wedgeprops={"edgecolor": "white", "linewidth": 2}, pctdistance=0.8,
       textprops={"fontsize": 11})
centre_circle = plt.Circle((0,0), 0.55, fc="white")
fig.gca().add_artist(centre_circle)
ax.set_title("Segmentation des clients")
save(fig, "08_segmentation_clients")

print("Figures de marque generees dans", FIG_DIR)
for f in sorted(os.listdir(FIG_DIR)):
    print(" -", f)
