import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_FILE = os.path.join(BASE_DIR, "data", "schema.sql")
NOTES_FILE = os.path.join(BASE_DIR, "data", "NOTES.md")

def get_system_prompt():
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_ddl = f.read().strip()

    prompt = f"""You are an expert PostgreSQL data analyst.
Given a PostgreSQL database schema and business semantic rules, convert the user's natural language question into a single, valid, executable SQL query.

### INSTRUCTIONS & CONSTRAINTS:
1. Return ONLY the raw SQL statement. Do NOT include markdown formatting (no ```sql), no explanation, and no comments.
2. Read-only SELECT queries ONLY. Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
3. If the question CANNOT be answered using the provided schema (e.g., asking for customer age, gender, returns, discounts, inventory, employee data, profit margins, or details not tracked), respond with the exact word: REFUSE
4. Strict Business Metric Definitions:
   - Delivered Order: Filter with `order_status = 'delivered'` for all revenue/delivery metrics unless specified otherwise.
   - Net Revenue: `SUM(price)` from `order_items` for delivered orders (excludes freight).
   - Total Order Value: `SUM(price + freight_value)` from `order_items`.
   - Late Delivery: `order_delivered_customer_date > order_estimated_delivery_date`.
   - Delivery Duration (Days): `EXTRACT(DAY FROM (order_delivered_customer_date - order_purchase_timestamp))`.
   - Active Seller: A seller associated with at least one delivered order.

### DATABASE SCHEMA (PostgreSQL):
{schema_ddl}
"""
    return prompt.strip()

if __name__ == "__main__":
    p = get_system_prompt()
    print("System Prompt Preview (first 500 chars):\n")
    print(p[:500] + "\n...")
    print(f"\nTotal characters: {len(p)}")
