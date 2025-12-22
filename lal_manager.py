"""
Licensed Asset Loader (LAL) - Manages third-party content packs for TuxTalks.

Provides an open directory structure for developers to distribute audio assets
and macro packs. Supports multiple installation methods:
- Custom installers (HCS VoicePacks)
- GitHub repositories
- Manual installation
- Optional GUI helper

Directory: ~/.local/share/tuxtalks/packs/{pack_name}/
"""

import os
import json
from pathlib import Path


class LALManager:
    """Licensed Asset Loader - Third-party content pack manager."""
    
    PACKS_DIR = os.path.expanduser("~/.local/share/tuxtalks/packs")
    
    # Validation limits
    MAX_AUDIO_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_MACRO_FILE_SIZE = 1 * 1024 * 1024    # 1MB
    MAX_TOTAL_PACK_SIZE = 500 * 1024 * 1024  # 500MB
    
    SUPPORTED_AUDIO_FORMATS = ['.wav', '.ogg', '.mp3', '.flac']
    
    def __init__(self):
        self.packs = {}  # pack_name -> PackInfo
        self._ensure_packs_dir()
        self.load_all_packs()
    
    def _ensure_packs_dir(self):
        """Create packs directory if it doesn't exist."""
        if not os.path.exists(self.PACKS_DIR):
            os.makedirs(self.PACKS_DIR, exist_ok=True)
            print(f"✅ Created packs directory: {self.PACKS_DIR}")
    
    def load_all_packs(self):
        """Scan and load all installed packs."""
        if not os.path.exists(self.PACKS_DIR):
            return
        
        loaded_count = 0
        for pack_name in os.listdir(self.PACKS_DIR):
            pack_path = os.path.join(self.PACKS_DIR, pack_name)
            
            # Only process directories
            if not os.path.isdir(pack_path):
                continue
            
            # Check for pack.json
            metadata_file = os.path.join(pack_path, "pack.json")
            if os.path.exists(metadata_file):
                if self.load_pack(pack_path):
                    loaded_count += 1
        
        if loaded_count > 0:
            print(f"📦 Loaded {loaded_count} content pack(s)")
    
    def load_pack(self, pack_path):
        """Load and validate a single pack."""
        try:
            metadata_file = os.path.join(pack_path, "pack.json")
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Validate schema
            validation_result = self.validate_pack_metadata(metadata, pack_path)
            if not validation_result['valid']:
                print(f"⚠️ Invalid pack at {pack_path}: {validation_result['error']}")
                return False
            
            # Load audio index if present
            audio_index = self.load_audio_index(pack_path, metadata)
            
            # Load macros
            macros = self.load_pack_macros(pack_path, metadata)
            
            # Create pack info
            pack_info = PackInfo(
                path=pack_path,
                metadata=metadata,
                audio_index=audio_index,
                macros=macros
            )
            
            # Store by pack name
            pack_name = metadata['name']
            self.packs[pack_name] = pack_info
            
            print(f"✅ Loaded pack: {pack_name} v{metadata.get('version', '1.0.0')}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {pack_path}/pack.json: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to load pack {pack_path}: {e}")
            return False
    
    def validate_pack_metadata(self, metadata, pack_path):
        """Validate pack.json schema and security."""
        # Required fields
        required_fields = ['name', 'version', 'author', 'compatibility']
        for field in required_fields:
            if field not in metadata:
                return {'valid': False, 'error': f"Missing required field: {field}"}
        
        # Validate version compatibility
        compatibility = metadata.get('compatibility', {})
        tuxtalks_version = compatibility.get('tuxtalks_version')
        if not tuxtalks_version:
            return {'valid': False, 'error': "Missing tuxtalks_version in compatibility"}
        
        # Check pack size
        pack_size = self._calculate_directory_size(pack_path)
        if pack_size > self.MAX_TOTAL_PACK_SIZE:
            return {'valid': False, 'error': f"Pack size {pack_size} exceeds limit"}
        
        # Check for executable files (security)
        if self._contains_executables(pack_path):
            return {'valid': False, 'error': "Pack contains executable files (.exe, .sh, .py)"}
        
        return {'valid': True}
    
    def _calculate_directory_size(self, path):
        """Calculate total size of directory."""
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except OSError:
                    pass
        return total
    
    def _contains_executables(self, path):
        """Check if directory contains executable files."""
        dangerous_extensions = ['.exe', '.sh', '.py', '.bat', '.cmd']
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in dangerous_extensions:
                    return True
        return False
    
    def load_audio_index(self, pack_path, metadata):
        """Load audio index from pack."""
        audio_index = {}
        
        content = metadata.get('content', {})
        audio_info = content.get('audio', {})
        index_file = audio_info.get('index_file')
        
        if not index_file:
            return audio_index
        
        index_path = os.path.join(pack_path, index_file)
        if not os.path.exists(index_path):
            print(f"⚠️ Audio index not found: {index_path}")
            return audio_index
        
        try:
            with open(index_path, 'r') as f:
                index_data = json.load(f)
            
            # Flatten categories into single audio_id -> file mapping
            categories = index_data.get('categories', {})
            for category, items in categories.items():
                for item in items:
                    audio_id = item.get('id')
                    filename = item.get('file')
                    
                    if audio_id and filename:
                        # Validate file exists and size
                        audio_path = os.path.join(pack_path, os.path.dirname(index_file), filename)
                        if os.path.exists(audio_path):
                            file_size = os.path.getsize(audio_path)
                            if file_size <= self.MAX_AUDIO_FILE_SIZE:
                                audio_index[audio_id] = {
                                    'file': os.path.join(os.path.dirname(index_file), filename),
                                    'tags': item.get('tags', [])
                                }
                            else:
                                print(f"⚠️ Audio file too large: {filename} ({file_size} bytes)")
            
            return audio_index
            
        except Exception as e:
            print(f"⚠️ Failed to load audio index: {e}")
            return {}
    
    def load_pack_macros(self, pack_path, metadata):
        """Load macros from pack."""
        all_macros = {}
        
        content = metadata.get('content', {})
        macro_files = content.get('macros', [])
        
        for macro_file in macro_files:
            macro_path = os.path.join(pack_path, macro_file)
            
            if not os.path.exists(macro_path):
                print(f"⚠️ Macro file not found: {macro_path}")
                continue
            
            # Check file size
            file_size = os.path.getsize(macro_path)
            if file_size > self.MAX_MACRO_FILE_SIZE:
                print(f"⚠️ Macro file too large: {macro_file}")
                continue
            
            try:
                with open(macro_path, 'r') as f:
                    macro_data = json.load(f)
                
                # Extract macros
                macros = macro_data.get('macros', {})
                game_type = macro_data.get('game_type', 'Generic')
                
                for macro_name, macro_def in macros.items():
                    # Add game_type to macro
                    macro_def['game_type'] = game_type
                    macro_def['source_pack'] = metadata['name']
                    all_macros[macro_name] = macro_def
                
            except Exception as e:
                print(f"⚠️ Failed to load macros from {macro_file}: {e}")
        
        return all_macros
    
    def get_audio(self, audio_id, profile_type=None):
        """Find audio file by ID, optionally filtered by game type."""
        for pack_name, pack in self.packs.items():
            # Filter by game type if specified
            if profile_type:
                games = pack.metadata.get('compatibility', {}).get('games', [])
                if profile_type not in games:
                    continue
            
            # Check if audio exists in this pack
            if audio_id in pack.audio_index:
                audio_info = pack.audio_index[audio_id]
                audio_path = os.path.join(pack.path, audio_info['file'])
                
                if os.path.exists(audio_path):
                    return audio_path
        
        return None
    
    def get_macros_for_game(self, game_type):
        """Get all macros compatible with a specific game type."""
        compatible_macros = {}
        
        for pack_name, pack in self.packs.items():
            games = pack.metadata.get('compatibility', {}).get('games', [])
            
            if game_type in games:
                for macro_name, macro_def in pack.macros.items():
                    if macro_def.get('game_type') == game_type:
                        compatible_macros[macro_name] = macro_def
        
        return compatible_macros
    
    def list_packs(self):
        """List all installed packs."""
        return [
            {
                'name': pack.metadata['name'],
                'version': pack.metadata.get('version', '1.0.0'),
                'author': pack.metadata.get('author', 'Unknown'),
                'games': pack.metadata.get('compatibility', {}).get('games', []),
                'audio_count': len(pack.audio_index),
                'macro_count': len(pack.macros)
            }
            for pack in self.packs.values()
        ]


class PackInfo:
    """Container for loaded pack information."""
    
    def __init__(self, path, metadata, audio_index, macros):
        self.path = path
        self.metadata = metadata
        self.audio_index = audio_index  # audio_id -> file_info
        self.macros = macros              # macro_name -> macro_def
    
    def get_macros_for_game(self, game_name):
        """
        Get macros from this pack applicable to the given game.
        
        Args:
            game_name: Game name (e.g., "Elite Dangerous")
            
        Returns:
            dict: {macro_name: macro_data}
        """
        # Check game compatibility
        compatible_games = self.metadata.get('compatibility', {}).get('games', [])
        
        # If pack specifies games and this game isn't listed, return empty
        if compatible_games and game_name not in compatible_games:
            return {}
        
        # Return all macros (already filtered by compatibility)
        return self.macros.copy()
