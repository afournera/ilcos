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






 ===== Headers in composant =====
dfs["composant"].rename(
    columns={
        "Actif": "is_active",
        "Type d'Article": "item_type",
        "Référence": "item_code",  # Matches 'item_code' from your stock table!
        "Nom": "item_name",
        "Générique": "generic_name",
        "Contenant": "container_type",
        "Palette": "palette_type",
        "Contrôle Requis": "is_control_required",
        "Contrôle Bactério": "is_bacterio_control",
        "Fournisseur par défaut": "default_supplier",
        "Article - Référence Fournisseur": "supplier_part_num",
        "Article - Nom Fournisseur": "supplier_name",
        "Prix Unitaire": "unit_price",
        "Frais Transport": "shipping_fees",
        "Prix Fournisseur - Fiche": "supplier_card_price",
        "Prix Fournisseur - Devise": "supplier_currency",
        "Unité d'Achat": "purchase_uom",
        "DDP - Transport Inclus": "is_ddp_shipping_inc",
        "Quantité Mini Cde.": "min_order_qty",
        "Quantité Maxi Cde.": "max_order_qty",
        "Stock Physique": "physical_stock_qty",
        "Stock N.C.": "nc_stock_qty",
        "Stock Conforme": "compliant_stock_qty",
        "Stock HZP": "hzp_stock_qty",
        "Stock - Refusé": "rejected_stock_qty",
        "Stock Ext.": "external_stock_qty",
        "Qté Commandée": "qty_on_order",
        "Seuil Mini": "min_stock_threshold",
        "Seuil Maxi": "max_stock_threshold",
        "Délai de Réapprovisionnement": "lead_time_days",
        "Validation Service Achat": "purchasing_approved",
        "Phasing": "phasing_status",
        "Commitment": "commitment_status",
        "Consommable": "is_consumable",
        "Stock - Indisponible": "unavailable_stock_qty",
    },
    inplace=True,
)
