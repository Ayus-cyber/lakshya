import pandas as pd
import random
from faker import Faker
import os
from datetime import datetime

fake = Faker()
Faker.seed(42)  # For reproducibility

# Configuration
NUM_PRODUCTS = 50
NUM_STORES = 5
NUM_SNAPSHOTS = 200
NUM_RESTOCKS = 50
OUTPUT_DIR = r"C:\Users\91823\.gemini\antigravity\brain\8f155d49-b9ca-49ba-bcb8-3c7db8ff8b32\pipeline\data\raw"

def generate_products():
    products = []
    # Create some "base" products to simulate logic
    categories = ['Electronics', 'Clothing', 'Home', 'Toys']
    for i in range(NUM_PRODUCTS):
        cat = random.choice(categories)
        products.append({
            "product_id": f"P{str(i).zfill(4)}",
            "product_name": f"{fake.word()} {cat}",
            "category": cat,
            "unit_price": round(random.uniform(10.0, 500.0), 2)
        })
    df = pd.DataFrame(products)
    df.to_csv(os.path.join(OUTPUT_DIR, "products.csv"), index=False)
    return df

def generate_stores():
    stores = []
    for i in range(NUM_STORES):
        stores.append({
            "store_id": f"S{str(i).zfill(3)}",
            "store_name": f"{fake.city()} Store",
            "city": fake.city()
        })
    df = pd.DataFrame(stores)
    df.to_csv(os.path.join(OUTPUT_DIR, "stores.csv"), index=False)
    return df

def generate_inventory_snapshot(products_df, stores_df):
    snapshots = []
    product_ids = products_df['product_id'].tolist()
    store_ids = stores_df['store_id'].tolist()
    
    # 1. Valid Data
    for _ in range(NUM_SNAPSHOTS):
        product_id = random.choice(product_ids)
        snapshots.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "store_id": random.choice(store_ids),
            "product_id": product_id,
            "quantity": random.randint(0, 500)
        })
    
    # 2. INTRODUCE ERRORS (For Validation Testing)
    
    # Error: Negative Stock
    snapshots.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "store_id": list(store_ids)[0],
        "product_id": list(product_ids)[0],
        "quantity": -10 # INVALID
    })
    
    # Error: Mismatched Product ID (Typos for fuzzy matching)
    # Pick a real product and mutate it slightly
    valid_pid = list(product_ids)[5] # e.g., P0005
    invalid_pid = valid_pid.replace("0", "O") # P0O05
    snapshots.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "store_id": list(store_ids)[0],
        "product_id": invalid_pid, # INVALID
        "quantity": 50
    })
    
    # Error: Duplicate Entry for same store/product/date
    dup_pid = list(product_ids)[2]
    dup_store = list(store_ids)[1]
    snapshots.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "store_id": dup_store,
        "product_id": dup_pid,
        "quantity": 100
    })
    snapshots.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "store_id": dup_store,
        "product_id": dup_pid, # DUPLICATE
        "quantity": 120 # Conflicting qty
    })

    df = pd.DataFrame(snapshots)
    df.to_csv(os.path.join(OUTPUT_DIR, f"inventory_snapshot_{datetime.now().strftime('%Y%m%d')}.csv"), index=False)
    return df

def generate_restock_events(products_df, stores_df):
    events = []
    product_ids = products_df['product_id'].tolist()
    store_ids = stores_df['store_id'].tolist()

    for _ in range(NUM_RESTOCKS):
        events.append({
            "event_date": datetime.now().strftime("%Y-%m-%d"),
            "store_id": random.choice(store_ids),
            "product_id": random.choice(product_ids),
            "restock_qty": random.randint(10, 200)
        })
    
    # Error: Logical Max (Huge restock)
    events.append({
        "event_date": datetime.now().strftime("%Y-%m-%d"),
        "store_id": list(store_ids)[0],
        "product_id": list(product_ids)[0],
        "restock_qty": 50000 # Unrealistic
    })

    df = pd.DataFrame(events)
    df.to_csv(os.path.join(OUTPUT_DIR, f"restock_events_{datetime.now().strftime('%Y%m%d')}.csv"), index=False)
    return df

def generate_damaged_log(products_df, stores_df):
    logs = []
    product_ids = products_df['product_id'].tolist()
    store_ids = stores_df['store_id'].tolist()
    
    # Generate some random damage events
    for _ in range(30):
        logs.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "store_id": random.choice(store_ids),
            "product_id": random.choice(product_ids),
            "damaged_qty": random.randint(1, 20)
        })
    
    df = pd.DataFrame(logs)
    df.to_csv(os.path.join(OUTPUT_DIR, f"damaged_log_{datetime.now().strftime('%Y%m%d')}.csv"), index=False)
    return df

if __name__ == "__main__":
    print("Generating Synthetic Data...")
    products = generate_products()
    stores = generate_stores()
    generate_inventory_snapshot(products, stores)
    generate_restock_events(products, stores)
    generate_damaged_log(products, stores)
    print(f"Data generated in {OUTPUT_DIR}")
