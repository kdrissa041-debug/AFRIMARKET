import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.grid": True,
    "grid.color": "#e0e0e0",
    "grid.linewidth": 0.6,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
})

PALETTE = ["#2C5F8A", "#E07A3E", "#4C9F70", "#C44E52", "#8172B2", "#937860", "#DA8BC3", "#8C8C8C"]

IN_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\df_features.csv"
FIG_DIR = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\figures"

df = pd.read_csv(IN_PATH, parse_dates=["date_commande"], encoding="utf-8")
df_valid = df[df["statut_commande"] != "Annulée"].copy()

def money_fmt(x, pos):
    return f"{x/1000:.0f}k"

# 1. Distribution du panier (chiffre_affaires par commande)
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df_valid["chiffre_affaires"], bins=50, color=PALETTE[0], edgecolor="white")
ax.set_title("Distribution du chiffre d'affaires par commande")
ax.set_xlabel("Chiffre d'affaires ($)")
ax.set_ylabel("Nombre de commandes")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/01_distribution_ca.png", dpi=150)
plt.close(fig)

# 2. CA par categorie (barplot)
cat_ca = df_valid.groupby("categorie")["chiffre_affaires"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(cat_ca.index, cat_ca.values, color=PALETTE[:len(cat_ca)])
ax.set_title("Chiffre d'affaires par categorie")
ax.set_ylabel("CA ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
for b in bars:
    ax.annotate(f"{b.get_height()/1000:.0f}k$", (b.get_x()+b.get_width()/2, b.get_height()),
                ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/02_ca_par_categorie.png", dpi=150)
plt.close(fig)

# 3. Taux de retour par categorie
retour_cat = df.groupby("categorie")["indicateur_retour"].mean().sort_values(ascending=False) * 100
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(retour_cat.index, retour_cat.values, color=PALETTE[3])
ax.set_title("Taux de retour par categorie (%)")
ax.set_ylabel("Taux de retour (%)")
for b in bars:
    ax.annotate(f"{b.get_height():.1f}%", (b.get_x()+b.get_width()/2, b.get_height()),
                ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/03_taux_retour_categorie.png", dpi=150)
plt.close(fig)

# 4. Evolution mensuelle du CA global (line plot)
evo = df_valid.groupby("mois")["chiffre_affaires"].sum()
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(evo.index, evo.values, marker="o", color=PALETTE[0], linewidth=2)
ax.set_title("Evolution mensuelle du chiffre d'affaires (global)")
ax.set_ylabel("CA ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
plt.xticks(rotation=30)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/04_evolution_ca_mensuel.png", dpi=150)
plt.close(fig)

# 5. Evolution mensuelle du CA par categorie (multi-line)
evo_cat = df_valid.groupby(["mois", "categorie"])["chiffre_affaires"].sum().unstack()
fig, ax = plt.subplots(figsize=(9, 5))
for i, col in enumerate(evo_cat.columns):
    ax.plot(evo_cat.index, evo_cat[col], marker="o", label=col, color=PALETTE[i % len(PALETTE)])
ax.set_title("Evolution mensuelle du CA par categorie")
ax.set_ylabel("CA ($)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
ax.legend()
plt.xticks(rotation=30)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/05_evolution_ca_categorie.png", dpi=150)
plt.close(fig)

# 6. CA par ville (barplot horizontal)
ville_ca = df_valid.groupby("ville")["chiffre_affaires"].sum().sort_values()
fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(ville_ca.index, ville_ca.values, color=PALETTE[1])
ax.set_title("Chiffre d'affaires par ville")
ax.set_xlabel("CA ($)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/06_ca_par_ville.png", dpi=150)
plt.close(fig)

# 7. Taux d'annulation par ville
annul_ville = df.groupby("ville")["indicateur_annulation"].mean().sort_values(ascending=False) * 100
fig, ax = plt.subplots(figsize=(8, 5))
colors = [PALETTE[3] if v == annul_ville.max() else PALETTE[7] for v in annul_ville.values]
bars = ax.bar(annul_ville.index, annul_ville.values, color=colors)
ax.set_title("Taux d'annulation par ville (%)")
ax.set_ylabel("Taux d'annulation (%)")
plt.xticks(rotation=30, ha="right")
for b in bars:
    ax.annotate(f"{b.get_height():.1f}%", (b.get_x()+b.get_width()/2, b.get_height()),
                ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/07_annulation_ville.png", dpi=150)
plt.close(fig)

# 8. Heatmap CA (mois x ville) — via matplotlib imshow (pas besoin de seaborn)
heat = df_valid.groupby(["ville", "mois"])["chiffre_affaires"].sum().unstack().fillna(0)
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(heat.values, aspect="auto", cmap="YlOrRd")
ax.set_xticks(range(len(heat.columns)))
ax.set_xticklabels(heat.columns, rotation=45, ha="right")
ax.set_yticks(range(len(heat.index)))
ax.set_yticklabels(heat.index)
ax.set_title("Heatmap du CA mensuel par ville")
fig.colorbar(im, ax=ax, label="CA ($)")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/08_heatmap_ca_ville_mois.png", dpi=150)
plt.close(fig)

# 9. ROI par canal marketing
mkt = df_valid.groupby("canal_marketing").agg(CA=("chiffre_affaires","sum"), cout=("cout_marketing","sum"))
mkt["ROI"] = (mkt["CA"] - mkt["cout"]) / mkt["cout"]
mkt = mkt.sort_values("ROI", ascending=False)
fig, ax = plt.subplots(figsize=(8, 5))
colors = [PALETTE[2] if v == mkt["ROI"].max() else (PALETTE[3] if v == mkt["ROI"].min() else PALETTE[0]) for v in mkt["ROI"]]
bars = ax.bar(mkt.index, mkt["ROI"], color=colors)
ax.set_title("ROI par canal marketing")
ax.set_ylabel("ROI (x)")
for b in bars:
    ax.annotate(f"{b.get_height():.1f}x", (b.get_x()+b.get_width()/2, b.get_height()),
                ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/09_roi_canal_marketing.png", dpi=150)
plt.close(fig)

# 10. Pareto clients (80/20)
clv = df_valid.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False).reset_index(drop=True)
clv_cum_pct = clv.cumsum() / clv.sum() * 100
pct_clients = np.arange(1, len(clv)+1) / len(clv) * 100
fig, ax1 = plt.subplots(figsize=(9, 5))
ax1.plot(pct_clients, clv_cum_pct.values, color=PALETTE[0], linewidth=2)
ax1.axhline(80, color=PALETTE[3], linestyle="--", linewidth=1, label="80% du CA")
idx_80 = (clv_cum_pct <= 80).sum()
x80 = pct_clients[idx_80]
ax1.axvline(x80, color=PALETTE[3], linestyle="--", linewidth=1)
ax1.annotate(f"{x80:.0f}% des clients\n= 80% du CA", xy=(x80, 80), xytext=(x80+10, 55),
             arrowprops=dict(arrowstyle="->", color=PALETTE[3]))
ax1.set_title("Courbe de Pareto — Concentration du CA par client")
ax1.set_xlabel("% des clients (tries par CA decroissant)")
ax1.set_ylabel("% du CA cumule")
ax1.legend(loc="lower right")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/10_pareto_clients.png", dpi=150)
plt.close(fig)

# 11. Segmentation clients (pie/bar)
commandes_par_client = df.groupby("id_client")["id_commande"].count()
def segment(n):
    if n == 1: return "Nouveau (1 cmd)"
    elif n <= 5: return "Occasionnel (2-5)"
    else: return "Fidele (6+)"
seg = commandes_par_client.apply(segment).value_counts()
fig, ax = plt.subplots(figsize=(7, 6))
ax.pie(seg.values, labels=seg.index, autopct="%1.1f%%", colors=PALETTE[:len(seg)],
       wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax.set_title("Segmentation des clients par frequence d'achat")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/11_segmentation_clients.png", dpi=150)
plt.close(fig)

# 12. Marge et profit par categorie (barplot groupe)
cat_pl = df_valid.groupby("categorie").agg(CA=("chiffre_affaires","sum"), marge=("marge_brute","sum"), profit=("profit_net","sum"))
cat_pl = cat_pl.sort_values("CA", ascending=False)
x = np.arange(len(cat_pl))
width = 0.35
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(x - width/2, cat_pl["marge"], width, label="Marge brute", color=PALETTE[0])
ax.bar(x + width/2, cat_pl["profit"], width, label="Profit net", color=PALETTE[1])
ax.set_xticks(x)
ax.set_xticklabels(cat_pl.index)
ax.set_title("Marge brute vs profit net par categorie")
ax.set_ylabel("$")
ax.legend()
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/12_marge_profit_categorie.png", dpi=150)
plt.close(fig)

print("12 figures generees dans", FIG_DIR)
import os
for f in sorted(os.listdir(FIG_DIR)):
    print(" -", f)
