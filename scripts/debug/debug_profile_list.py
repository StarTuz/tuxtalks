import sys
import os

# Ensure local path
sys.path.insert(0, os.path.abspath("."))

try:
    from game_manager import GameManager
    
    print("Initializing GameManager...")
    gm = GameManager()
    print(f"Profiles List: {gm.profiles}")
    print(f"Count: {len(gm.profiles)}")
    
    for p in gm.profiles:
        print(f" - Profile: {p.name}")
        
    gm.initialize()
    print("Initialization complete.")
    
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
