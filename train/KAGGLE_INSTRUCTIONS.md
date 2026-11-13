# How to Train TinySQL on Kaggle (Free T4 GPU)

Training `Qwen2.5-3B-Instruct` on 158 examples takes **~25 minutes** on Kaggle's free T4 GPU.

---

### Step 1: Create a Kaggle Notebook
1. Go to [kaggle.com](https://www.kaggle.com) and log in.
2. Click **+ Create** -> **New Notebook**.
3. In the right-hand panel under **Notebook Options**:
   - **Accelerator**: Choose **GPU T4** (or **GPU T4 x2**).
   - **Internet**: Toggle **On** (required to download model weights and Unsloth).

---

### Step 2: Upload Your Training Data
1. In the right panel, click **+ Add Input** -> **Upload** -> Select:
   - `train/train.jsonl`
   - `train/dev.jsonl`
2. Name the dataset `tinysql-data`. Once uploaded, Kaggle will place them at:
   `/kaggle/input/tinysql-data/train.jsonl`
   `/kaggle/input/tinysql-data/dev.jsonl`

---

### Step 3: Run the Training Code
Create 3 code cells in your Kaggle notebook:

#### Cell 1: Install Dependencies
```bash
%%capture
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps trl peft accelerate bitsandbytes
```

#### Cell 2: Run Training
```python
import os
import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

# 1. Load 4-bit quantized base model
max_seq_length = 2048
model_name = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit"

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    max_seq_length=max_seq_length,
    load_in_4bit=True,
)

# 2. Add LoRA adapter (r=16, alpha=32)
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)

# 3. Load datasets
dataset = load_dataset("json", data_files={
    "train": "/kaggle/input/tinysql-data/train.jsonl",
    "eval": "/kaggle/input/tinysql-data/dev.jsonl"
})

def format_prompts(examples):
    texts = [tokenizer.apply_chat_template(c, tokenize=False, add_generation_prompt=False) for c in examples["messages"]]
    return {"text": texts}

dataset = dataset.map(format_prompts, batched=True)

# 4. Train with SFTTrainer
output_dir = "/kaggle/working/tinysql_adapter"

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    eval_dataset=dataset["eval"],
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=15,
        optim="adamw_8bit",
        output_dir=output_dir,
        report_to="none"
    ),
)

trainer.train()

# 5. Save LoRA Adapter (~40 MB)
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"Saved adapter to {output_dir}")
```

#### Cell 3: (Optional) Push Adapter Directly to Hugging Face
```python
# Set your Hugging Face write token
hf_token = "YOUR_HF_TOKEN"
repo_id = "YOUR_USERNAME/tinysql-qwen-3b-lora"

model.push_to_hub(repo_id, token=hf_token)
tokenizer.push_to_hub(repo_id, token=hf_token)
print(f"Successfully uploaded adapter to: https://huggingface.co/{repo_id}")
```

---

### Step 4: Download Your Adapter
In Kaggle's right panel under **Output** -> `/kaggle/working/tinysql_adapter`, click the three dots and select **Download**.
You can also push directly to Hugging Face Hub (free public artifact).
