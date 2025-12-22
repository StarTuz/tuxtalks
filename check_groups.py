
import json
import os

USER_GAMES_FILE = os.path.expanduser("~/.config/tuxtalks/user_games.json")

def check_groups():
    if not os.path.exists(USER_GAMES_FILE):
        print("❌ No user_games.json found.")
        return

    try:
        with open(USER_GAMES_FILE, 'r') as f:
            data = json.load(f)
            
        print(f"📂 Total Profiles in JSON: {len(data)}")
        
        groups = {}
        for p in data:
            g = p.get('group', 'Unknown')
            name = p.get('name', 'Unnamed')
            ptype = p.get('type', 'Unknown')
            
            if g not in groups:
                groups[g] = []
            groups[g].append(f"{name} ({ptype})")
            
        print("\n--- Detected Groups ---")
        for g, profiles in groups.items():
            print(f"Group: '{g}' ({len(profiles)} profiles)")
            for p in profiles[:3]:
                print(f"  - {p}")
            if len(profiles) > 3:
                print(f"  ... and {len(profiles)-3} more")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_groups()
