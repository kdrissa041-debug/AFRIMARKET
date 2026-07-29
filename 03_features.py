import pandas as pd
import numpy as np

IN_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\df_clean.csv"
OUT_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\df_features.csv"

df = pd.read_csv(IN_PATH, parse_dates=["date_commande"], encoding="utf-8")

# Hypothese de marge brute par categorie (a defaut de cout d'achat reel dans les donnees).
# Valeurs typiques du e-commerce : forte concurrence/prix sur l'electronique (marge faible),
# marges plus confortables sur mode/beaute/maison.
TAUX_MARGE = {
    "Électronique": 0.15,
    "Mode": 0.45,
    "Beauté": 0.50,
    "Maison": 0.35,
}

# --- chiffre_affaires : revenu net de la remise, par ligne de commande ---
df["chiffre_affaires"] = df["prix_unitaire"] * df["quantite"] * (1 - df["remise"])

# --- marge_brute estimee : CA * taux de marge hypothetique de la categorie ---
df["taux_marge"] = df["categorie"].map(TAUX_MARGE)
df["marge_brute"] = df["chiffre_affaires"] * df["taux_marge"]

# --- profit_net estime : marge brute - couts logistiques - couts marketing ---
df["profit_net"] = df["marge_brute"] - df["cout_livraison"] - df["cout_marketing"]

# --- mois : periode mensuelle de la commande ---
df["mois"] = df["date_commande"].dt.to_period("M").astype(str)

# --- indicateur_retour : commande retournee (1) ou non (0) ---
df["indicateur_retour"] = (df["statut_commande"] == "Retournée").astype(int)
df["indicateur_annulation"] = (df["statut_commande"] == "Annulée").astype(int)

# --- nombre_commandes_par_client : frequence d'achat sur les 6 mois ---
df["nombre_commandes_par_client"] = df.groupby("id_client")["id_commande"].transform("count")

# --- valeur_vie_client (CLV simplifiee) : somme du CA genere par client sur la periode ---
# (hors commandes annulees, qui ne generent aucun revenu reel)
ca_reel = df.loc[df["statut_commande"] != "Annulée"].groupby("id_client")["chiffre_affaires"].sum()
df["valeur_vie_client"] = df["id_client"].map(ca_reel).fillna(0)

print("=== APERCU df_features ===")
print(df.shape)
print(df[["chiffre_affaires","marge_brute","profit_net","mois","indicateur_retour",
          "nombre_commandes_par_client","valeur_vie_client"]].describe())
print()
print(df.head(5).to_string())

df.to_csv(OUT_PATH, index=False, encoding="utf-8")
print(f"\ndf_features sauvegarde -> {OUT_PATH}")
