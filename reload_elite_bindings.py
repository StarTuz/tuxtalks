#!/usr/bin/env python3
"""
Force-reload Elite Dangerous Bindings
Fixes action mappings after profile restoration
"""

import json
import os
from pathlib import Path

# Import GameManager classes
import sys
sys.path.insert(0, '/home/startux/code/tuxtalks')
from game_manager import GameManager, EliteDangerousProfile

def reload_elite_bindings():
    """Force reload all Elite Dangerous bindings from .binds files."""
    
    print("🔄 Force-reloading Elite Dangerous bindings...")
    
    # Load GameManager (automatically loads profiles in __init__)
    gm = GameManager()
    
    print(f"📊 Total profiles loaded: {len(gm.profiles)}")
    print(f"DEBUG: Profiles type: {type(gm.profiles)}")
    print(f"DEBUG: First few profile names: {[p.name for p in gm.profiles[:3]] if gm.profiles else 'NONE'}")


    
    # Find all Elite profiles
    elite_profiles = [p for p in gm.profiles if isinstance(p, EliteDangerousProfile)]
    
    print(f"🎮 Elite Dangerous profiles found: {len(elite_profiles)}")
    
    if not elite_profiles:
        print("⚠️  No Elite Dangerous profiles found!")
        return
    
    # Reload each profile
    reloaded_count = 0
    for profile in elite_profiles:
        print(f"\n📁 Processing: {profile.name}")
        
        # Force reload bindings from file
        try:
            # Call load_bindings which will re-parse the .binds file
            profile.load_bindings()
            
            # Check if bindings were loaded
            if profile.bindings:
                print(f"   ✅ Reloaded {len(profile.bindings)} bindings")
                reloaded_count += 1
            else:
                print(f"   ⚠️  No bindings found in file")
                
            # Also reload actions to rebuild the action map
            if hasattr(profile, 'actions'):
                print(f"   ✅ Actions: {len(profile.actions)}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Save all profiles
    print(f"\n💾 Saving {reloaded_count} updated profiles...")
    gm.save_profiles()
    
    print("\n✅ Done! Elite Dangerous bindings reloaded.")
    print(f"   Profiles updated: {reloaded_count}/{len(elite_profiles)}")
    print("\n🎯 Restart TuxTalks to see the changes!")

if __name__ == "__main__":
    reload_elite_bindings()
