import sqlite3
import os

db_path = os.path.expanduser("~/.local/share/strawberry/strawberry/strawberry.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n--- Inspecting Kiri Te Kanawa ---")
cursor.execute("SELECT title, album, composer FROM songs WHERE artist LIKE '%Kiri%' OR albumartist LIKE '%Kiri%'")
rows = cursor.fetchall()
for r in rows:
    print(f"Title: {r[0]}, Album: {r[1]}, Composer: {r[2]}")

conn.close()
