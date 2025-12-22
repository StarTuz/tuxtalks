
import json
import os

USER_GAMES_FILE = os.path.expanduser("~/.config/tuxtalks/user_games.json")

def check_active():
    if not os.path.exists(USER_GAMES_FILE):
        print(f"❌ File not found: {USER_GAMES_FILE}")
        return

    try:
        with open(USER_GAMES_FILE, 'r') as f:
            data = json.load(f)
            
        print(f"📂 Loaded {len(data)} profiles.")
        
        active_found = False
        for entry in data:
            name = entry.get('name', 'Unknown')
            is_active = entry.get('active', False)
            print(f" - {name}: Active={is_active}")
            if is_active:
                active_found = True
                
        if active_found:
            print("\n✅ Active flag IS present in JSON.")
        else:
            print("\n❌ NO profile has 'active': true flag.")
            
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")

if __name__ == "__main__":
    check_active()
