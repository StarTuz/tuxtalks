"""
TuxTalks Data Migration Script

Migrates games data from flat structure to hierarchical per-game subdirectories.

Usage:
    tuxtalks-admin migrate data --dry-run    # Preview changes
    tuxtalks-admin migrate data --backup     # Backup + migrate
    tuxtalks-admin migrate data --rollback   # Undo migration
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

GAMES_DIR = os.path.expanduser("~/.local/share/tuxtalks/games")
BACKUP_DIR = os.path.expanduser("~/.local/share/tuxtalks/.migration_backup")
MIGRATION_LOG = os.path.expanduser("~/.config/tuxtalks/migration.json")


def parse_game_name(filename):
    """Extract game name from flat structure filename."""
    # Remove file extension
    name = filename.replace('.json', '').replace('.bak', '')
    
    # Remove suffixes like _commands, _macros, _config
    for suffix in ['_commands', '_macros', '_config']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    
    return name


def detect_flat_files():
    """Detect all files in flat structure."""
    if not os.path.exists(GAMES_DIR):
        return []
    
    flat_files = []
    for item in os.listdir(GAMES_DIR):
        path = os.path.join(GAMES_DIR, item)
        
        # Skip if it's already a directory (hierarchical structure)
        if os.path.isdir(path):
            continue
        
        # Only JSON files and backups
        if item.endswith('.json') or item.endswith('.json.bak'):
            flat_files.append(item)
    
    return flat_files


def group_files_by_game(flat_files):
    """Group flat files by game name."""
    games = {}
    
    for filename in flat_files:
        game_name = parse_game_name(filename)
        
        if game_name not in games:
            games[game_name] = []
        
        games[game_name].append(filename)
    
    return games


def create_migration_plan(games):
    """Create detailed migration plan."""
    plan = {}
    
    for game_name, files in games.items():
        game_dir = os.path.join(GAMES_DIR, game_name)
        macros_dir = os.path.join(game_dir, "macros")
        backups_dir = os.path.join(game_dir, ".backups")
        
        plan[game_name] = {
            "directories": [game_dir, macros_dir, backups_dir],
            "migrations": []
        }
        
        for filename in files:
            old_path = os.path.join(GAMES_DIR, filename)
            
            # Determine new path
            if filename.endswith('.bak'):
                # Backup files go to .backups/
                new_filename = filename.replace(f'{game_name}_', '')
                new_path = os.path.join(backups_dir, new_filename)
            elif '_commands.json' in filename:
                new_path = os.path.join(game_dir, "commands.json")
            elif '_macros.json' in filename:
                # Legacy single macro file goes to macros/default.json
                new_path = os.path.join(macros_dir, "default.json")
            elif '_config.json' in filename:
                new_path = os.path.join(game_dir, "config.json")
            else:
                # Unknown file, put in game root
                new_filename = filename.replace(f'{game_name}_', '')
                new_path = os.path.join(game_dir, new_filename)
            
            plan[game_name]["migrations"].append({
                "old": old_path,
                "new": new_path
            })
    
    return plan


def print_plan(plan):
    """Print migration plan in human-readable format."""
    print("\n📦 Migration Plan Preview\n")
    print("=" * 70)
    
    for game_name, details in plan.items():
        print(f"\n🎮 {game_name.replace('_', ' ').title()}")
        print(f"   Creating directories:")
        for dir_path in details["directories"]:
            print(f"     ✓ {dir_path}")
        
        print(f"   Migrating files:")
        for migration in details["migrations"]:
            print(f"     • {os.path.basename(migration['old'])}")
            print(f"       → {migration['new'].replace(GAMES_DIR + '/', '')}")
    
    print("\n" + "=" * 70)
    
    total_files = sum(len(d["migrations"]) for d in plan.values())
    print(f"\nTotal: {len(plan)} games, {total_files} files\n")


def backup_flat_structure():
    """Create backup of entire flat structure."""
    if not os.path.exists(GAMES_DIR):
        return False
    
    print(f"📦 Creating backup at {BACKUP_DIR}...")
    
    # Remove old backup if exists
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    
    # Create backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    for item in os.listdir(GAMES_DIR):
        src = os.path.join(GAMES_DIR, item)
        dst = os.path.join(BACKUP_DIR, item)
        
        if os.path.isfile(src):
            shutil.copy2(src, dst)
    
    print("✅ Backup created successfully")
    return True


def execute_migration(plan):
    """Execute the migration plan."""
    print("\n🚀 Executing migration...\n")
    
    for game_name, details in plan.items():
        print(f"🎮 {game_name.replace('_', ' ').title()}")
        
        # Create directories
        for dir_path in details["directories"]:
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✓ Created {os.path.basename(dir_path)}/")
        
        # Move files
        for migration in details["migrations"]:
            shutil.move(migration["old"], migration["new"])
            print(f"   ✓ Moved {os.path.basename(migration['old'])}")
    
    # Log migration
    log_migration(plan)
    
    print("\n✅ Migration completed successfully!\n")


def log_migration(plan):
    """Log migration details for rollback."""
    os.makedirs(os.path.dirname(MIGRATION_LOG), exist_ok=True)
    
    log_data = {
        "date": datetime.now().isoformat(),
        "backup_location": BACKUP_DIR,
        "migrated_games": list(plan.keys()),
        "total_files": sum(len(d["migrations"]) for d in plan.values())
    }
    
    with open(MIGRATION_LOG, 'w') as f:
        json.dump(log_data, f, indent=2)


def rollback_migration():
    """Rollback to flat structure from backup."""
    if not os.path.exists(BACKUP_DIR):
        print("❌ No backup found. Cannot rollback.")
        return False
    
    if not os.path.exists(MIGRATION_LOG):
        print("❌ No migration log found. Cannot rollback.")
        return False
    
    print("🔄 Rolling back migration...\n")
    
    # Remove hierarchical structure
    for item in os.listdir(GAMES_DIR):
        path = os.path.join(GAMES_DIR, item)
        if os.path.isdir(path):
            print(f"   ✓ Removing {item}/")
            shutil.rmtree(path)
    
    # Restore flat files
    for item in os.listdir(BACKUP_DIR):
        src = os.path.join(BACKUP_DIR, item)
        dst = os.path.join(GAMES_DIR, item)
        shutil.copy2(src, dst)
        print(f"   ✓ Restored {item}")
    
    # Remove backup and log
    shutil.rmtree(BACKUP_DIR)
    os.remove(MIGRATION_LOG)
    
    print("\n✅ Rollback completed successfully!\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Migrate TuxTalks games data to hierarchical structure")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without executing")
    parser.add_argument("--backup", action="store_true", help="Create backup before migration")
    parser.add_argument("--rollback", action="store_true", help="Rollback to flat structure")
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration()
        return
    
    # Detect flat files
    flat_files = detect_flat_files()
    
    if not flat_files:
        print("✅ No flat structure files found. Already migrated or nothing to migrate.")
        return
    
    # Group by game
    games = group_files_by_game(flat_files)
    
    # Create migration plan
    plan = create_migration_plan(games)
    
    # Print plan
    print_plan(plan)
    
    if args.dry_run:
        print("ℹ️  Dry run complete. No changes made.")
        print("   Run without --dry-run to execute migration.")
        return
    
    # Confirm with user
    response = input("Proceed with migration? [y/N]: ")
    if response.lower() != 'y':
        print("❌ Migration cancelled.")
        return
    
    # Backup if requested
    if args.backup:
        backup_flat_structure()
    
    # Execute migration
    execute_migration(plan)


if __name__ == "__main__":
    main()
