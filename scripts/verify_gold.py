import json
import os
import hashlib
import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/olist_db")
db_url_clean = db_url.replace("postgresql+psycopg2://", "postgresql://")

def get_deterministic_hash(cursor, query: str):
    """
    Executes SQL query, normalizes rows, rounds floats, sorts rows,
    and returns a deterministic SHA-256 hash + row count.
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    normalized_rows = []
    for row in rows:
        norm_row = []
        for val in row:
            if val is None:
                norm_row.append("__NULL__")
            elif isinstance(val, float):
                norm_row.append(f"{val:.4f}")
            else:
                norm_row.append(str(val).strip())
        normalized_rows.append(tuple(norm_row))

    # Sort rows deterministically so result set order doesn't break matching
    normalized_rows.sort()

    serialized = json.dumps(normalized_rows, ensure_ascii=True)
    hash_val = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return hash_val, len(normalized_rows)

def verify_all(eval_file=None, update_hashes=False):
    if eval_file is None:
        eval_file = os.path.join(BASE_DIR, "data", "eval_set.jsonl")

    if not os.path.exists(eval_file):
        print(f"File {eval_file} not found.")
        return False

    conn = psycopg2.connect(db_url_clean)
    cur = conn.cursor()

    passed = 0
    failed = 0
    refused = 0
    updated_items = []

    with open(eval_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line_str = line.strip()
            if not line_str:
                continue
            item = json.loads(line_str)
            q_id = item.get("id", idx + 1)
            sql = item.get("gold_sql", "").strip()

            if sql == "REFUSE":
                refused += 1
                passed += 1
                updated_items.append(item)
                continue

            try:
                computed_hash, row_count = get_deterministic_hash(cur, sql)
                stored_hash = item.get("result_hash")

                if update_hashes or not stored_hash:
                    item["result_hash"] = computed_hash
                    item["row_count"] = row_count
                    passed += 1
                elif stored_hash != computed_hash:
                    print(f"[MISMATCH] Item {q_id}: Stored={stored_hash[:8]} != Computed={computed_hash[:8]}")
                    failed += 1
                else:
                    passed += 1

                updated_items.append(item)
            except Exception as e:
                print(f"[ERROR] Item {q_id} failed with query error: {e}")
                conn.rollback()
                failed += 1
                updated_items.append(item)

    cur.close()
    conn.close()

    if update_hashes:
        with open(eval_file, "w", encoding="utf-8") as f:
            for itm in updated_items:
                f.write(json.dumps(itm, ensure_ascii=False) + "\n")
        print(f"Updated hashes in {eval_file}")

    print(f"\n--- Verification Summary ---")
    print(f"Total: {passed + failed} | Passed: {passed} (Refusals: {refused}) | Failed: {failed}")
    return failed == 0

if __name__ == "__main__":
    import sys
    update_flag = "--update" in sys.argv
    verify_all(update_hashes=update_flag)
