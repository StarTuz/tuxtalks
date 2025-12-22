
import game_manager
import os

# Patch before creating instance
TEST_FILE = os.path.abspath("test_games.json")
game_manager.USER_GAMES_FILE = TEST_FILE

from game_manager import GameManager, GenericGameProfile

def test_persistence():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
        
    print(f"Testing with: {TEST_FILE}")

    gm = GameManager()
    # Create dummy profiles
    p1 = GenericGameProfile(name="Profile A", group="Group A")
    p2 = GenericGameProfile(name="Profile B", group="Group B")
    
    gm.profiles = [p1, p2]
    gm.active_profile = p2  # Set B as active
    
    # Save
    print(f"Saving. Active: {gm.active_profile.name}")
    gm.save_profiles()
    
    # Reload
    print("Reloading...")
    gm2 = GameManager()
    gm2.load_profiles()
    
    if os.path.exists(TEST_FILE):
        with open(TEST_FILE, 'r') as f:
            print(f"JSON Content: {f.read()}")
    
    print(f"Loaded {len(gm2.profiles)} profiles.")
    if gm2.active_profile:
        print(f"Restored Active Profile: {gm2.active_profile.name}")
        if gm2.active_profile.name == "Profile B":
            print("✅ SUCCESS: Active profile persisted.")
        else:
            print(f"❌ FAILURE: Expected Profile B, got {gm2.active_profile.name}")
    else:
        print("❌ FAILURE: No active profile restored.")

    # Cleanup
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

if __name__ == "__main__":
    test_persistence()
