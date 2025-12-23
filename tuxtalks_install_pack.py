#!/usr/bin/env python3
"""
TuxTalks Pack Installer - CLI tool for installing content packs.

Usage:
    tuxtalks-admin install-pack ./pack.zip
    tuxtalks-admin install-pack https://example.com/pack.tar.gz
    tuxtalks-admin install-pack --list
"""

import sys
import os
import argparse
import zipfile
import tarfile
import shutil
import json
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None


def install_pack(source_path, packs_dir):
    """
    Install a content pack from local or remote source.
    
    Args:
        source_path: Local file path or URL to pack archive
        packs_dir: Directory to install packs to
        
    Returns:
        True if successful, False otherwise
    """
    # Check if source is URL
    is_url = source_path.startswith(('http://', 'https://'))
    
    if is_url:
        if not requests:
            print("❌ Error: 'requests' library not installed. Cannot download from URL.")
            return False
        
        print(f"📥 Downloading pack from {source_path}...")
        try:
            response = requests.get(source_path, stream=True)
            response.raise_for_status()
            
            # Save to temp file
            temp_file = os.path.join(packs_dir, '.temp_download')
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            archive_path = temp_file
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    else:
        # Local file
        archive_path = os.path.expanduser(source_path)
        if not os.path.exists(archive_path):
            print(f"❌ File not found: {archive_path}")
            return False
    
    # Create temp extraction directory
    temp_dir = os.path.join(packs_dir, '.temp_extract')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Extract archive
        print(f"📦 Extracting archive...")
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        elif archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(temp_dir)
        else:
            print(f"❌ Unsupported archive format. Use .zip or .tar.gz")
            return False
        
        # Find pack.json
        pack_json_path = None
        for root, dirs, files in os.walk(temp_dir):
            if 'pack.json' in files:
                pack_json_path = os.path.join(root, 'pack.json')
                break
        
        if not pack_json_path:
            print("❌ No pack.json found in archive.")
            print("\n💡 This might be a VoiceAttack profile or other non-LAL pack.")
            print("   To convert it for TuxTalks:")
            print("   1. Extract the archive manually")
            print("   2. Create a pack.json file (see docs/LAL_QUICKSTART.md)")
            print("   3. Organize audio files in the required structure")
            print("   4. Copy to ~/.local/share/tuxtalks/packs/")
            return False
        
        # Validate pack.json
        print("✅ Validating pack...")
        with open(pack_json_path, 'r') as f:
            metadata = json.load(f)
        
        required_fields = ['name', 'version', 'author', 'compatibility']
        for field in required_fields:
            if field not in metadata:
                print(f"❌ Missing required field in pack.json: {field}")
                return False
        
        pack_name = metadata['name']
        pack_version = metadata['version']
        pack_author = metadata.get('author', 'Unknown')
        
        # Determine target directory
        pack_dir = os.path.dirname(pack_json_path)
        target_name = pack_name.replace(' ', '_').replace('/', '_').lower()
        target_path = os.path.join(packs_dir, target_name)
        
        # Check if pack already exists
        if os.path.exists(target_path):
            print(f"⚠️  Pack '{pack_name}' already installed.")
            response = input("Overwrite? [y/N]: ").strip().lower()
            if response != 'y':
                print("❌ Installation cancelled.")
                return False
            shutil.rmtree(target_path)
        
        # Install pack
        print(f"📦 Installing pack '{pack_name}' v{pack_version}...")
        shutil.copytree(pack_dir, target_path)
        
        print(f"\n✅ Successfully installed:")
        print(f"   Name: {pack_name}")
        print(f"   Version: {pack_version}")
        print(f"   Author: {pack_author}")
        print(f"   License: {metadata.get('license', 'Not specified')}")
        print(f"   Location: {target_path}")
        print(f"\n⚠️  Reminder: Respect this pack's license terms. You are responsible for compliance.")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        if is_url and os.path.exists(temp_file):
            os.remove(temp_file)


def list_packs(packs_dir):
    """List all installed packs."""
    if not os.path.exists(packs_dir):
        print("📦 No packs installed yet.")
        return
    
    pack_dirs = [d for d in os.listdir(packs_dir) if os.path.isdir(os.path.join(packs_dir, d)) and not d.startswith('.')]
    
    if not pack_dirs:
        print("📦 No packs installed yet.")
        return
    
    print(f"\n📦 Installed Content Packs ({len(pack_dirs)}):\n")
    
    for pack_dir in sorted(pack_dirs):
        pack_path = os.path.join(packs_dir, pack_dir)
        pack_json = os.path.join(pack_path, 'pack.json')
        
        if os.path.exists(pack_json):
            try:
                with open(pack_json, 'r') as f:
                    metadata = json.load(f)
                
                name = metadata.get('name', pack_dir)
                version = metadata.get('version', 'Unknown')
                author = metadata.get('author', 'Unknown')
                games = metadata.get('compatibility', {}).get('games', [])
                
                print(f"  • {name} v{version}")
                print(f"    Author: {author}")
                print(f"    Games: {', '.join(games) if games else 'All'}")
                print()
            except:
                print(f"  • {pack_dir} (Invalid pack.json)")
                print()
        else:
            print(f"  • {pack_dir} (No pack.json)")
            print()


def main():
    """Main entry point for CLI tool."""
    parser = argparse.ArgumentParser(
        description='TuxTalks Content Pack Installer',
        epilog='Examples:\n'
               '  tuxtalks-install-pack ./my-pack.zip\n'
               '  tuxtalks-install-pack https://example.com/pack.tar.gz\n'
               '  tuxtalks-install-pack --list\n\n'
               'Legal Notice:\n'
               '  You are responsible for respecting pack licenses. Third-party content\n'
               '  may have different terms than TuxTalks (MIT). Check pack.json for license info.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('source', nargs='?', help='Pack archive (local file or URL)')
    parser.add_argument('--list', '-l', action='store_true', help='List installed packs')
    parser.add_argument('--packs-dir', default=os.path.expanduser('~/.local/share/tuxtalks/packs'),
                        help='Packs installation directory (default: ~/.local/share/tuxtalks/packs)')
    
    args = parser.parse_args()
    
    # Create packs directory if needed
    os.makedirs(args.packs_dir, exist_ok=True)
    
    if args.list:
        list_packs(args.packs_dir)
        return 0
    
    if not args.source:
        parser.print_help()
        return 1
    
    success = install_pack(args.source, args.packs_dir)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
