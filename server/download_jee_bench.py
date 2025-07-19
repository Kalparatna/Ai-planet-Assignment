import os
import json
import requests
from huggingface_hub import hf_hub_download

# Constants
DATASET_REPO = "JEE-Bench/JEE-Bench"
DATASET_FILE = "JEE-Bench.json"

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

def download_jee_bench():
    """Download the JEE Bench dataset using Hugging Face Hub"""
    print("Downloading JEE Bench dataset from Hugging Face Hub...")
    try:
        # Download the file using huggingface_hub
        file_path = hf_hub_download(repo_id=DATASET_REPO, filename=DATASET_FILE)
        
        # Copy the file to our data directory
        with open(file_path, "r") as src, open("data/jee_bench.json", "w") as dst:
            dst.write(src.read())
        print("Download complete!")
        print(f"File size: {os.path.getsize('data/jee_bench.json')} bytes")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return None
    
    # Verify the file is valid JSON
    try:
        with open("data/jee_bench.json", "r") as f:
            data = json.load(f)
        print(f"Successfully loaded JSON data with {len(data)} entries")
        return data
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {e}")
        return None

if __name__ == "__main__":
    download_jee_bench()