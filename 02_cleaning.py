import pandas as pd
import numpy as np

RAW_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\afrimarket_dataset_senior.csv"
OUT_PATH = r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\df_clean.csv"

df = pd.read_csv(RAW_PATH, encoding="utf-8")
n_start = len(df)

# 1. Doublons exacts (id_commande + toutes les colonnes identiques)
n_dup = df.duplicated().sum()
df = df.drop_duplicates().copy()

# 2. Dates -> datetime (le format est deja YYYY-MM-DD, on type-caste proprement)
df["date_commande"] = pd.to_datetime(df["date_commande"], format="%Y-%m-%d", errors="coerce")
n_bad_dates = df["date_commande"].isna().sum()

# 3. Villes mal orthographiees -> on uniformise vers le nom correct
ville_map = {
    "Kinshassa": "Kinshasa",
}
df["ville"] = df["ville"].replace(ville_map).str.strip()

# 4. Categories -> uniformiser casse/accents (electronique == Electronique)
categorie_map = {
    "electronique": "Électronique",
}
df["categorie"] = df["categorie"].replace(categorie_map).str.strip()

# 5. Statuts -> capitalisation uniforme (Livree / Retournee / Annulee)
df["statut_commande"] = df["statut_commande"].str.strip().str.capitalize()

# 6. Remises negatives -> erreur de saisie (signe invers?), on prend la valeur absolue
#    puis on borne dans la plage metier observee [0, 0.30]
n_remise_neg = (df["remise"] < 0).sum()
df["remise"] = df["remise"].abs()
df["remise"] = df["remise"].clip(lower=0, upper=0.30)

# 7. Prix aberrants -> les prix <= 0 (ex: -50) sont des valeurs invalides, pas des vrais prix.
#    On les remplace par la mediane du prix pour la meme categorie (valeurs valides uniquement).
n_prix_invalid = (df["prix_unitaire"] <= 0).sum()
df.loc[df["prix_unitaire"] <= 0, "prix_unitaire"] = np.nan
median_prix_categorie = df.groupby("categorie")["prix_unitaire"].transform("median")
df["prix_unitaire"] = df["prix_unitaire"].fillna(median_prix_categorie)

# 8. Quantites nulles -> une commande avec 0 unite n'a pas de sens business (CA impossible a calculer).
#    On supprime ces lignes (erreurs de saisie).
n_qty_zero = (df["quantite"] == 0).sum()
df = df[df["quantite"] > 0].copy()

# 9. cout_marketing / cout_livraison -> deja numeriques et dans des plages coherentes, rien a corriger.

# 10. Verification finale des types
df["id_commande"] = df["id_commande"].astype(str)
df["id_client"] = df["id_client"].astype(str)

n_end = len(df)

print("=== RAPPORT DE NETTOYAGE ===")
print(f"Lignes de depart            : {n_start}")
print(f"Doublons exacts supprimes   : {n_dup}")
print(f"Dates invalides (NaT)       : {n_bad_dates}")
print(f"Remises negatives corrigees : {n_remise_neg}")
print(f"Prix invalides (<=0) imputes: {n_prix_invalid}")
print(f"Quantites nulles supprimees : {n_qty_zero}")
print(f"Lignes finales              : {n_end}")
print(f"Total lignes supprimees     : {n_start - n_end}")
print()
print("Valeurs uniques ville:", sorted(df['ville'].unique()))
print("Valeurs uniques categorie:", sorted(df['categorie'].unique()))
print("Valeurs uniques statut_commande:", sorted(df['statut_commande'].unique()))
print()
print("Verification prix_unitaire:", df["prix_unitaire"].describe())
print()
print("Verification remise:", df["remise"].describe())
print()
print("dtypes finaux:")
print(df.dtypes)

df.to_csv(OUT_PATH, index=False, encoding="utf-8")
print(f"\ndf_clean sauvegarde -> {OUT_PATH}  shape={df.shape}")
