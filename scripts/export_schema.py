import os
import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/olist_db")
# psycopg2 standard format
db_url_clean = db_url.replace("postgresql+psycopg2://", "postgresql://")

conn = psycopg2.connect(db_url_clean)
cur = conn.cursor()

cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
""")
tables = [row[0] for row in cur.fetchall()]

schema_lines = []
for t in tables:
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{t}' 
        ORDER BY ordinal_position;
    """)
    cols = [f"    {col[0]} {col[1]}" for col in cur.fetchall()]
    schema_lines.append(f"CREATE TABLE {t} (\n" + ",\n".join(cols) + "\n);")

out_file = os.path.join(BASE_DIR, "data", "schema.sql")
with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n\n".join(schema_lines))

print(f"Exported clean DDL for {len(tables)} tables to data/schema.sql")
cur.close()
conn.close()
