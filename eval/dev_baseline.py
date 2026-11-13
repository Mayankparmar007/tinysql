import json
import os
import sys
import re
import time
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

from scripts.verify_gold import get_deterministic_hash

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/olist_db")
db_url_clean = DB_URL.replace("postgresql+psycopg2://", "postgresql://")

DEV_FILE = os.path.join(BASE_DIR, "train", "dev.jsonl")

FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]

def clean_sql(raw_output: str) -> str:
    cleaned = raw_output.strip()
    # Strip markdown if model added it
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:sql)?\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip()

def is_safe_sql(sql: str) -> bool:
    upper = sql.upper()
    for kw in FORBIDDEN_KEYWORDS:
        # Match as standalone word
        if re.search(r'\b' + kw + r'\b', upper):
            return False
    return True

def run_dev_baseline(model_name="gpt-4o-mini", api_base=None, api_key=None):
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key and not api_base:
        print("[ERROR] No OPENAI_API_KEY found in .env! Please set OPENAI_API_KEY in .env to run gpt-4o-mini.")
        return

    client = OpenAI(
        api_key=api_key or "dummy-key",
        base_url=api_base
    )

    conn = psycopg2.connect(db_url_clean)
    cur = conn.cursor()

    with open(DEV_FILE, "r", encoding="utf-8") as f:
        dev_items = [json.loads(line) for line in f]

    print(f"\n=======================================================")
    print(f"Running Baseline on {len(dev_items)} Dev Questions with: {model_name}")
    print(f"=======================================================\n")

    correct = 0
    refused_correct = 0
    unsafe_count = 0
    syntax_errors = 0
    latencies = []

    results = []

    for idx, item in enumerate(dev_items):
        q_id = item["id"]
        messages = item["messages"]
        user_q = messages[1]["content"]
        gold_sql = messages[2]["content"].strip()
        expected_refusal = (gold_sql == "REFUSE")

        t0 = time.time()
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": messages[0]["content"]},
                    {"role": "user", "content": user_q}
                ],
                temperature=0.0
            )
            raw_content = resp.choices[0].message.content or ""
            latency_ms = (time.time() - t0) * 1000
            latencies.append(latency_ms)
        except Exception as e:
            print(f"[{idx+1}/{len(dev_items)}] API Error on Q{q_id}: {e}")
            continue

        predicted = clean_sql(raw_content)

        # 1. Safety check
        if not is_safe_sql(predicted):
            unsafe_count += 1
            print(f"[{idx+1}/{len(dev_items)}] Q{q_id} UNSAFE SQL REJECTED: {predicted}")
            continue

        # 2. Refusal check
        if predicted.upper() == "REFUSE":
            if expected_refusal:
                correct += 1
                refused_correct += 1
                status = "PASS (Refusal)"
            else:
                status = "FAIL (False Refusal)"
            results.append({"id": q_id, "status": status, "predicted": predicted, "gold": gold_sql})
            print(f"[{idx+1}/{len(dev_items)}] Q{q_id}: {status} ({latency_ms:.0f}ms)")
            continue

        if expected_refusal:
            # Model generated SQL when it should have refused
            status = "FAIL (Failed to Refuse)"
            results.append({"id": q_id, "status": status, "predicted": predicted, "gold": gold_sql})
            print(f"[{idx+1}/{len(dev_items)}] Q{q_id}: {status} ({latency_ms:.0f}ms)")
            continue

        # 3. Execution accuracy check
        try:
            pred_hash, pred_rows = get_deterministic_hash(cur, predicted)
            gold_hash, gold_rows = get_deterministic_hash(cur, gold_sql)

            if pred_hash == gold_hash:
                correct += 1
                status = "PASS"
            else:
                status = "FAIL (Result Mismatch)"
        except Exception as err:
            conn.rollback()
            syntax_errors += 1
            status = f"FAIL (Execution Error: {str(err).splitlines()[0]})"

        results.append({"id": q_id, "status": status, "predicted": predicted, "gold": gold_sql})
        print(f"[{idx+1}/{len(dev_items)}] Q{q_id}: {status} ({latency_ms:.0f}ms)")

    cur.close()
    conn.close()

    accuracy = (correct / len(dev_items)) * 100
    p50_latency = sorted(latencies)[len(latencies)//2] if latencies else 0
    p95_latency = sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0

    print(f"\n-------------------------------------------------------")
    print(f"BASELINE RESULTS FOR: {model_name}")
    print(f"-------------------------------------------------------")
    print(f"Execution Accuracy : {accuracy:.1f}% ({correct}/{len(dev_items)})")
    print(f"Syntax/Exec Errors : {syntax_errors}")
    print(f"Unsafe SQL Count   : {unsafe_count}")
    print(f"Median Latency p50 : {p50_latency:.0f} ms")
    print(f"p95 Latency        : {p95_latency:.0f} ms")
    print(f"-------------------------------------------------------\n")

    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-4o-mini", help="Model name")
    parser.add_argument("--api-base", default=None, help="Custom API base url")
    args = parser.parse_args()

    run_dev_baseline(model_name=args.model, api_base=args.api_base)
