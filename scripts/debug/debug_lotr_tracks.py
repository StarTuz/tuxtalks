import sqlite3
import pathlib

db_path = pathlib.Path.home() / ".local" / "share" / "strawberry" / "strawberry" / "strawberry.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "lord of the rings"
    print(f"--- QUERY: '{query}' ---")
    
    # Check Titles
    print("\n[TITLES matching query]")
    sql = "SELECT title, album FROM songs WHERE title LIKE ?"
    cursor.execute(sql, (f"%{query}%",))
    rows = cursor.fetchall()
    for r in rows:
        print(f" - Song: '{r[0]}' on Album: '{r[1]}'")
        
    conn.close()

except Exception as e:
    print(f"Error: {e}")
