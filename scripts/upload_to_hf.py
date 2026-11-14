"""
Upload TinySQL LoRA Adapter to Hugging Face Hub
"""

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADAPTER_DIR = os.path.join(BASE_DIR, "train", "tinysql_adapter")
MODEL_CARD_SRC = os.path.join(BASE_DIR, "MODEL_CARD.md")

def upload_adapter(repo_id: str, token: str = None):
    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("[ERROR] huggingface_hub is not installed. Please run:")
        print("pip install huggingface_hub")
        return

    if not os.path.exists(ADAPTER_DIR):
        print(f"[ERROR] Adapter directory not found at: {ADAPTER_DIR}")
        return

    # Check if adapter_model.safetensors exists
    weights_path = os.path.join(ADAPTER_DIR, "adapter_model.safetensors")
    if not os.path.exists(weights_path):
        print(f"[ERROR] Model weights file missing: {weights_path}")
        return

    print("=" * 60)
    print(f"Uploading TinySQL Adapter to Hugging Face Hub")
    print(f"Target Repository : {repo_id}")
    print(f"Source Folder     : {ADAPTER_DIR}")
    print("=" * 60)

    api = HfApi(token=token)

    # 1. Create repo if it doesn't exist
    try:
        create_repo(repo_id=repo_id, repo_type="model", token=token, exist_ok=True)
        print(f"✓ Repository ready: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"[WARNING] Could not create repo automatically: {e}")

    # 2. Copy MODEL_CARD.md as README.md into the adapter folder so HF displays it beautifully
    target_readme = os.path.join(ADAPTER_DIR, "README.md")
    if os.path.exists(MODEL_CARD_SRC):
        import shutil
        shutil.copyfile(MODEL_CARD_SRC, target_readme)
        print("✓ Packaged MODEL_CARD.md as repository README.md")

    # 3. Upload the folder
    print("\nUploading model weights and configs (~120 MB)... Please wait...")
    try:
        api.upload_folder(
            folder_path=ADAPTER_DIR,
            repo_id=repo_id,
            repo_type="model",
            token=token,
            commit_message="Initial release of TinySQL-3B-Olist adapter"
        )
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your model is live on Hugging Face!")
        print(f"View and share your model at:")
        print(f"👉 https://huggingface.co/{repo_id}")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Upload failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload TinySQL adapter to Hugging Face Hub")
    parser.add_argument("--repo", required=True, help="HF Repo ID in format: <username>/tinysql-3b-olist")
    parser.add_argument("--token", default=None, help="Hugging Face Write Token (hf_...)")
    args = parser.parse_args()

    upload_adapter(args.repo, token=args.token)
