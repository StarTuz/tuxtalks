from local_library import LocalLibrary
import pathlib

# Initialize library
db_path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "library.db"
lib = LocalLibrary(db_path)

# Run query
print("Querying for 'Gustav Holst'...")
albums = lib.get_artist_albums("Gustav Holst")

print("\n--- Sorted Results ---")
for i, album in enumerate(albums):
    print(f"{i+1}. {album}")
