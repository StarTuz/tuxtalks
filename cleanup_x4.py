import json
import os

path = os.path.expanduser("~/.config/tuxtalks/user_games.json")
if not os.path.exists(path):
    print("No file found.")
    exit()

with open(path, 'r') as f:
    data = json.load(f)

# Filter out corrupted X4 Proton profiles
# User asked to delete "Game: X4 Foundation (Steam Proton)"
# We will remove all profiles belonging to that group.
# Also check for exact name match just in case
new_data = [p for p in data if p.get("group") != "X4 Foundations (Steam Proton)" and p.get("name") != "X4 Foundations (Steam Proton)"]

removed_count = len(data) - len(new_data)
print(f"Removed {removed_count} corrupted profiles.")

with open(path, 'w') as f:
    json.dump(new_data, f, indent=4)
