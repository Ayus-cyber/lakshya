import os
import glob
import pandas as pd
from pipeline_core import load_config, get_dataset_config, load_csv, validate_data
from reconciliation import ReconciliationEngine

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # pipeline/
CONFIG_PATH = os.path.join(BASE_DIR, "config", "schema_config.yaml")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
QUARANTINE_DIR = os.path.join(BASE_DIR, "data", "quarantine")

def run_pipeline():
    print("--- Starting Pipeline (Functional Core) ---")
    
    # 1. Setup
    config = load_config(CONFIG_PATH)
    
    # Load Master Data
    print("Loading Master Data...")
    products_df = load_csv(RAW_DIR, "products.csv")
    master_product_ids = set(products_df['product_id'])
    
    reconciler = ReconciliationEngine(products_df)
    
    # 2. Process Inventory Snapshots
    print("Processing Inventory Snapshots...")
    inv_config = get_dataset_config(config, "inventory_snapshot")
    
    import fnmatch
    all_files = os.listdir(RAW_DIR)
    inv_files = [f for f in all_files if fnmatch.fnmatch(f, inv_config['file_pattern'])]
    
    final_valid_frames = []
    final_quarantine_frames = []

    for f in inv_files:
        print(f"  Ingesting {f}...")
        df = load_csv(RAW_DIR, f)
        
        # Validate
        valid, quarantine = validate_data(df, inv_config, master_product_ids)
        print(f"    Initial: Valid={len(valid)}, Quarantine={len(quarantine)}")
        
        # Reconcile Quarantine
        recovered = reconciler.reconcile(quarantine)
        if not recovered.empty:
            print(f"    Reconciled {len(recovered)} records via Fuzzy Match!")
            valid = pd.concat([valid, recovered], ignore_index=True)
        
        final_valid_frames.append(valid)
        final_quarantine_frames.append(quarantine)

    # 3. Aggregation / Fact Table
    if final_valid_frames:
        full_inventory = pd.concat(final_valid_frames, ignore_index=True)
        
        # Load Restocks
        print("Processing Restocks...")
        restock_config = get_dataset_config(config, "restock_events")
        res_files = [f for f in all_files if fnmatch.fnmatch(f, restock_config['file_pattern'])]
        
        restock_frames = []
        for f in res_files:
            rdf = load_csv(RAW_DIR, f)
            # Validate Restocks
            r_valid, r_quarantine = validate_data(rdf, restock_config, master_product_ids)
            restock_frames.append(r_valid)
            if not r_quarantine.empty:
                final_quarantine_frames.append(r_quarantine)
        
        if restock_frames:
            full_restock = pd.concat(restock_frames, ignore_index=True)

        # Load Damaged Logs
        print("Processing Damaged Logs...")
        damaged_config = get_dataset_config(config, "damaged_log")
        dam_files = [f for f in all_files if fnmatch.fnmatch(f, damaged_config['file_pattern'])]
        
        damaged_frames = []
        for f in dam_files:
            ddf = load_csv(RAW_DIR, f)
            d_valid, d_quarantine = validate_data(ddf, damaged_config, master_product_ids)
            damaged_frames.append(d_valid)
            if not d_quarantine.empty:
                final_quarantine_frames.append(d_quarantine)
        
        full_damaged = pd.DataFrame()
        if damaged_frames:
            full_damaged = pd.concat(damaged_frames, ignore_index=True)
        
        # 4. Compute Effective Stock
        print("Computing Effective Stock Positions...")
        
        # Sum restocks
        stock_additions = pd.DataFrame()
        if not full_restock.empty:
            stock_additions = full_restock.groupby(['store_id', 'product_id'])['restock_qty'].sum().reset_index()

        # Sum damages
        stock_deductions = pd.DataFrame()
        if not full_damaged.empty:
            stock_deductions = full_damaged.groupby(['store_id', 'product_id'])['damaged_qty'].sum().reset_index()
        
        latest_inventory = full_inventory.sort_values('date').groupby(['store_id', 'product_id']).tail(1)
        
        # Merge Restocks
        merged = pd.merge(latest_inventory, stock_additions, on=['store_id', 'product_id'], how='left')
        merged['restock_qty'] = merged['restock_qty'].fillna(0)
        
        # Merge Damages
        merged = pd.merge(merged, stock_deductions, on=['store_id', 'product_id'], how='left')
        merged['damaged_qty'] = merged['damaged_qty'].fillna(0)
        
        # Calc Formula: Snapshot + Restock - Damaged
        merged['effective_stock'] = merged['quantity'] + merged['restock_qty'] - merged['damaged_qty']
        
        # Save Gold Record
        output_file = os.path.join(PROCESSED_DIR, "inventory_fact.csv")
        merged.to_csv(output_file, index=False)
        print(f"SUCCESS: Curated Inventory Fact Table saved to {output_file}")
        print(merged[['store_id', 'product_id', 'quantity', 'restock_qty', 'damaged_qty', 'effective_stock']].head())

    # Save Quarantine
    if final_quarantine_frames:
        all_quarantine = pd.concat(final_quarantine_frames, ignore_index=True)
        q_file = os.path.join(QUARANTINE_DIR, "quarantine_records.csv")
        all_quarantine.to_csv(q_file, index=False)
        print(f"WARNING: {len(all_quarantine)} records sent to Quarantine: {q_file}")

if __name__ == "__main__":
    run_pipeline()
