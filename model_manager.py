import os
import sys
import zipfile
import urllib.request
import shutil
from pathlib import Path
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)

def download_and_extract_model(url, dest_path):
    """
    Downloads a zip file from url and extracts it to dest_path.
    """
    dest_path = Path(dest_path)
    zip_name = "model.zip"
    
    # Create parent dir if needed
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"⬇️  Downloading model from {url}...")
    try:
        download_url(url, zip_name)
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

    print("📦 Extracting model...")
    try:
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            # Extract to parent of dest_path because zip usually contains a folder
            # But we need to handle if the zip contains the folder or just files
            # For Vosk models, they usually contain a folder named like the zip
            
            # Let's extract to a temp dir first
            temp_extract_dir = Path("temp_extract")
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            temp_extract_dir.mkdir()
            
            zip_ref.extractall(temp_extract_dir)
            
            # Find the model folder (should be the only child)
            children = list(temp_extract_dir.iterdir())
            if len(children) == 1 and children[0].is_dir():
                model_dir = children[0]
            else:
                # If multiple files, maybe the zip IS the model dir
                model_dir = temp_extract_dir
            
            # Move to dest_path
            if dest_path.exists():
                shutil.rmtree(dest_path)
            
            shutil.move(str(model_dir), str(dest_path))
            
            # Cleanup
            shutil.rmtree(temp_extract_dir)
        
        os.remove(zip_name)
        print("✅ Model setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        if os.path.exists(zip_name):
            os.remove(zip_name)
        return False

def setup_vosk_model(model_path_str):
    """
    Checks if the Vosk model exists. If not, downloads and extracts it.
    Returns the path to the model.
    """
    model_path = Path(model_path_str)
    
    # If model exists, we're good
    if model_path.exists():
        return True

    print(f"⚠️  Vosk model not found at: {model_path}")
    print("   This is required for offline voice recognition.")
    
    # Define model URL (using the lgraph model we chose)
    MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip"
    
    # Ask user permission
    print(f"   Do you want to download the default model now? (~128MB)")
    response = input("   [Y/n]: ").strip().lower()
    
    if response in ['n', 'no']:
        print("❌ Model download cancelled. The assistant cannot run without it.")
        return False

    return download_and_extract_model(MODEL_URL, model_path)

def get_available_models(base_dir=None):
    """
    Returns a list of available Vosk model paths in the base directory.
    """
    if base_dir is None:
        base_dir = Path.home() / ".local" / "share" / "tuxtalks" / "models"
    else:
        base_dir = Path(base_dir)
        
    if not base_dir.exists():
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"❌ Failed to create model directory: {e}")
            return []
        return []
        
    models = []
    for item in base_dir.iterdir():
        if item.is_dir():
            # Check if it looks like a model (has conf/model.conf or is named vosk-model*)
            if (item / "conf" / "model.conf").exists() or item.name.startswith("vosk-model"):
                models.append(str(item))
                
    return sorted(models)

def delete_model(model_path):
    """Deletes a model directory."""
    path = Path(model_path)
    if not path.exists():
        print(f"❌ Model path not found: {model_path}")
        return False
        
    try:
        import shutil
        shutil.rmtree(path)
        print(f"🗑️ Model deleted: {model_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to delete model: {e}")
        return False

if __name__ == "__main__":
    # Test run
    # setup_vosk_model("vosk-model-en-us-0.22-lgraph")
    pass
