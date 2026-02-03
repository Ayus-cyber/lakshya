import yaml
import pandas as pd
import os
from typing import Dict, List, Tuple

# --- Config Functions ---
def load_config(config_path: str) -> Dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_dataset_config(config: Dict, dataset_name: str) -> Dict:
    return config['datasets'].get(dataset_name)

# --- Ingestion Functions ---
def load_csv(data_dir: str, filename: str) -> pd.DataFrame:
    path = os.path.join(data_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path)

# --- Validation Functions ---
def validate_data(df: pd.DataFrame, rules: Dict, master_products: set) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits input df into valid_df and quarantine_df based on rules.
    """
    df['quarantine_reason'] = None
    
    # We'll use a mask to track invalid rows
    # True = Invalid/Quarantine
    quarantine_mask = pd.Series([False] * len(df))

    # Check: Negative Stock / Min Value
    for col in rules.get('required_columns', []):
        col_name = col['name']
        checks = col.get('checks', [])
        
        if col_name not in df.columns:
            continue 

        if "min_0" in checks:
            is_negative = df[col_name] < 0
            df.loc[is_negative, 'quarantine_reason'] = f"{col_name} < 0"
            quarantine_mask |= is_negative

        if "max_1000" in checks: # Example logical max
            is_huge = df[col_name] > 1000
            df.loc[is_huge, 'quarantine_reason'] = f"{col_name} > 1000"
            quarantine_mask |= is_huge

    # Check: Master Data Validation (Product ID logic)
    if 'product_id' in df.columns:
        is_unknown = ~df['product_id'].isin(master_products)
        new_unknowns = is_unknown & (~quarantine_mask)
        df.loc[new_unknowns, 'quarantine_reason'] = "Unknown Product ID"
        quarantine_mask |= is_unknown

    # Check: Duplicates (Store + Product + Date)
    if all(x in df.columns for x in ['store_id', 'product_id']):
        date_col = 'date' if 'date' in df.columns else 'event_date'
        if date_col in df.columns:
            subset = ['store_id', 'product_id', date_col]
            is_dup = df.duplicated(subset=subset, keep=False) 
            new_dups = is_dup & (~quarantine_mask)
            df.loc[new_dups, 'quarantine_reason'] = "Duplicate Entry"
            quarantine_mask |= is_dup

    quarantine_df = df[quarantine_mask].copy()
    valid_df = df[~quarantine_mask].copy()
    
    return valid_df, quarantine_df
