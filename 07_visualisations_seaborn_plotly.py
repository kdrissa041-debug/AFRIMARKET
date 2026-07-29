import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio

IN_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\df_features.csv"
FIG_DIR = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\figures"

df = pd.read_csv(IN_PATH, parse_dates=["date_commande"], encoding="utf-8")
df_valid = df[df["statut_commande"] != "Annulée"].copy()

sns.set_style("whitegrid")
PALETTE = ["#2C5F8A", "#E07A3E", "#4C9F70", "#C44E52", "#8172B2", "#937860", "#DA8BC3", "#8C8C8C"]

# 13. Heatmap seaborn : correlation CA / marge / profit / cout_livraison / cout_marketing
num_cols = ["prix_unitaire","quantite","remise","cout_livraison","cout_marketing",
            "chiffre_affaires","marge_brute","profit_net"]
corr = df_valid[num_cols].corr()
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax,
            cbar_kws={"label": "Correlation"})
ax.set_title("Matrice de correlation des variables numeriques", fontweight="bold")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/13_heatmap_correlation_seaborn.png", dpi=150)
plt.close(fig)

# 14. Boxplot seaborn : distribution du CA par categorie (avec outliers)
fig, ax = plt.subplots(figsize=(9, 5))
order = df_valid.groupby("categorie")["chiffre_affaires"].median().sort_values(ascending=False).index
sns.boxplot(data=df_valid, x="categorie", y="chiffre_affaires", order=order, palette=PALETTE, ax=ax)
ax.set_title("Distribution du CA par commande, par categorie", fontweight="bold")
ax.set_ylabel("Chiffre d'affaires ($)")
ax.set_xlabel("")
fig.tight_layout()
fig.savefig(f"{FIG_DIR}/14_boxplot_ca_categorie_seaborn.png", dpi=150)
plt.close(fig)

# 15. Plotly interactif : CA mensuel par ville (line chart) — export HTML pour le notebook/dashboard
evo_ville = df_valid.groupby(["mois", "ville"])["chiffre_affaires"].sum().reset_index()
fig_px = px.line(evo_ville, x="mois", y="chiffre_affaires", color="ville", markers=True,
                  title="Evolution mensuelle du CA par ville (interactif)",
                  labels={"chiffre_affaires": "CA ($)", "mois": "Mois", "ville": "Ville"})
fig_px.update_layout(template="plotly_white", font=dict(size=12))
fig_px.write_html(f"{FIG_DIR}/15_plotly_evolution_ville.html", include_plotlyjs="cdn")

# 16. Plotly interactif : treemap CA par categorie/ville
tree_data = df_valid.groupby(["categorie","ville"])["chiffre_affaires"].sum().reset_index()
fig_tree = px.treemap(tree_data, path=["categorie","ville"], values="chiffre_affaires",
                       title="Repartition du CA par categorie et ville",
                       color="chiffre_affaires", color_continuous_scale="Blues")
fig_tree.write_html(f"{FIG_DIR}/16_plotly_treemap_ca.html", include_plotlyjs="cdn")

print("Figures seaborn/plotly generees.")
import os
for f in sorted(os.listdir(FIG_DIR)):
    print(" -", f)
