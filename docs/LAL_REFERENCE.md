# Licensed Asset Loader (LAL) Reference Manual

This document provides the technical specification for the LAL Framework, used to create and distribute content packs for TuxTalks.

## Directory Structure

A content pack is a directory containing a `pack.json` manifest and resources.

```
my_pack/
├── pack.json                 # (Required) Manifest
├── LICENSE                   # (Required) License text
├── README.md                 # (Optional) Documentation
├── audio/                    # (Optional) Audio files
│   ├── index.json            # Audio metadata
│   ├── confirm_01.wav
│   └── ...
└── macros/                   # (Optional) Macro definitions
    └── combat.json
```

---

## Manifest: `pack.json`

The entry point for the pack.

```json
{
  "name": "Pack Name",          // Display name
  "version": "1.0.0",           // Semantic versioning
  "author": "Author Name",
  "license": "MIT",             // License identifier (SPDX)
  "description": "Short description",
  "url": "https://...",         // Project URL
  "compatibility": {
    "tuxtalks_version": ">=1.1.0",
    "games": ["EliteDangerous", "X4Foundations"] // "Generic" or specific game ID
  },
  "content": {
    "audio": {
      "index_file": "audio/index.json", // Path relative to pack root
      "base_dir": "audio/"              // Base audio path
    },
    "macros": [
      "macros/combat.json",
      "macros/exploration.json"
    ]
  }
}
```

---

## Audio Index: `index.json`

Maps logical sound IDs to physical files. This allows TuxTalks to "Play sound by ID" regardless of filename.

```json
{
  "version": "1.0",
  "categories": {
    "category_name": [
      {
        "id": "sound_id_unique",     // ID referenced in macros
        "file": "filename.wav",      // Relative to base_dir
        "duration_ms": 1500,         // (Optional) Duration hint
        "tags": ["tag1", "tag2"],    // (Optional) Search tags
        "text": "Spoken text content"// (Optional) Subtitle/transcript
      }
    ]
  }
}
```

### Sound Features
*   **Sequential vs Random:** If multiple entries share the same `id` (not strictly supported by schema, usually handled by Sound Pools), TuxTalks treats valid Sound Pool directories as collections. LAL currently focuses on direct file mapping.
*   **Formats:** `.wav` (PCM), `.ogg` (Vorbis), `.mp3`, `.flac`.

---

## Macro Definitions

Macros allow defining voice commands and their actions.

```json
{
  "pack_name": "My Pack Macros",
  "game_type": "EliteDangerous", // Must match Game ID in TuxTalks
  "macros": {
    "macro_unique_id": {
      "triggers": [             // Voice phrases
        "deploy hardpoints",
        "weapons hot"
      ],
      "description": "Deploys weapons and confirms",
      "category": "Combat",     // UI grouping
      "steps": [                // Execution sequence
        {
          "action": "press_key", 
          "key": "u", 
          "duration": 50
        },
        {
          "action": "wait", 
          "duration": 500
        },
        {
           "action": "play_sound",
           "id": "sound_id_unique" // References audio/index.json ID
        },
        {
           "action": "tts",
           "text": "Weapons deployed."
        }
      ]
    }
  }
}
```

### Action Types

| Action | Parameters | Description |
|--------|------------|-------------|
| `press_key` | `key` (str), `duration` (int ms) | Simulates a key press |
| `hold_key` | `key` (str) | Python `keyDown` equivalent (requires release) |
| `release_key` | `key` (str) | Python `keyUp` equivalent |
| `wait` | `duration` (int ms) | Sleep |
| `play_sound` | `id` (str) | Play audio asset from pack |
| `tts` | `text` (str) | Speak using TTS engine |
| `run_macro` | `id` (str) | Execute another macro |

---

## Distribution

1.  **Zip:** Zip the pack directory.
2.  **Naming:** `packname_v1.0.zip`.
3.  **Install:** Users unzip to `~/.local/share/tuxtalks/packs/`.

## Best Practices

1.  **Namespace IDs:** Prefix IDs with your pack name to avoid collisions (e.g., `hcs_astra_confirm_dock`).
2.  **normalize Audio:** Ensure audio levels are roughly -3dB peak.
3.  **Legal:** Include clear license files.
