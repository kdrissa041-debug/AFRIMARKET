import pandas as pd
import numpy as np

pd.set_option("display.width", 160)
IN_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\df_features.csv"
df = pd.read_csv(IN_PATH, parse_dates=["date_commande"], encoding="utf-8")
df_valid = df[df["statut_commande"] != "Annulée"].copy()

print("############################################")
print("4.2 ANALYSE PAR CATEGORIE")
print("############################################")
cat_stats = df_valid.groupby("categorie").agg(
    CA=("chiffre_affaires", "sum"),
    marge=("marge_brute", "sum"),
    profit=("profit_net", "sum"),
    nb_commandes=("id_commande", "count"),
).round(2)
cat_stats["CA_%"] = (cat_stats["CA"] / cat_stats["CA"].sum() * 100).round(1)
taux_retour_cat = df.groupby("categorie")["indicateur_retour"].mean() * 100
cat_stats["taux_retour_%"] = taux_retour_cat.round(2)
print(cat_stats.sort_values("CA", ascending=False))

print("\nEvolution mensuelle du CA par categorie:")
evo_cat = df_valid.groupby(["mois", "categorie"])["chiffre_affaires"].sum().unstack().round(0)
print(evo_cat)

print("\n############################################")
print("4.3 ANALYSE GEOGRAPHIQUE")
print("############################################")
ville_stats = df_valid.groupby("ville").agg(
    CA=("chiffre_affaires", "sum"),
    profit=("profit_net", "sum"),
    nb_commandes=("id_commande", "count"),
).round(2)
taux_annulation_ville = df.groupby("ville")["indicateur_annulation"].mean() * 100
ville_stats["taux_annulation_%"] = taux_annulation_ville.round(2)
print(ville_stats.sort_values("CA", ascending=False))

print("\nCroissance mensuelle du CA par ville (premier vs dernier mois):")
evo_ville = df_valid.groupby(["mois", "ville"])["chiffre_affaires"].sum().unstack().round(0)
premier_mois, dernier_mois = evo_ville.index.min(), evo_ville.index.max()
croissance = ((evo_ville.loc[dernier_mois] - evo_ville.loc[premier_mois]) / evo_ville.loc[premier_mois] * 100).round(1)
print(f"Croissance {premier_mois} -> {dernier_mois} (%):")
print(croissance.sort_values(ascending=False))

print("\n############################################")
print("4.4 ANALYSE MARKETING")
print("############################################")
mkt_stats = df_valid.groupby("canal_marketing").agg(
    CA=("chiffre_affaires", "sum"),
    cout_marketing=("cout_marketing", "sum"),
    nb_commandes=("id_commande", "count"),
).round(2)
mkt_stats["ROI"] = ((mkt_stats["CA"] - mkt_stats["cout_marketing"]) / mkt_stats["cout_marketing"]).round(2)
# taux de retention par canal = % de clients acquis sur ce canal qui ont commande plus d'une fois
client_canal = df.groupby(["id_client", "canal_marketing"])["id_commande"].count().reset_index()
retention = client_canal.groupby("canal_marketing")["id_commande"].apply(lambda x: (x > 1).mean() * 100).round(2)
mkt_stats["taux_retention_%"] = retention
print(mkt_stats.sort_values("ROI", ascending=False))

print("\n############################################")
print("4.5 ANALYSE CLIENTS")
print("############################################")
nb_clients = df["id_client"].nunique()
commandes_par_client = df.groupby("id_client")["id_commande"].count()
pct_recurrents = (commandes_par_client > 1).mean() * 100
print(f"Nombre total de clients          : {nb_clients}")
print(f"%% clients recurrents (>1 cmd)    : {pct_recurrents:.2f} %")

# Pareto 80/20 sur le CA valide
clv = df_valid.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False)
clv_cum_pct = clv.cumsum() / clv.sum() * 100
nb_clients_pour_80pct = (clv_cum_pct <= 80).sum() + 1
pct_clients_80 = nb_clients_pour_80pct / len(clv) * 100
print(f"Clients generant 80%% du CA       : {nb_clients_pour_80pct} clients ({pct_clients_80:.1f}%% de la base)")

print("\nTop 10 clients (par CA cumule):")
print(clv.head(10))

# Segmentation simple par nombre de commandes
def segment(n):
    if n == 1:
        return "Nouveau (1 commande)"
    elif n <= 5:
        return "Occasionnel (2-5)"
    else:
        return "Fidele (6+)"

seg = commandes_par_client.apply(segment).value_counts()
print("\nSegmentation clients par frequence d'achat:")
print(seg)
