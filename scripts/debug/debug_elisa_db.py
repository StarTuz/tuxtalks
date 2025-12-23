import sqlite3
import os

db_path = os.path.expanduser("~/.local/share/elisa/elisaDatabase.db")
print(f"Checking Elisa DB at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\nTables:", tables)
    
    for table in tables:
        table_name = table[0]
        print(f"\n--- Schema for {table_name} ---")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
            
    # Sample data from likely tables
    likely_tables = ["Tracks", "Albums", "Artists", "FileScanner"] # Guessing names
    
    # Check if we have a 'Tracks' or similar table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%Track%'")
    track_tables = cursor.fetchall()
    if track_tables:
        t_name = track_tables[0][0]
        print(f"\n--- Sample data from {t_name} ---")
        cursor.execute(f"SELECT * FROM {t_name} LIMIT 5")
        for row in cursor.fetchall():
            print(row)

    conn.close()

except Exception as e:
    print(f"Error: {e}")
