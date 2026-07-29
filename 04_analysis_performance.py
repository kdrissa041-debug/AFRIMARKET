import pandas as pd
import numpy as np

IN_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\df_features.csv"
df = pd.read_csv(IN_PATH, parse_dates=["date_commande"], encoding="utf-8")

# On exclut les commandes annulees du calcul du CA/profit (aucun revenu reel encaisse)
df_valid = df[df["statut_commande"] != "Annulée"].copy()

ca_total = df_valid["chiffre_affaires"].sum()
ca_net_hors_retours = df_valid.loc[df_valid["statut_commande"] != "Retournée", "chiffre_affaires"].sum()
profit_net_total = df_valid["profit_net"].sum()
panier_moyen = df_valid["chiffre_affaires"].mean()
taux_annulation = (df["statut_commande"] == "Annulée").mean() * 100
taux_retour = (df["statut_commande"] == "Retournée").mean() * 100
nb_commandes = len(df)
nb_commandes_valides = len(df_valid)

print("=== 4.1 PERFORMANCE GLOBALE ===")
print(f"Nombre total de commandes         : {nb_commandes:,}")
print(f"CA total (brut, hors annulees)     : {ca_total:,.2f} $")
print(f"CA net (hors annulees + retours)   : {ca_net_hors_retours:,.2f} $")
print(f"Profit net estime (total)          : {profit_net_total:,.2f} $")
print(f"Panier moyen                       : {panier_moyen:,.2f} $")
print(f"Taux d'annulation                  : {taux_annulation:.2f} %")
print(f"Taux de retour                     : {taux_retour:.2f} %")
