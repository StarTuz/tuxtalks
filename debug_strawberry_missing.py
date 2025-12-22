import sqlite3
import os

db_path = os.path.expanduser("~/.local/share/strawberry/strawberry/strawberry.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

missing_albums = [
    "Fantasies, rhapsodies and daydreams",
    "Vol. 29 - Pastoral Scenes",
    "Classic FM Hall of Fame 2014",
    "Classic Fm Hall of Fame Disk 3"
]

print("\n--- Inspecting Missing Albums ---")
for album in missing_albums:
    print(f"\nAlbum: {album}")
    # Get all columns for tracks in this album
    cursor.execute("SELECT title, artist, composer, albumartist, performer, grouping, comment FROM songs WHERE album LIKE ?", (f"%{album}%",))
    rows = cursor.fetchall()
    if not rows:
        print("  (No tracks found in DB for this album name)")
        continue
        
    for r in rows:
        print(f"  Title: {r[0]}")
        print(f"  Artist: {r[1]}")
        print(f"  Composer: {r[2]}")
        print(f"  AlbumArtist: {r[3]}")
        print(f"  Performer: {r[4]}")
        print(f"  Grouping: {r[5]}")
        print(f"  Comment: {r[6]}")
        print("  ---")

conn.close()
