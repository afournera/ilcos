import pandas as pd
import os

raw_dir = "../01-lx-raw/"

data_sources = {
    "composant": "Composants.xlsx",
    "stock": "Stock_Emplacements_Details.xlsx",
    "po_pipeline": "LigneFournisseur.xlsx",
    "wo_active": "OrdreFabrication.xlsx",
    "wo_closed": "OrdreFabrication_Closed.xlsx",
}

dfs = {}
for entity, filename in data_sources.items():
    file_path = os.path.join(raw_dir, filename)
    if os.path.exists(file_path):
        dfs[entity] = pd.read_excel(file_path, engine="openpyxl")
        print(f"successfully loaded {entity} data ({dfs[entity].shape[0]} rows).")
    else:
        print(f"Warning: File {entity} not found in {file_path}")


# 1. Concatenate Production Orders (Combine Active & Closed)
if "wo_active" in dfs and "wo_closed" in dfs:
    dfs["wo_active"]["Is_Closed"] = False
    dfs["wo_closed"]["Is_Closed"] = True
    
    # Vertically stack them
    dfs["wo_combined"] = pd.concat([dfs["wo_active"], dfs["wo_closed"]], ignore_index=True)
    
    # Free up memory by removing the separated dataframes
    del dfs["wo_active"]
    del dfs["wo_closed"]

# 2. Global Standardization Iteration
for entity_name, df in dfs.items():
    
    df.dropna(how='all', axis=1, inplace=True)

    # A. Drop wasted memory columns
    if 'Entreprise' in df.columns:
        df.drop(columns=['Entreprise'], inplace=True)
        
    # B. Fix known ERP export typos (like the missing 'e' in stock)
    if entity_name == "stock":
        df.rename(columns={"Quantit": "Quantite"}, inplace=True)
        
    # C. Strip trailing/leading whitespaces from all string columns (CRITICAL for joins)
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        # Only strip actual strings, ignore NaN floats
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        
    print(f"Cleaned {entity_name}: Dropped redundant columns and stripped strings.")




import numpy as np

# 1. Enrich Stock with Component Master Data
# This brings in the item family, type, and bacteriological control flags for dashboard filtering
df_inv = pd.merge(
    dfs["stock"],
    dfs["composant"][["Reference", "Nom", "Type d'Article", "Famille - Nom", "Controle Bacterio"]],
    left_on="Article",
    right_on="Reference",
    how="left"
)

# Drop the redundant 'Reference' column from the merge
df_inv.drop(columns=["Reference"], inplace=True)