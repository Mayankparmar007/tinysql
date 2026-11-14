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
MODEL_NAME = "claude-sonnet-5-5"
BASE_URL = "https://freemodel.in/v1"

FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]

def clean_sql(raw_output: str) -> str:
    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:sql)?\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip()

def is_safe_sql(sql: str) -> bool:
    upper = sql.upper()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', upper):
            return False
    return True

def run_dev_baseline():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("[ERROR] No OPENAI_API_KEY found in .env!")
        return

    client = OpenAI(
        api_key=api_key,
        base_url=BASE_URL
    )

    conn = psycopg2.connect(db_url_clean)
    cur = conn.cursor()

    with open(DEV_FILE, "r", encoding="utf-8") as f:
        dev_items = [json.loads(line) for line in f]

    print(f"\n=======================================================")
    print(f"Running Baseline on {len(dev_items)} Dev Questions with: {MODEL_NAME}")
    print(f"Endpoint: {BASE_URL}")
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
        system_p = messages[0]["content"]
        user_q = messages[1]["content"]
        gold_sql = messages[2]["content"].strip()
        expected_refusal = (gold_sql == "REFUSE")

        t0 = time.time()
        raw_content = ""
        latency_ms = 0.0
        success = False
        max_retries = 3

        for attempt in range(max_retries):
            try:
                resp = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_p},
                        {"role": "user", "content": user_q}
                    ],
                    temperature=0.0
                )
                raw_content = resp.choices[0].message.content or ""
                latency_ms = (time.time() - t0) * 1000
                latencies.append(latency_ms)
                success = True
                break
            except Exception as e:
                err_str = str(e)
                if attempt == max_retries - 1:
                    print(f"[{idx+1}/{len(dev_items)}] API Error on Q{q_id}: {e}")
                else:
                    time.sleep(2)

        if not success or not raw_content:
            results.append({"id": q_id, "status": "FAIL (API Error)", "predicted": "", "gold": gold_sql})
            continue

        predicted = clean_sql(raw_content)

        # 1. Safety check
        if not is_safe_sql(predicted):
            unsafe_count += 1
            print(f"[{idx+1}/{len(dev_items)}] Q{q_id}: FAIL (Unsafe SQL Rejected)")
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
            status = "FAIL (Failed to Refuse)"
            results.append({"id": q_id, "status": status, "predicted": predicted, "gold": gold_sql})
            print(f"[{idx+1}/{len(dev_items)}] Q{q_id}: {status} ({latency_ms:.0f}ms)")
            continue

        # 3. Execution check on PostgreSQL
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
    print(f"BASELINE RESULTS FOR: {MODEL_NAME}")
    print(f"-------------------------------------------------------")
    print(f"Execution Accuracy : {accuracy:.1f}% ({correct}/{len(dev_items)})")
    print(f"Syntax/Exec Errors : {syntax_errors}")
    print(f"Unsafe SQL Count   : {unsafe_count}")
    print(f"Median Latency p50 : {p50_latency:.0f} ms")
    print(f"p95 Latency        : {p95_latency:.0f} ms")
    print(f"-------------------------------------------------------\n")

    out_json = os.path.join(BASE_DIR, "eval", "baseline_sonnet_dev.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved detailed question-by-question breakdown to {out_json}")

    return results

if __name__ == "__main__":
    run_dev_baseline()
