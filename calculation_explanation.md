# Understanding the Calculation Logic

This document explains exactly how we turn "Raw" data into the final **Inventory Fact** and **Quarantine** tables.

## 1. The Big Picture (Data Flow)

```mermaid
graph TD
    Raw[Raw Inventory Snapshot] --> Validator{Checks}
    Master[Master Products/Stores] --> Validator
    
    Validator -->|Pass| Valid[Valid Records]
    Validator -->|Fail| Quarantine[Quarantine Table]
    
    Quarantine --> Recon{Reconciliation<br/>(Fuzzy Match)}
    Recon -->|Success| Valid
    Recon -->|Fail| FinalQuarantine[Final Quarantine]
    
    Valid --> Aggregator[Calculation Engine]
    Restock[Raw Restock Events] -->|Valid| Aggregator
    
    Aggregator --> Fact[Inventory Fact Table<br/>(Effective Stock)]
```

## 2. How `Quarantine` is Calculated
A row ends up in the Quarantine table if it breaks **any** of these rules:

1.  **Schema Check**: Does it have the required columns? (Defined in `schema_config.yaml`)
2.  **Value Check**: Is `quantity < 0`? (We flagged this as "Negative Stock").
3.  **Master Data Integrity**:
    -   The system looks at `products.csv` and `stores.csv`.
    -   It asks: *"Does the `product_id` in this snapshot exist in the Master Product list?"*
    -   If **No** $\rightarrow$ It is flagged as **"Unknown Product ID"** and Quarantined.

*Example:*
-   **Master**: Product `P001` exists.
-   **Input**: Product `P0O1` (Letter 'O' instead of Zero).
-   **Result**: `P0O1` is not in Master $\rightarrow$ **Quarantine**.

## 3. How `Inventory Fact` is Calculated
The Fact table represents the "Truth" of your inventory. It is calculated **only** using records that passed validation (or were fixed).

**The Formula used in `main.py`:**
$$ \text{Effective Stock} = \text{Latest Snapshot Qty} + \sum \text{Restock Qty} $$

### Step-by-Step Logic:
1.  **Filter**: Take only the `Valid` (Clean) records.
2.  **Snapshots**:
    -   Group by `Store` and `Product`.
    -   Find the **latest** date.
    -   Take that `quantity` as the **Base Level**.
3.  **Restocks**:
    -   Take all valid `restock_events`.
    -   Sum up the `restock_qty` for each Store/Product combination.
4.  **Merge**:
    -   Join the **Base Level** with the **Sum of Restocks**.
    -   Add them together.

### Concrete Example
**Scenario**: Store S1, Product P1.

**1. Raw Data (Input)**
-   **Snapshot (Day 1)**: Qty = 100. (Valid)
-   **Restock (Day 2)**: Qty = +50. (Valid)
-   **Snapshot (Day 3)**: Qty = -5. (**Invalid** $\rightarrow$ Quarantine)

**2. Execution**
-   The "Day 3" snapshot is thrown out (Negative Stock).
-   The system looks for the *latest valid snapshot*. That is **Day 1** (Qty 100).
-   The system looks for valid restocks. It finds **Day 2** (+50).

**3. Final Calculation**
-   `Effective Stock = 100 (Snapshot) + 50 (Restock) = 150`

**4. Result**
-   **Inventory Fact**: `S1, P1, Effective_Stock = 150`
-   **Quarantine**: `S1, P1, -5, Reason="Negative Stock"`
