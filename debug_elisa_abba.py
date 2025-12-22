import sqlite3
import os

db_path = os.path.expanduser("~/.local/share/elisa/elisaDatabase.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

errant_albums = [
    "An Ancient Muse",
    "Lovecraft And Witch Hearts",
    "MEDTNER: Sonatas Opp 22 and 25, Nos 1 and 2",
    "La Coleccionista"
]

print("\n--- Inspecting Errant ABBA Results ---")
for album in errant_albums:
    print(f"\nAlbum: {album}")
    # Get all columns for tracks in this album
    # Columns: Title, ArtistName, AlbumArtistName, Composer
    cursor.execute("SELECT Title, ArtistName, AlbumArtistName, Composer FROM Tracks WHERE AlbumTitle LIKE ?", (f"%{album}%",))
    rows = cursor.fetchall()
    if not rows:
        print("  (No tracks found in DB for this album name)")
        continue
        
    # Print first few rows to see where 'abba' might be
    for i, r in enumerate(rows):
        if i >= 5: break # Limit output
        print(f"  Title: {r[0]}")
        print(f"  Artist: {r[1]}")
        print(f"  AlbumArtist: {r[2]}")
        print(f"  Composer: {r[3]}")
        print("  ---")

conn.close()
