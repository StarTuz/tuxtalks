#!/usr/bin/env python3
"""
Profile Recovery Script
Scans ~/.local/share/tuxtalks/games/ and rebuilds user_games.json
"""

import os
import json
from pathlib import Path

def restore_profiles():
    """Scan game folders and rebuild profiles."""
    
    games_dir = Path.home() / ".local/share/tuxtalks/games"
    
    if not games_dir.exists():
        print(f"❌ Games directory not found: {games_dir}")
        return
    
    print(f"🔍 Scanning: {games_dir}")
    
    profiles = []
    
    # Scan all subdirectories
    for folder in sorted(games_dir.iterdir()):
        if not folder.is_dir():
            continue
        
        folder_name = folder.name.lower()
        
        # Skip temp and backup folders
        if folder_name in ['temp', '.migration_backup']:
            continue
        
        # Determine game type and variant
        profile_data = None
        
        if folder_name.startswith('elite_dangerous'):
            # Elite Dangerous profile
            variant = folder_name.replace('elite_dangerous_', '').replace('elite_dangerous', '')
            variant = variant.strip('_()').replace('_', ' ').title()
            if not variant:
                variant = "Default"
            
            name = f"Elite Dangerous ({variant})"
            group = "Elite Dangerous"
            
            profile_data = {
                "name": name,
                "group": group,
                "type": "EliteDangerous",  # ← Correct type!
                "process_name": ["EliteDangerous64.exe", "EliteDangerous.exe"],
                "bindings": {},
                "macros": []
            }
            
        elif folder_name.startswith('x4_foundations'):
            # X4 Foundations profile
            variant = folder_name.replace('x4_foundations_', '').replace('x4_foundations', '')
            variant = variant.strip('_()').replace('_', ' ').title()
            if not variant:
                variant = "Default"
            
            # Determine group from variant
            if 'gog' in variant.lower():
                group = "X4 Foundations (GOG)"
            elif 'steam native' in variant.lower():
                group = "X4 Foundations (Steam Native)"
            elif 'steam proton' in variant.lower() or 'steamapps' in variant.lower():
                group = "X4 Foundations (Steam Proton)"
            else:
                group = "X4 Foundations"
            
            name = f"{group} ({variant})"
            
            profile_data = {
                "name": name,
                "group": group,
                "type": "X4",  # ← Correct type!
                "process_name": ["X4.exe", "X4"],
                "bindings": {},
                "macros": []
            }
            
        elif folder_name.startswith('x-plane') or folder_name.startswith('xplane'):
            # X-Plane profile
            variant = folder_name.replace('x-plane_12_', '').replace('x-plane-12_', '').replace('x-plane_12', '').replace('x-plane-12', '')
            variant = variant.strip('_()').replace('_', ' ').title()
            if not variant:
                variant = "Default"
            
            name = f"X-Plane 12 ({variant})"
            group = "X-Plane 12"
            
            profile_data = {
                "name": name,
                "group": group,
                "type": "Generic",  # ← Correct type!
                "process_name": ["X-Plane", "X-Plane-x86_64"],
                "bindings": {},
                "macros": []
            }
        
        if profile_data:
            profiles.append(profile_data)
            print(f"✅ Found: {profile_data['name']}")
    
    # Save as ARRAY at root (not wrapped in "profiles" key!)
    output_file = games_dir / "user_games.json"
    
    with open(output_file, 'w') as f:
        json.dump(profiles, f, indent=2)  # ← Direct array!
    
    print(f"\n✅ Restored {len(profiles)} profiles to {output_file}")
    print("\n📋 Summary by game:")
    
    # Count by group
    groups = {}
    for p in profiles:
        group = p['group']
        groups[group] = groups.get(group, 0) + 1
    
    for group, count in sorted(groups.items()):
        print(f"  • {group}: {count} profiles")
    
    print("\n🎯 Restart TuxTalks to see all games!")

if __name__ == "__main__":
    restore_profiles()
