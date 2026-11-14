---
language:
- en
license: apache-2.0
tags:
- text-to-sql
- postgresql
- qwen2.5
- qlora
- unsloth
- code-generation
base_model: Qwen/Qwen2.5-3B-Instruct
datasets:
- custom/olist-ecommerce-sql
pipeline_tag: text2text-generation
---

# Model Card for TinySQL-3B-Olist

**TinySQL-3B** is a specialized, lightweight text-to-SQL model fine-tuned from `Qwen/Qwen2.5-3B-Instruct` using 4-bit QLoRA. It is tailored to translate natural language analytics queries into performant, syntactically accurate PostgreSQL 16 queries against the 9-table [Brazilian E-Commerce (Olist)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) database.

---

## 1. Model Details

- **Model Name:** TinySQL-3B-Olist
- **Base Model:** `Qwen/Qwen2.5-3B-Instruct` (3.09 Billion Parameters)
- **Architecture:** Causal Decoder Transformer with RoPE, SwiGLU, and Grouped Query Attention (GQA)
- **Quantization:** 4-bit NormalFloat (NF4) via BitsAndBytes
- **Fine-Tuning Method:** QLoRA ($r=16, \alpha=32$, targeted: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`)
- **Tuning Library:** [Unsloth](https://github.com/unslothai/unsloth) + Hugging Face `TRL` (`SFTTrainer`)
- **Target Dialect:** PostgreSQL 16
- **Developer:** Mayank Parmar (B.Tech CSE - Cloud Computing, UPES)

---

## 2. Intended Use & Capabilities

### Intended Use Cases
1. **Natural Language Analytics & BI:** Translating business stakeholder questions into executable SQL without manual query engineering.
2. **Deterministic Schema Adherence:** Operating against a fixed 9-table relational database schema with strictly guarded foreign keys and metric definitions.
3. **Safe & Compliant Generation:** Generating strictly read-only analytical queries (`SELECT`) and refusing destructive actions (`DROP`, `DELETE`, `UPDATE`, `INSERT`).
4. **Out-of-Domain Refusal:** Emitting `REFUSE` when user requests refer to data absent from the schema (e.g. ad spend, margins, customer salary).

### Out-of-Scope & Limitations
- **General Database Portability:** The model is highly optimized for the 9-table Olist relational structure. It does not generalize out-of-the-box to arbitrary unseen enterprise databases without providing corresponding schema context or fine-tuning adapters.
- **Dialect Specificity:** Optimized for PostgreSQL 16 functions (`EXTRACT(DOW ...)`, `DATE_TRUNC`, `ILIKE`). Generating SQLite or Oracle SQL is not guaranteed.
- **Single-Annotator / Synthetic Generation:** Ground-truth pairs were synthesized with domain heuristics and verified through live PostgreSQL execution.

---

## 3. Training Data & Procedure

### Schema Topology (9 Tables, 1.5M+ rows)
- `orders` (99,441 rows)
- `order_items` (112,650 rows)
- `customers` (99,441 rows)
- `products` (32,951 rows)
- `sellers` (3,095 rows)
- `order_payments` (103,886 rows)
- `order_reviews` (99,224 rows)
- `category_translation` (71 rows)
- `geolocation` (1,000,163 rows)

### Training Split
- **Dataset Size:** 228 verified questions (158 train / 30 dev / 40 sealed test)
- **Input Format:** Standard ChatML format with Unified System Prompt containing complete table DDLs, foreign key mappings, and semantic metric definitions (delivered orders only, tiebreaker ordering).

### Hyperparameters
| Parameter | Value |
| :--- | :--- |
| Precision | 4-bit NormalFloat (NF4), bfloat16 adapter compute |
| LoRA Rank ($r$) | 16 |
| LoRA Alpha ($\alpha$) | 32 |
| LoRA Dropout | 0.0 (Unsloth optimized) |
| Optimizer | `adamw_8bit` |
| Learning Rate | `2e-4` |
| LR Schedule | Cosine with 5 warmup steps |
| Effective Batch Size | 8 (Per-device batch 2 $\times$ Gradient Accumulation 4) |
| Epochs / Steps | 3 Epochs (60 steps) |
| Max Sequence Length | 2048 tokens |
| Compute Hardware | 1x NVIDIA Tesla T4 (16 GB VRAM) on Kaggle |
| Training Duration | 14 minutes 12 seconds |
| Final Train Loss | **0.2984** |
| Final Eval Loss | **0.1140** |

---

## 4. Quantitative Evaluation

Scored on **Execution Accuracy** against live PostgreSQL 16 with deterministic SHA-256 result hashing:

| Category | Questions | Zero-Shot Raw Accuracy | Self-Healing Agent Accuracy |
| :--- | :---: | :---: | :---: |
| Single-Table Aggregations | 13 | **100.0%** (13/13) | **100.0%** (13/13) |
| Refusal Precision (Unanswerable) | 3 | **100.0%** (3/3) | **100.0%** (3/3) |
| Date & Timestamp Arithmetic | 3 | 33.3% (1/3) | 66.7% (2/3) |
| Multi-Table Joins | 8 | 25.0% (2/8) | 75.0% (6/8) |
| Analytical / Window Functions | 3 | 0.0% (0/3) | 66.7% (2/3) |
| **Overall** | **30** | **63.3%** (19/30) | **86.7%** (26/30) |

- **Unsafe SQL Injections:** 0 queries produced forbidden DDL/DML tokens.
- **Latency (vLLM on T4):** p50 = 185 ms, p95 = 310 ms.

---

## 5. Usage & Deployment

### Loading Adapter with Transformers & PEFT

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model_name = "Qwen/Qwen2.5-3B-Instruct"
adapter_path = "train/tinysql_adapter"

tokenizer = AutoTokenizer.from_pretrained(base_model_name)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
model = PeftModel.from_pretrained(base_model, adapter_path)

prompt = """<|im_start|>system
You are TinySQL, a PostgreSQL 16 Text-to-SQL expert. Return ONLY valid SQL.<|im_end|>
<|im_start|>user
What are the top 3 product categories by delivered revenue?<|im_end|>
<|im_start|>assistant
"""

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=150, do_sample=False)
print(tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
```

### Production Serving with vLLM

```bash
docker run --gpus all -p 8000:8000 \
  -v ./train/tinysql_adapter:/models/tinysql \
  vllm/vllm-openai:latest \
  --model /models/tinysql \
  --served-model-name tinysql \
  --max-model-len 2048 \
  --gpu-memory-utilization 0.9
```
