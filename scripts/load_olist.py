import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/olist_db")

CSV_MAPPING = {
    "customers": os.path.join(BASE_DIR, "data", "raw", "olist_customers_dataset.csv"),
    "sellers": os.path.join(BASE_DIR, "data", "raw", "olist_sellers_dataset.csv"),
    "products": os.path.join(BASE_DIR, "data", "raw", "olist_products_dataset.csv"),
    "orders": os.path.join(BASE_DIR, "data", "raw", "olist_orders_dataset.csv"),
    "order_items": os.path.join(BASE_DIR, "data", "raw", "olist_order_items_dataset.csv"),
    "order_payments": os.path.join(BASE_DIR, "data", "raw", "olist_order_payments_dataset.csv"),
    "order_reviews": os.path.join(BASE_DIR, "data", "raw", "olist_order_reviews_dataset.csv"),
    "category_translation": os.path.join(BASE_DIR, "data", "raw", "product_category_name_translation.csv"),
    "geolocation": os.path.join(BASE_DIR, "data", "raw", "olist_geolocation_dataset.csv")
}

def load_data():
    print("Connecting to PostgreSQL in Docker...")
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        res = conn.execute(text("SELECT version();")).fetchone()
        print(f"Connected: {res[0]}\n")

    for table_name, csv_path in CSV_MAPPING.items():
        if not os.path.exists(csv_path):
            print(f"[SKIP] Missing file: {csv_path}")
            continue

        print(f"Loading '{table_name}' from {os.path.basename(csv_path)}...")
        df = pd.read_csv(csv_path)

        # Convert date columns to proper datetime
        for col in df.columns:
            if "date" in col or "timestamp" in col:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Push to PostgreSQL
        df.to_sql(table_name, engine, if_exists="replace", index=False, chunksize=10000)
        print(f"  -> Successfully loaded {len(df):,} rows into '{table_name}'.")

    print("\nCreating indexes for high-speed queries...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON order_items(seller_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_payments_order_id ON order_payments(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_reviews_order_id ON order_reviews(order_id);"
    ]
    with engine.begin() as conn:
        for idx in indexes:
            conn.execute(text(idx))

    print("\n[SUCCESS] All 9 tables loaded into PostgreSQL!")

if __name__ == "__main__":
    load_data()
