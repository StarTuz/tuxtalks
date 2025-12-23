import sqlite3
import pathlib
import os

db_path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "library.db"

if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Opening database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n--- Searching for 'CHRISTMAS CAROLS' ---")
    cursor.execute("SELECT path, title, artist, album, composer FROM tracks WHERE album LIKE '%CHRISTMAS CAROLS%'")
    rows = cursor.fetchall()
    for row in rows:
        path_blob, title, artist, album, composer = row
        try:
            path = path_blob.decode('utf-8', 'surrogateescape')
        except:
            path = str(path_blob)
        print(f"Path: {path}")
        print(f"  Title: {title}")
        print(f"  Artist: {artist}")
        print(f"  Album: {album}")
        print(f"  Composer: {composer}")
        print("-" * 20)

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
