import json
import os

path = os.path.expanduser("~/.config/tuxtalks/user_games.json")
if not os.path.exists(path):
    print("No file found.")
    exit()

with open(path, 'r') as f:
    data = json.load(f)

# Filter out X4 GOG profiles
initial_count = len(data)
new_data = [p for p in data if p.get("group") != "X4 Foundations (GOG)"]
removed_count = initial_count - len(new_data)

print(f"Removed {removed_count} profiles for group 'X4 Foundations (GOG)'.")

with open(path, 'w') as f:
    json.dump(new_data, f, indent=4)
