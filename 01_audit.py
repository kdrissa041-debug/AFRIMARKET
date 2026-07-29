import pandas as pd
import numpy as np

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 160)

df = pd.read_csv(r"c:\Users\LENOVO\Desktop\PROJET PYTHON\data\afrimarket_dataset_senior.csv")

print("=== SHAPE ===")
print(df.shape)

print("\n=== DTYPES ===")
print(df.dtypes)

print("\n=== HEAD ===")
print(df.head(10))

print("\n=== MISSING VALUES ===")
print(df.isna().sum())
print("\n% missing:")
print((df.isna().mean()*100).round(2))

print("\n=== DUPLICATES (full row) ===")
print(df.duplicated().sum())

print("\n=== DUPLICATES (id_commande) ===")
print(df.duplicated(subset=["id_commande"]).sum())

for col in ["ville", "categorie", "methode_paiement", "canal_marketing", "statut_commande"]:
    print(f"\n=== UNIQUE VALUES: {col} ===")
    print(df[col].value_counts(dropna=False))

print("\n=== date_commande sample/parse check ===")
print(df["date_commande"].head(20))
print("min/max as string:", df["date_commande"].min(), df["date_commande"].max())

print("\n=== NUMERIC DESCRIBE ===")
for col in ["prix_unitaire","quantite","remise","cout_livraison","cout_marketing"]:
    print(f"\n--- {col} (dtype={df[col].dtype}) ---")
    print(df[col].describe())

print("\n=== cout_marketing raw sample (string oddities like 08.04) ===")
print(df["cout_marketing"].astype(str).head(30).tolist())

print("\n=== remise negative count ===")
print((pd.to_numeric(df["remise"], errors="coerce") < 0).sum())

print("\n=== quantite == 0 count ===")
print((pd.to_numeric(df["quantite"], errors="coerce") == 0).sum())

print("\n=== prix_unitaire <=0 or extreme ===")
prix = pd.to_numeric(df["prix_unitaire"], errors="coerce")
print("min", prix.min(), "max", prix.max())
print("count <=0:", (prix<=0).sum())

print("\n=== id_client unique count ===")
print(df["id_client"].nunique())

print("\n=== id_commande unique count vs rows ===")
print(df["id_commande"].nunique(), len(df))
