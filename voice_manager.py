import os
import urllib.request
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

class VoiceManager:
    # Dictionary of available voices: Name -> Base URL (without .onnx or .onnx.json)
    # Using Hugging Face URLs for Piper voices
    AVAILABLE_VOICES = {
        "en_GB-cori-high": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high",
        "en_US-lessac-high": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high",
        "en_US-amy-medium": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium",
        "en_US-danny-low": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/danny/low/en_US-danny-low",
        "en_US-ryan-medium": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium",
        "en_US-kathleen-low": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kathleen/low/en_US-kathleen-low",
    }

    def __init__(self, base_dir=None):
        if base_dir:
            self.voices_dir = Path(base_dir)
        else:
            self.voices_dir = Path.home() / ".local" / "share" / "tuxtalks" / "voices"
        
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.refresh_voices()

    def refresh_voices(self):
        """Scans the voices directory for installed voices."""
        # Start with default available voices
        self.installed_voices = []
        
        # Check what's actually on disk
        for file in self.voices_dir.glob("*.onnx"):
            voice_name = file.stem
            if voice_name not in self.installed_voices:
                self.installed_voices.append(voice_name)
        
        # Ensure defaults are in the list if they are installed
        # actually, get_available_voices should return everything that IS installed OR IS available to download
        pass

    def get_available_voices(self):
        """Returns a list of all available voice names (installed + downloadable)."""
        all_voices = set(self.AVAILABLE_VOICES.keys())
        all_voices.update(self.installed_voices)
        return sorted(list(all_voices))

    def get_voice_path(self, voice_name):
        """
        Returns the path to the .onnx file for the given voice.
        Downloads the voice if it doesn't exist.
        """
        onnx_path = self.voices_dir / f"{voice_name}.onnx"
        json_path = self.voices_dir / f"{voice_name}.onnx.json"

        if onnx_path.exists() and json_path.exists():
            return str(onnx_path)

        if voice_name in self.AVAILABLE_VOICES:
            print(f"⬇️  Downloading voice '{voice_name}'...")
            base_url = self.AVAILABLE_VOICES[voice_name]
            
            try:
                # Download .onnx
                download_url(f"{base_url}.onnx", onnx_path)
                # Download .onnx.json
                download_url(f"{base_url}.onnx.json", json_path)
                
                print(f"✅ Voice '{voice_name}' downloaded successfully.")
                self.refresh_voices()
                return str(onnx_path)
            except Exception as e:
                print(f"❌ Failed to download voice '{voice_name}': {e}")
                # Cleanup partial downloads
                if onnx_path.exists(): onnx_path.unlink()
                if json_path.exists(): json_path.unlink()
                return None
        else:
            print(f"❌ Voice '{voice_name}' not found locally or in available downloads.")
            return None

    def install_voice_from_url(self, url, name):
        """
        Installs a voice from a URL. 
        Assumes URL points to the .onnx file, and .onnx.json exists at same location + .json
        """
        onnx_path = self.voices_dir / f"{name}.onnx"
        json_path = self.voices_dir / f"{name}.onnx.json"
        
        # Handle Hugging Face "tree" or "blob" URLs
        if "huggingface.co" in url:
            if "/tree/" in url:
                url = url.replace("/tree/", "/resolve/")
            elif "/blob/" in url:
                url = url.replace("/blob/", "/resolve/")
                
            # If it's a directory URL (doesn't end in .onnx), try to guess the filename
            if not url.endswith(".onnx"):
                parts = url.rstrip("/").split("/")
                if len(parts) >= 3:
                    guessed_name = f"{parts[-3]}-{parts[-2]}-{parts[-1]}"
                    url = f"{url.rstrip('/')}/{guessed_name}.onnx"
                    print(f"ℹ️  Guessed Hugging Face URL: {url}")

        # Handle GitHub URLs
        # e.g. https://github.com/dividebysandwich/piper-voice-models/blob/main/Data/en_US-danny-low.onnx
        # -> https://raw.githubusercontent.com/dividebysandwich/piper-voice-models/main/Data/en_US-danny-low.onnx
        if "github.com" in url:
            if "/tree/" in url:
                print("❌ GitHub 'tree' URLs are directories. Please provide the link to the specific .onnx file (blob).")
                return False
            
            if "/blob/" in url:
                url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                
        # If url doesn't end in .onnx, assume it's the base name
        if url.endswith(".onnx"):
            base_url = url[:-5]
        else:
            base_url = url
            
        try:
            print(f"⬇️  Downloading custom voice '{name}'...")
            download_url(f"{base_url}.onnx", onnx_path)
            download_url(f"{base_url}.onnx.json", json_path)
            print(f"✅ Custom voice '{name}' installed.")
            self.refresh_voices()
            return True
        except Exception as e:
            print(f"❌ Failed to install custom voice: {e}")
            if onnx_path.exists(): onnx_path.unlink()
            if json_path.exists(): json_path.unlink()
            return False

    def delete_voice(self, voice_name):
        """Deletes an installed voice."""
        onnx_path = self.voices_dir / f"{voice_name}.onnx"
        json_path = self.voices_dir / f"{voice_name}.onnx.json"
        
        deleted = False
        if onnx_path.exists():
            onnx_path.unlink()
            deleted = True
        if json_path.exists():
            json_path.unlink()
            deleted = True
            
        if deleted:
            print(f"🗑️ Voice '{voice_name}' deleted.")
            self.refresh_voices()
            return True
        else:
            print(f"❌ Voice '{voice_name}' not found.")
            return False

    def install_voice_from_local(self, onnx_src, json_src, name):
        """Installs a voice from local files."""
        import shutil
        onnx_dest = self.voices_dir / f"{name}.onnx"
        json_dest = self.voices_dir / f"{name}.onnx.json"
        
        try:
            shutil.copy2(onnx_src, onnx_dest)
            shutil.copy2(json_src, json_dest)
            print(f"✅ Custom voice '{name}' imported.")
            self.refresh_voices()
            return True
        except Exception as e:
            print(f"❌ Failed to import custom voice: {e}")
            return False

if __name__ == "__main__":
    # Test
    vm = VoiceManager()
    print("Available voices:", vm.get_available_voices())
    # vm.get_voice_path("en_US-lessac-high")
