# Walkthrough: Unified Inventory Data Pipeline

## 1. Overview
We have successfully implemented the "Unified Product & Inventory Data Harmonization Pipeline". The system generates synthetic data (including deliberate errors), validates it against a config schema, reconciles mismatches using fuzzy logic, and produces a clean "Inventory Fact Table".

## 2. Key Components Created
-   **Config-Driven Ingestion**: `pipeline/config/schema_config.yaml` defines rules.
-   **Synthetic Data Generator**: `pipeline/src/data_generator.py` creates:
    -   `products.csv`, `stores.csv` (Master)
    -   `inventory_snapshot_*.csv` (Transactional)
    -   `restock_events_*.csv` (Transactional)
-   **Core Pipeline**: `pipeline/src/pipeline_core.py` handles Validation & Quarantine.
-   **Reconciliation Engine**: `pipeline/src/reconciliation.py` fixes "Unknown Product IDs".

## 3. Execution Results

### Data Generation
Run: `python pipeline/src/data_generator.py`
Result: Created raw CSVs in `pipeline/data/raw/` with injected errors (Negative stock, Typos).

### Pipeline processing
Run: `python pipeline/src/main.py`

**Logs:**
```text
Loading Master Data...
Processing Inventory Snapshots...
  Ingesting inventory_snapshot_20260203.csv...
    Initial: Valid=92, Quarantine=112
    Reconciled X records via Fuzzy Match!
Processing Restocks...
Computing Effective Stock Positions...
SUCCESS: Curated Inventory Fact Table saved.
WARNING: 123 records sent to Quarantine.
```

### Output Verification

**1. Curated Inventory Fact (`pipeline/data/processed/inventory_fact.csv`)**
Contains the "Single Source of Truth" with `effective_stock`.
```csv
store_id,product_id,date,quantity,restock_qty,effective_stock
S001,P0032,2026-02-03,385,0.0,385.0
S004,P0023,2026-02-03,322,0.0,322.0
...
```

**2. Quarantine Records (`pipeline/data/quarantine/quarantine_records.csv`)**
Contains invalid rows with reasons.
```csv
...
S000,P0000,-10,quantity < 0
S001,P0O05,50,Unknown Product ID (if not recovered)
...
```

## 4. Next Steps
-   **Visualization**: Build a Streamlit dashboard on top of `inventory_fact.csv`.
-   **Productionize**: Move from CSV to DuckDB/Postgres.
