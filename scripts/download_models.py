import os
import urllib.request
import time

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "models")
os.makedirs(MODEL_DIR, exist_ok=True)
model_path = os.path.join(MODEL_DIR, "lama.onnx")

def download_lama_real():
    print("Downloading REAL LaMa ONNX model weights (approx 190MB)...")
    
    # Hugging Face direct resolve link using a public fork that has no auth wrappers
    url = "https://huggingface.co/any-file/lama-cleaner/resolve/main/lama_1.onnx"
    # Alternative direct release link from the original repo
    url_alt = "https://github.com/Sanster/models/releases/download/add_tf_models/lama_1.onnx"
    
    try:
        urllib.request.urlretrieve(url_alt, model_path)
        print(f"Successfully downloaded to {model_path}")
    except Exception as e:
        print(f"Direct download failed: {e}. ")
        print("Model must be downloaded manually or injected via GUI.")

if __name__ == "__main__":
    download_lama_real()
