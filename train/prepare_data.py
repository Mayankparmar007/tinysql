import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from train.prompt_template import get_system_prompt

EVAL_SET = os.path.join(BASE_DIR, "data", "eval_set.jsonl")
TRAIN_OUT = os.path.join(BASE_DIR, "train", "train.jsonl")
DEV_OUT = os.path.join(BASE_DIR, "train", "dev.jsonl")

def prepare_chat_data():
    system_prompt = get_system_prompt()

    train_data = []
    dev_data = []

    with open(EVAL_SET, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            item = json.loads(line_str)
            split = item.get("split")

            if split not in ["train", "dev"]:
                # Test split remains completely sealed
                continue

            chat_record = {
                "id": item["id"],
                "category": item["category"],
                "split": split,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": item["question"]},
                    {"role": "assistant", "content": item["gold_sql"]}
                ]
            }

            if split == "train":
                train_data.append(chat_record)
            elif split == "dev":
                dev_data.append(chat_record)

    with open(TRAIN_OUT, "w", encoding="utf-8") as f:
        for r in train_data:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(DEV_OUT, "w", encoding="utf-8") as f:
        for r in dev_data:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Generated {len(train_data)} training examples -> {TRAIN_OUT}")
    print(f"Generated {len(dev_data)} validation examples -> {DEV_OUT}")

if __name__ == "__main__":
    prepare_chat_data()
