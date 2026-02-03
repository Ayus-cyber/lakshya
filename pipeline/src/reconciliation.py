import pandas as pd
from rapidfuzz import process, fuzz

class ReconciliationEngine:
    def __init__(self, master_products_df: pd.DataFrame):
        self.master_products_map = dict(zip(master_products_df['product_id'], master_products_df['product_name']))
        self.master_ids = list(self.master_products_map.keys())
        # We might need to match against master IDs or Names? 
        # Typically data has IDs. If ID is "P0O05" (typo), we want to match P0005.
        # But "P0O05" is a string. "P0005" is a string.
        # Simple Levenshtein on IDs might work if typos are in IDs.
        # If input has Product Name, we use that.
        # Assuming input has potentially corrupted IDs.
    
    def reconcile(self, quarantine_df: pd.DataFrame) -> pd.DataFrame:
        """
        Attempts to fix 'Unknown Product ID' errors.
        Returns a dataframe of RECOVERED records (which can be added to valid).
        """
        if quarantine_df.empty:
            return pd.DataFrame()

        # Filter only Unknown Product ID errors
        params = quarantine_df['quarantine_reason'] == "Unknown Product ID"
        to_check = quarantine_df[params].copy()
        
        if to_check.empty:
            return pd.DataFrame()

        recovered_rows = []
        
        for index, row in to_check.iterrows():
            bad_id = row['product_id']
            # Fuzzy match bad_id against all master_ids
            # rapidfuzz.process.extractOne returns (match, score, index)
            match = process.extractOne(bad_id, self.master_ids, scorer=fuzz.ratio)
            
            if match:
                best_id, score, _ = match
                if score >= 90: # Threshold from architecture
                     row['product_id'] = best_id
                     row['quarantine_reason'] = f"Fixed (Fuzzy Match: {bad_id} -> {best_id}, Score: {score})"
                     recovered_rows.append(row)
        
        return pd.DataFrame(recovered_rows)
