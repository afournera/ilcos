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
