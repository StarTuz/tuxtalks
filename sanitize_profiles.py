
import json
import os

USER_GAMES_FILE = os.path.expanduser("~/.config/tuxtalks/user_games.json")

def sanitize():
    print("🧹 Sanitizing user_games.json...")
    
    if not os.path.exists(USER_GAMES_FILE):
        print("❌ File not found.")
        return

    try:
        with open(USER_GAMES_FILE, 'r') as f:
            data = json.load(f)
            
        cleaned_data = []
        seen = set()
        
        for p in data:
            # 1. Fix Process Name (List -> String)
            if isinstance(p.get('process_name'), list):
                 # Take the first item (usually the valid exe)
                 p['process_name'] = p['process_name'][0]
                 print(f"   - Fixed process_name for {p['name']}: {p['process_name']}")
                 
            # 2. Fix Group Names (Standardize)
            # User hated standardization, so we KEEP what is there, but maybe clean specific duplicates
            
            # 3. Deduplicate by Name+Group
            uid = f"{p.get('group')}|{p.get('name')}"
            
            # Explicit user request: Delete "Elite Dangerous (Wine)"
            if "Wine" in p.get('name', ''):
                 print(f"   - Removing unwanted profile: {p['name']}")
                 continue
                 
            if uid in seen:
                 print(f"   - Removed duplicate: {uid}")
                 continue
            seen.add(uid)
            
            cleaned_data.append(p)
            
        # Refix Active State (Ensure exact one is active)
        # If multiple active, keep last?
        
        with open(USER_GAMES_FILE, 'w') as f:
            json.dump(cleaned_data, f, indent=4)
            
        print(f"✅ Sanitization Complete. {len(cleaned_data)} profiles saved.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sanitize()
