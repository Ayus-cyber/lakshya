# Implementation Plan: Visualization Dashboard

## Goal
Create a Streamlit dashboard to provide "Operational Intelligence" on the inventory pipeline.

## Features
1.  **KPI Metrics**: Total SKUs, Total Stock, Quarantine Ratio.
2.  **Data Quality Overview**: Bar chart showing Valid vs. Quarantine records.
3.  **Quarantine Analysis**: Breakdown of rejection reasons (e.g., "Unknown Product ID", "Negative Stock").
4.  **Reconciliation Impact**: Stat showing how many records were "Saved" by fuzzy matching.
5.  **Inventory Table**: View the final "Silver/Gold" dataset.

## Technical Details
-   **File**: `pipeline/src/dashboard.py`
-   **Libs**: `streamlit`, `pandas`, `plotly` (or `altair` if preferred, sticking to simple st charts).
-   **Input**: Reads CSVs from `pipeline/data/processed` and `pipeline/data/quarantine`.

## Verification
-   Run `streamlit run pipeline/src/dashboard.py`.
-   Verify charts render and interactions work.
