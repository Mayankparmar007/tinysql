"""
TinySQL: QLoRA Fine-Tuning Script using Unsloth
Model: Qwen2.5-3B-Instruct
Target: 158 training examples, 30 dev validation examples
"""

import os
import torch

def train():
    # 1. Check GPU availability
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Please run this script in a GPU environment (Kaggle T4 or rented 4090).")

    print(f"CUDA Device: {torch.cuda.get_device_name(0)}")

    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import load_dataset
    except ImportError:
        print("\nMissing libraries. Install them via:")
        print("pip install \"unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git\"")
        print("pip install --no-deps trl peft accelerate bitsandbytes")
        return

    # 2. Configuration
    max_seq_length = 2048
    model_name = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit"
    output_dir = os.environ.get("OUTPUT_DIR", "./tinysql_adapter")

    print(f"\nLoading base model: {model_name}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
        dtype=None, # Auto-detect float16 / bfloat16
    )

    # 3. Add LoRA adapters (QLoRA)
    print("\nAdding LoRA adapters (r=16, alpha=32)...")
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

    # 4. Load dataset
    train_file = os.environ.get("TRAIN_FILE", "train/train.jsonl")
    dev_file = os.environ.get("DEV_FILE", "train/dev.jsonl")

    print(f"\nLoading dataset from {train_file} and {dev_file}...")
    dataset = load_dataset("json", data_files={"train": train_file, "eval": dev_file})

    def formatting_prompts_func(examples):
        convos = examples["messages"]
        texts = [tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False) for convo in convos]
        return {"text": texts}

    dataset = dataset.map(formatting_prompts_func, batched=True)

    # 5. Trainer setup
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
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.bf16_supported(),
            logging_steps=5,
            evaluation_strategy="steps",
            eval_steps=15,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="cosine",
            seed=42,
            output_dir=output_dir,
            save_strategy="steps",
            save_steps=30,
            save_total_limit=2,
            report_to="none"
        ),
    )

    # 6. Train and track loss
    print("\nStarting QLoRA training...")
    trainer_stats = trainer.train()
    print("\nTraining completed successfully!")
    print(f"Final Train Loss: {trainer_stats.training_loss:.4f}")

    # 7. Save LoRA adapter
    print(f"\nSaving LoRA adapter to {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Adapter successfully saved in: {output_dir}")

    # 8. (Optional) Merge to 16-bit for vLLM deployment
    merged_output_dir = os.environ.get("MERGED_DIR", "./tinysql_merged_fp16")
    if os.environ.get("MERGE_WEIGHTS", "0") == "1":
        print(f"\nMerging LoRA weights with base model into {merged_output_dir}...")
        model.save_pretrained_merged(merged_output_dir, tokenizer, save_method="merged_16bit")
        print(f"Merged weights saved to: {merged_output_dir}")

if __name__ == "__main__":
    train()
