import sqlite3
import os

db_path = os.path.expanduser("~/.local/share/elisa/elisaDatabase.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n--- Inspecting Holst in Elisa ---")
# Check for "The Planets"
cursor.execute("SELECT Title, ArtistName, AlbumArtistName, Composer, AlbumTitle FROM Tracks WHERE AlbumTitle LIKE '%Planets%'")
rows = cursor.fetchall()
if not rows:
    print("No albums with 'Planets' found.")
else:
    for r in rows:
        print(f"Title: {r[0]}")
        print(f"Artist: {r[1]}")
        print(f"AlbumArtist: {r[2]}")
        print(f"Composer: {r[3]}")
        print(f"Album: {r[4]}")
        print("---")

print("\n--- Checking 'Gustav Holst' tokens ---")
# Simulate the query logic
tokens = ["gustav", "holst"]
columns = ["ArtistName", "AlbumArtistName", "Composer", "Title"]

def build_col_condition(col_name):
    # The new logic uses 4 variations
    token_conditions = []
    for _ in tokens:
        cond = f"({col_name} LIKE ? OR {col_name} LIKE ? OR {col_name} LIKE ? OR {col_name} LIKE ?)"
        token_conditions.append(cond)
    return f"({' AND '.join(token_conditions)})"

where_clauses = [build_col_condition(col) for col in columns]
where_sql = " OR ".join(where_clauses)
query = f"SELECT DISTINCT AlbumTitle FROM Tracks WHERE {where_sql}"

params = []
for _ in columns:
    for token in tokens:
        params.append(f"{token}")
        params.append(f"{token} %")
        params.append(f"% {token}")
        params.append(f"% {token} %")

print(f"Query: {query}")
# print(f"Params: {params}")

cursor.execute(query, tuple(params))
results = cursor.fetchall()
print("Search Results:", results)

conn.close()
