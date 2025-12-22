from game_manager import GameManager
import os
import json

USER_GAMES_FILE = os.path.expanduser("~/.config/tuxtalks/user_games.json")

def verify():
    # 1. Clean existing json if exists to test creation
    if os.path.exists(USER_GAMES_FILE):
        os.remove(USER_GAMES_FILE)
        print("🗑️ Removed existing user_games.json")
        
    # 2. Initialize GameManager (should trigger default creation)
    print("🎮 Initializing GameManager (First Run)...")
    gm = GameManager()
    
    # 3. Check if file created
    if os.path.exists(USER_GAMES_FILE):
        print("✅ SUCCESS: user_games.json created.")
        with open(USER_GAMES_FILE) as f:
            data = json.load(f)
            print(f"📄 Content: {json.dumps(data, indent=2)}")
            if len(data) >= 3:
                 print("✅ SUCCESS: Defaults saved correctly (Found 3 profiles).")
            else:
                 print("❌ FAILURE: Incorrect number of default profiles.")
    else:
        print("❌ FAILURE: user_games.json NOT created.")
        
    # 4. Test adding a profile
    print("\n➕ Simulation 'Add Game'...")
    from game_manager import X4Profile
    new_prof = X4Profile(name="Test X4 Custom", discriminator="test", default_path_override="/tmp/test.xml")
    gm.add_profile(new_prof)
    
    # 5. Reload and verify persistence
    print("\n🔄 Reloading GameManager...")
    gm2 = GameManager()
    found = gm2.get_profile_by_name("Test X4 Custom")
    if found:
        print("✅ SUCCESS: Custom profile persisted and reloaded.")
    else:
        print("❌ FAILURE: Custom profile lost on reload.")

if __name__ == "__main__":
    verify()
