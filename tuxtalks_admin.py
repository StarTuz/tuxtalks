#!/usr/bin/env python3
"""
TuxTalks Administrative Toolbox
Consolidates maintenance and utility tasks into a single command.
"""

import sys
import argparse
import importlib

def main():
    parser = argparse.ArgumentParser(
        description="TuxTalks Administrative Toolbox",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Administrative commands")
    
    # 1. Install Pack
    parser_install = subparsers.add_parser("install-pack", help="Install a TuxTalks content pack (.talkpack)")
    parser_install.add_argument("source", help="Pack archive (local file or URL)")
    parser_install.add_argument("--list", "-l", action="store_true", help="List installed packs")
    
    # 2. Migrate
    parser_migrate = subparsers.add_parser("migrate", help="Migrate configuration and data from older versions")
    parser_migrate.add_argument("type", choices=["data", "corrections", "all"], help="Type of migration to perform")
    parser_migrate.add_argument("--dry-run", action="store_true", help="Preview changes without applying (data only)")
    parser_migrate.add_argument("--backup", action="store_true", help="Create backup before migration")
    parser_migrate.add_argument("--rollback", action="store_true", help="Undo previous data migration")

    args = parser.parse_args()

    if args.command == "install-pack":
        import tuxtalks_install_pack
        sys.argv = ["tuxtalks-install-pack"]
        if args.list:
            sys.argv.append("--list")
        if args.source:
            sys.argv.append(args.source)
        return tuxtalks_install_pack.main()

    elif args.command == "migrate":
        if args.type in ["data", "all"]:
            import migrate_games_data
            print("--- Starting Data Migration ---")
            sys.argv = ["migrate_games_data.py"]
            if args.dry_run: sys.argv.append("--dry-run")
            if args.backup: sys.argv.append("--backup")
            if args.rollback: sys.argv.append("--rollback")
            migrate_games_data.main()
            
        if args.type in ["corrections", "all"]:
            import tuxtalks_migrate_corrections
            print("\n--- Starting Corrections Migration ---")
            # corrections tool doesn't use argparse currently, just main()
            tuxtalks_migrate_corrections.main()
        return 0

    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
