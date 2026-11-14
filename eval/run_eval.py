"""
TinySQL Comprehensive Evaluation Runner
Evaluates generated SQL queries against PostgreSQL ground-truth using deterministic SHA-256 result hashing.
Supports raw model outputs and agentic self-healing mode.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import defaultdict
import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))
from scripts.verify_gold import get_deterministic_hash

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/olist_db")
db_url_clean = DB_URL.replace("postgresql+psycopg2://", "postgresql://")

EVAL_SET_PATH = os.path.join(BASE_DIR, "data", "eval_set.jsonl")
DEFAULT_DEV_PREDS = os.path.join(BASE_DIR, "eval", "tinysql_dev_predictions.json")

FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]

def clean_sql(raw_output: str) -> str:
    if not raw_output:
        return ""
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

def load_ground_truth(eval_set_path=EVAL_SET_PATH):
    ground_truth = {}
    with open(eval_set_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                item = json.loads(line_str)
                ground_truth[item["id"]] = item
    return ground_truth

def run_evaluation(predictions_file, output_csv=None, agentic_healing=False):
    if not os.path.exists(predictions_file):
        raise FileNotFoundError(f"Predictions file not found: {predictions_file}")

    with open(predictions_file, "r", encoding="utf-8") as f:
        preds = json.load(f)

    gt_map = load_ground_truth()

    conn = psycopg2.connect(db_url_clean)
    cur = conn.cursor()

    category_stats = defaultdict(lambda: {"total": 0, "correct": 0, "errors": 0, "mismatches": 0, "refusals": 0})
    detailed_rows = []
    failure_gallery = []

    print("\n" + "=" * 70)
    print(f"TinySQL Execution Evaluation: {len(preds)} Queries")
    print(f"Source file: {predictions_file}")
    print(f"Self-Healing Mode: {'ENABLED' if agentic_healing else 'DISABLED (Zero-Shot Raw)'}")
    print("=" * 70 + "\n")

    overall_correct = 0
    overall_unsafe = 0
    overall_syntax_errors = 0

    for idx, pred_item in enumerate(preds):
        qid = pred_item["id"]
        meta = gt_map.get(qid, {})
        category = meta.get("category", "unknown")
        question = meta.get("question", pred_item.get("question", ""))
        gold_sql = meta.get("gold_sql", pred_item.get("gold_sql", "")).strip()
        predicted_raw = pred_item.get("predicted_sql", "")
        predicted_sql = clean_sql(predicted_raw)

        category_stats[category]["total"] += 1
        expected_refusal = (gold_sql == "REFUSE")

        status = "UNKNOWN"
        error_msg = ""
        is_pass = False

        # 1. Safety audit
        if not is_safe_sql(predicted_sql):
            status = "FAIL_UNSAFE"
            overall_unsafe += 1
            error_msg = "Forbidden DDL/DML keyword detected"
            failure_gallery.append({
                "id": qid,
                "category": category,
                "question": question,
                "predicted": predicted_sql,
                "gold": gold_sql,
                "reason": "Unsafe statement rejected"
            })
        elif predicted_sql.upper() == "REFUSE":
            if expected_refusal:
                status = "PASS_REFUSAL"
                is_pass = True
                category_stats[category]["correct"] += 1
                category_stats[category]["refusals"] += 1
                overall_correct += 1
            else:
                status = "FAIL_FALSE_REFUSAL"
                category_stats[category]["mismatches"] += 1
                failure_gallery.append({
                    "id": qid,
                    "category": category,
                    "question": question,
                    "predicted": predicted_sql,
                    "gold": gold_sql,
                    "reason": "Model falsely refused answerable question"
                })
        elif expected_refusal:
            status = "FAIL_UNANSWERABLE_EXECUTED"
            category_stats[category]["mismatches"] += 1
            failure_gallery.append({
                "id": qid,
                "category": category,
                "question": question,
                "predicted": predicted_sql,
                "gold": gold_sql,
                "reason": "Model attempted unanswerable question instead of REFUSE"
            })
        else:
            # 2. Execution evaluation
            try:
                pred_hash, _ = get_deterministic_hash(cur, predicted_sql)
                gold_hash, _ = get_deterministic_hash(cur, gold_sql)

                if pred_hash == gold_hash:
                    status = "PASS"
                    is_pass = True
                    category_stats[category]["correct"] += 1
                    overall_correct += 1
                else:
                    status = "FAIL_RESULT_MISMATCH"
                    category_stats[category]["mismatches"] += 1
                    failure_gallery.append({
                        "id": qid,
                        "category": category,
                        "question": question,
                        "predicted": predicted_sql,
                        "gold": gold_sql,
                        "reason": "Result hash mismatch (semantic logic discrepancy)"
                    })
            except Exception as e:
                conn.rollback()
                err_line = str(e).splitlines()[0]
                status = "FAIL_EXECUTION_ERROR"
                error_msg = err_line
                overall_syntax_errors += 1
                category_stats[category]["errors"] += 1
                failure_gallery.append({
                    "id": qid,
                    "category": category,
                    "question": question,
                    "predicted": predicted_sql,
                    "gold": gold_sql,
                    "reason": f"PostgreSQL execution error: {err_line}"
                })

        mark = "✓" if is_pass else "✗"
        print(f"[{idx+1:2d}/{len(preds)}] Q{qid:3d} [{category:13s}] {mark} {status} {('('+error_msg+')') if error_msg else ''}")

        detailed_rows.append({
            "id": qid,
            "category": category,
            "question": question,
            "status": status,
            "is_pass": is_pass,
            "error_msg": error_msg,
            "predicted_sql": predicted_sql,
            "gold_sql": gold_sql
        })

    cur.close()
    conn.close()

    total_count = len(preds)
    overall_acc = (overall_correct / total_count * 100) if total_count > 0 else 0.0

    print("\n" + "=" * 70)
    print(f"{'CATEGORY':18s} | {'PASSED':8s} | {'TOTAL':6s} | {'ACCURACY':10s}")
    print("-" * 70)
    for cat, stats in sorted(category_stats.items()):
        acc = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
        print(f"{cat:18s} | {stats['correct']:8d} | {stats['total']:6d} | {acc:9.1f}%")
    print("-" * 70)
    print(f"{'OVERALL (RAW)':18s} | {overall_correct:8d} | {total_count:6d} | {overall_acc:9.1f}%")
    print("=" * 70)
    print(f"PostgreSQL Execution Errors: {overall_syntax_errors}")
    print(f"Unsafe Queries Blocked     : {overall_unsafe}")
    print("=" * 70 + "\n")

    # Save to CSV
    if not output_csv:
        output_csv = os.path.join(BASE_DIR, "eval", "results.csv")
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "category", "status", "is_pass", "error_msg", "question", "predicted_sql", "gold_sql"])
        writer.writeheader()
        writer.writerows(detailed_rows)
    print(f"Detailed per-query results exported to: {output_csv}")

    return {
        "overall_accuracy": overall_acc,
        "correct": overall_correct,
        "total": total_count,
        "category_stats": dict(category_stats),
        "failures": failure_gallery
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate TinySQL predictions.")
    parser.add_argument("--file", default=DEFAULT_DEV_PREDS, help="Path to predictions JSON")
    parser.add_argument("--out", default=None, help="Output CSV path")
    parser.add_argument("--agentic", action="store_true", help="Simulate agentic healing")
    args = parser.parse_args()

    run_evaluation(args.file, output_csv=args.out, agentic_healing=args.agentic)
