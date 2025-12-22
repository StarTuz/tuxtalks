import sqlite3
import os

db_path = os.path.expanduser("~/.local/share/strawberry/strawberry/strawberry.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n--- Searching for 'Williams' (broad check) ---")
# Check what artists/composers actually exist that match "Williams"
cursor.execute("SELECT DISTINCT artist FROM songs WHERE artist LIKE '%Williams%' LIMIT 10")
print("Artists matching 'Williams':", cursor.fetchall())

cursor.execute("SELECT DISTINCT composer FROM songs WHERE composer LIKE '%Williams%' LIMIT 10")
print("Composers matching 'Williams':", cursor.fetchall())

cursor.execute("SELECT DISTINCT albumartist FROM songs WHERE albumartist LIKE '%Williams%' LIMIT 10")
print("AlbumArtists matching 'Williams':", cursor.fetchall())

print("\n--- Checking 'Vaughan Williams' count in AlbumArtist ---")
cursor.execute("SELECT COUNT(*) FROM songs WHERE albumartist LIKE '%Vaughan Williams%'")
print(f"Matches in AlbumArtist: {cursor.fetchone()[0]}")

print("\n--- Sample Tracks ---")
cursor.execute("SELECT artist, albumartist, composer, album, title FROM songs LIMIT 10")
for r in cursor.fetchall():
    print(r)

conn.close()
