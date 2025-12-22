import sqlite3
import os

db_path = os.path.expanduser("~/.local/share/strawberry/strawberry/strawberry.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

missing_albums = [
    "World In Union",
    "Holst: The Planets, Op. 32"
]

print("\n--- Inspecting Missing Holst Albums ---")
for album in missing_albums:
    print(f"\nAlbum: {album}")
    # Get all columns for tracks in this album
    cursor.execute("SELECT title, artist, composer, albumartist, performer FROM songs WHERE album LIKE ?", (f"%{album}%",))
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
        print("  ---")

print("\n--- Checking 'Gustav Holst' vs 'Holst' ---")
cursor.execute("SELECT count(*) FROM songs WHERE composer LIKE '%Gustav Holst%'")
print(f"Matches for 'Gustav Holst' in composer: {cursor.fetchone()[0]}")

cursor.execute("SELECT count(*) FROM songs WHERE composer LIKE '%Holst%' AND composer NOT LIKE '%Gustav Holst%'")
print(f"Matches for 'Holst' (but not Gustav) in composer: {cursor.fetchone()[0]}")

conn.close()
