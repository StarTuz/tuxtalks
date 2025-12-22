import sqlite3
import pathlib

db_path = pathlib.Path.home() / ".local" / "share" / "strawberry" / "strawberry" / "strawberry.db"

if not db_path.exists():
    print(f"DB not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "lord of the rings"
    
    print(f"--- QUERY: '{query}' ---")
    
    # Check Albums
    print("\n[ALBUMS matching query]")
    sql = "SELECT DISTINCT album FROM songs WHERE album LIKE ?"
    cursor.execute(sql, (f"%{query}%",))
    albums = cursor.fetchall()
    for a in albums:
        print(f" - {a[0]}")
        
    # Check Artists
    print("\n[ARTISTS matching query]")
    sql = "SELECT DISTINCT artist FROM songs WHERE artist LIKE ?"
    cursor.execute(sql, (f"%{query}%",))
    artists = cursor.fetchall()
    for a in artists:
        print(f" - {a[0]}")
        
    conn.close()

except Exception as e:
    print(f"Error: {e}")
