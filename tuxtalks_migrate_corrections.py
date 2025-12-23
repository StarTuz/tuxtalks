#!/usr/bin/env python3
"""
TuxTalks Corrections Migration Tool

Migrates VOICE_CORRECTIONS and CUSTOM_VOCABULARY from config.json
to appropriate files:
- personal_corrections.json (music artists, personal terms)
- Game profile configs (game-specific terms)
- config.json cleaned (settings only)

Usage:
    tuxtalks-admin migrate corrections
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# Elite Dangerous keywords
ELITE_KEYWORDS = [
    "gear", "landing", "hardpoint", "heat sink", "chaff", "shield cell",
    "jump", "fsd", "frame shift", "supercruise", "hyperspace",
    "target", "enemy", "hostile", "wingman", "fighter",
    "cargo", "scoop", "docking", "lights", "night vision",
    "silent running", "flight assist", "orbital", "rotational",
    "boost", "scanner", "speed", "galaxy map", "system map",
    "codex", "squadron"
]

# Game mode keywords
GAME_MODE_KEYWORDS = [
    "game mode", "enable game", "disable game", "game modes"
]

# Player switching keywords  
PLAYER_KEYWORDS = [
    "jay river", "jriver", "strawberry", "elisa", "vlc", "mpris",
    "switch player", "change player", "use player", "player to"
]


def categorize_correction(key: str, value: str) -> str:
    """
    Categorize a correction into: 'elite', 'game_mode', 'player', or 'personal'
    
    Returns:
        Category string
    """
    key_lower = key.lower()
    value_lower = value.lower()
    combined = f"{key_lower} {value_lower}"
    
    # Elite Dangerous
    if any(kw in combined for kw in ELITE_KEYWORDS):
        return "elite"
    
    # Game mode
    if any(kw in combined for kw in GAME_MODE_KEYWORDS):
        return "game_mode"
    
    # Player switching
    if any(kw in combined for kw in PLAYER_KEYWORDS):
        return "player"
    
    # Personal (music, artists, etc.)
    return "personal"


def categorize_vocabulary(term: str) -> str:
    """Categorize a vocabulary term"""
    term_lower = term.lower()
    
    # Elite Dangerous
    if any(kw in term_lower for kw in ELITE_KEYWORDS):
        return "elite"
    
    return "personal"


def migrate_corrections():
    """Main migration function"""
    
    logger.info("=" * 60)
    logger.info("TuxTalks Corrections Migration Tool")
    logger.info("=" * 60)
    
    # Load config.json
    config_file = Path.home() / ".config/tuxtalks/config.json"
    
    if not config_file.exists():
        logger.error(f"Config file not found: {config_file}")
        return
    
    logger.info(f"Loading config from: {config_file}")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    corrections = config.get("VOICE_CORRECTIONS", {})
    vocabulary = config.get("CUSTOM_VOCABULARY", [])
    
    logger.info(f"Found {len(corrections)} corrections and {len(vocabulary)} vocabulary terms")
    
    if not corrections and not vocabulary:
        logger.info("No corrections or vocabulary to migrate!")
        return
    
    # Categorize corrections
    elite_corrections = {}
    game_mode_corrections = {}
    player_corrections = {}
    personal_corrections = {}
    
    logger.info("\nCategorizing corrections...")
    for key, value in corrections.items():
        category = categorize_correction(key, value)
        
        if category == "elite":
            elite_corrections[key] = value
        elif category == "game_mode":
            game_mode_corrections[key] = value
        elif category == "player":
            player_corrections[key] = value
        else:
            personal_corrections[key] = value
    
    # Categorize vocabulary
    elite_vocab = []
    personal_vocab = []
    
    for term in vocabulary:
        if categorize_vocabulary(term) == "elite":
            elite_vocab.append(term)
        else:
            personal_vocab.append(term)
    
    # Print categorization results
    logger.info("\n" + "=" * 60)
    logger.info("Categorization Results:")
    logger.info("=" * 60)
    logger.info(f"  Elite Dangerous: {len(elite_corrections)} corrections, {len(elite_vocab)} vocabulary")
    logger.info(f"  Game Mode: {len(game_mode_corrections)} corrections")
    logger.info(f"  Player Switching: {len(player_corrections)} corrections")
    logger.info(f"  Personal: {len(personal_corrections)} corrections, {len(personal_vocab)} vocabulary")
    
    # Backup original config
    backup_file = config_file.parent / f"config.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"\nCreating backup: {backup_file}")
    shutil.copy2(config_file, backup_file)
    
    # Create personal_corrections.json
    if personal_corrections or personal_vocab:
        personal_file = Path.home() / ".local/share/tuxtalks/personal_corrections.json"
        personal_file.parent.mkdir(parents=True, exist_ok=True)
        
        personal_data = {
            "VOICE_CORRECTIONS": personal_corrections,
            "CUSTOM_VOCABULARY": personal_vocab
        }
        
        logger.info(f"\nWriting personal corrections: {personal_file}")
        with open(personal_file, 'w') as f:
            json.dump(personal_data, f, indent=2)
    
    # Update Elite Dangerous game profiles
    if elite_corrections or elite_vocab:
        games_dir = Path.home() / ".local/share/tuxtalks/games"
        
        if games_dir.exists():
            # Find Elite Dangerous profiles
            elite_profiles = list(games_dir.glob("elite_dangerous*"))
            
            if elite_profiles:
                for profile_dir in elite_profiles:
                    profile_config = profile_dir / "config.json"
                    
                    if profile_config.exists():
                        # Load existing profile config
                        with open(profile_config, 'r') as f:
                            profile_data = json.load(f)
                    else:
                        profile_data = {}
                    
                    # Merge corrections and vocabulary
                    existing_corrections = profile_data.get("VOICE_CORRECTIONS", {})
                    existing_corrections.update(elite_corrections)
                    profile_data["VOICE_CORRECTIONS"] = existing_corrections
                    
                    existing_vocab = profile_data.get("CUSTOM_VOCABULARY", [])
                    for term in elite_vocab:
                        if term not in existing_vocab:
                            existing_vocab.append(term)
                    profile_data["CUSTOM_VOCABULARY"] = existing_vocab
                    
                    logger.info(f"\nUpdating game profile: {profile_dir.name}")
                    with open(profile_config, 'w') as f:
                        json.dump(profile_data, f, indent=2)
            else:
                logger.warning("No Elite Dangerous profiles found. Elite corrections not migrated to game profile.")
        else:
            logger.warning(f"Games directory not found: {games_dir}")
    
    # Clean config.json (remove migrated items)
    logger.info("\nCleaning config.json...")
    
    # Note: We're NOT removing game_mode and player corrections from config
    # because they should be in system_corrections.json (shipped with installer)
    # Users can manually delete them if desired
    
    # Remove only personal and elite corrections
    items_to_remove = set(personal_corrections.keys()) | set(elite_corrections.keys())
    
    if "VOICE_CORRECTIONS" in config:
        original_count = len(config["VOICE_CORRECTIONS"])
        config["VOICE_CORRECTIONS"] = {
            k: v for k, v in config["VOICE_CORRECTIONS"].items()
            if k not in items_to_remove
        }
        removed_count = original_count - len(config["VOICE_CORRECTIONS"])
        logger.info(f"  Removed {removed_count} corrections from config.json")
    
    if "CUSTOM_VOCABULARY" in config:
        original_count = len(config["CUSTOM_VOCABULARY"])
        config["CUSTOM_VOCABULARY"] = [
            v for v in config["CUSTOM_VOCABULARY"]
            if v not in (elite_vocab + personal_vocab)
        ]
        removed_count = original_count - len(config["CUSTOM_VOCABULARY"])
        logger.info(f"  Removed {removed_count} vocabulary terms from config.json")
    
    # Write cleaned config
    logger.info(f"\nWriting cleaned config: {config_file}")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("Migration Complete!")
    logger.info("=" * 60)
    logger.info(f"✅ Backup created: {backup_file}")
    
    if personal_corrections or personal_vocab:
        logger.info(f"✅ Personal corrections: ~/.local/share/tuxtalks/personal_corrections.json")
    
    if elite_corrections or elite_vocab:
        logger.info(f"✅ Elite Dangerous corrections: Updated game profiles")
    
    logger.info(f"✅ Config cleaned: {config_file}")
    
    logger.info("\nNOTE: Game mode and player switching corrections remain in config.json")
    logger.info("      These will be handled by system_corrections.json in the next update.")
    logger.info("      You can manually remove them from config.json if desired.")
    
    logger.info("\n" + "=" * 60)


def main():
    """Entry point"""
    try:
        migrate_corrections()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
