# Developer Guide

This document provides a technical overview of the TuxTalks architecture to help you understand the codebase.

## Architecture Overview

TuxTalks is built as a modular Python application consisting of a Core Orchestrator, specific Players, and a Launcher UI.

### Core Components (`core/`)

*   **`tuxtalks.py`**: The main entry point and orchestrator. It initializes the Voice Assistant, handles the main loop, and manages shutdown.
*   **`command_processor.py`**: The "brain" of the operation. It receives normalized text and decides which action to take (Media control, Game macro, System command).
*   **`text_normalizer.py`**: Cleans up raw ASR output (e.g., "play Beethoven." -> "play beethoven"). Handles phonetic corrections and number parsing.
*   **`state_machine.py`**: Manages the application state (LISTENING, SPEAKING, COMMAND_MODE) and handles timeouts.
*   **`selection_handler.py`**: Manages user interaction when multiple search results are found (pagination, selection by number).

### Players (`players/`)

TuxTalks supports multiple media players via a plugin-like interface (`player_interface.py`).
*   **`jriver.py`**: Complex integration with JRiver Media Center via MCWS API.
*   **`mpris.py`**: Generic Linux media player control (VLC, Spotify, Rhythmbox) via DBus.
*   **`strawberry.py`**: SQL-based integration for the Strawberry Music Player.

### Launcher (`launcher.py` + `launcher_*.py`)

The configuration GUI is built with Tkinter and modularized into tabs:
*   **`launcher.py`**: Main window shell.
*   **`launcher_speech_tab.py`**: ASR/TTS configuration.
*   **`launcher_player_tab.py`**: Player selection and setup.
*   **`launcher_games_tab.py`**: Game bindings and Macro editor.
*   **`launcher_corrections_tab.py`**: Managing phonetic corrections and ignored commands.
*   **`launcher_training_tab.py`**: Voice training interface for manual pattern learning.

### Voice Learning System (`voice_fingerprint.py`)

TuxTalks includes a hybrid voice learning system that improves ASR accuracy over time:

**Architecture:**
*   **`voice_fingerprint.py`**: Core learning engine (475 lines)
    - Pattern storage with confidence scoring
    - JSON persistence (`~/.local/share/tuxtalks/voice_fingerprint.json`)
    - Automatic pattern extraction from ASR errors
*   **`launcher_training_tab.py`**: Manual training UI (400 lines)
    - 5-sample recording workflow
    - Real-time ASR transcription
    - Pattern management interface

**Three Learning Phases:**
1. **Passive Learning**: Automatic corrections from successful Ollama matches
   - Example: ASR hears "ever" → Ollama corrects to "abba" → System learns "ever" → "abba"
   - Zero user effort, learns during normal usage
   - Lower confidence (32%) initially, improves with repetition

2. **Library Context**: Bootstrap with user's music library
   - Injects top 50 artists into Ollama prompts
   - Immediate first-time corrections
   - Reduces learning curve for new users

3. **Manual Training**: User-driven via GUI
   - Record phrase 5 times
   - Higher confidence (55%, 3x weighted)
   - For problematic artists or non-English pronunciations

**Integration Points:**
- `command_processor.py`: Hooks for success detection
- `ollama_handler.py`: Prompt enhancement with learned patterns
- `text_normalizer.py`: Potential future integration for pre-processing

## Key Data Flows

1.  **Voice Input**: `VoiceAssistant` listens via `input_listener.py`.
2.  **ASR**: Audio is sent to `speech_engines/wyoming_asr.py` (or others).
3.  **Normalization**: Text is cleaned by `text_normalizer.py`.
4.  **Processing**: Clean text goes to `command_processor.py`.
5.  **Execution**:
    *   **Media**: Delegated to the active Player instance.
    *   **Game**: Delegated to `game_manager.py` (Key presses via `input_controller.py`).
    *   **System**: Executed directly (e.g., volume, shutdown).

## Game Integration

The Game Integration uses a parser-based architecture:
*   **Game Manager (`game_manager.py`)**: Handles profile management, process detection, and conflict resolution.
*   **Parsers (`parsers/`)**: Dedicated modules for reading game configuration files.
*   **`ed_parser.py`**: Handles Elite Dangerous `.binds` (XML) files.
    *   **X4 Integration**: Parses `inputmap.xml` to map actions to keys.

## Critical Architectural Rules

### Game Profile System (DO NOT BREAK)

> **⚠️ CAUTION:** The profile system is fragile and has undergone multiple regression fixes. Follow these rules strictly.

#### Data Flow Principle
```
User Action → Modify In-Memory List → Save to Disk
              ↑                         ↓
              └─────── Never Reload ────┘
```

**Golden Rule:** After modifying `self.profiles` in `GameManager`, NEVER call `load_profiles()`. The data is already correct in memory.

#### When to Use Each Method

| Method | Use Case | Safe? |
|--------|----------|-------|
| `load_profiles()` | **STARTUP ONLY** | ⚠️ Replaces entire `self.profiles` |
| `add_profile(p)` | Adding single profile | ✅ Appends + saves |
| `batch_add_profiles([...])` | Importing defaults | ✅ Batch append + single save |
| `save_profiles()` | Manual save | ✅ Writes to disk only |

#### Common Anti-Patterns (FORBIDDEN)

```python
# ❌ WRONG - Causes data loss
self.profiles.append(new_profile)
self.save_profiles()
self.load_profiles()  # DO NOT RELOAD AFTER MUTATION

# ✅ CORRECT
self.profiles.append(new_profile)
self.save_profiles()
# That's it - data is consistent
```

#### Error Handling Requirements

1. **Per-Entry Safety:** `load_profiles()` MUST wrap each profile in try-except to prevent one bad entry from wiping all data
2. **Empty File Handling:** JSON parsers must check for empty content before parsing
3. **Active Flag:** Must be read during load and written during save

#### Testing Checklist

Before merging any changes to `game_manager.py` or `launcher_games_tab.py`:
- [ ] Add 30+ profiles via "Default Profiles" import
- [ ] Add a custom game via wizard
- [ ] Verify all profiles remain visible (no vanishing)
- [ ] Restart app - verify active profile persists
- [ ] Check console for no catastrophic errors

#### Known Fragile Areas

1. **Profile Name Matching:** Uses exact string comparison for UI display mapping
2. **Group String Consistency:** Must match exactly between save/load
3. **XML Parsing:** X4 uses both `INPUT_STATE_*` and `INPUT_ACTION_TOGGLE_*` formats
4. **Wizard Validation:** Generic types require both Process Name AND Bindings Path

### Security & Anti-Cheat Compliance

> **⚠️ MANDATORY:** All development must maintain anti-cheat compliance verified in Checkpoint 0.

**Security Audit:** [SECURITY_AUDIT.md](SECURITY_AUDIT.md) documents the comprehensive security review that certified TuxTalks as safe for use with anti-cheat protected games.

**Core Security Principles:**
1. **Process Isolation:** Commands only execute for user-registered games (whitelist-only)
2. **Input Sanitization:** All subprocess calls use array syntax (`shell=False`)
3. **No Dynamic Code:** Zero `eval()`, `exec()`, or `compile()` in application code
4. **User-Space Only:** ydotool for input (no memory access, no process hooks)
5. **Bounded File Access:** Limited to `~/.config/tuxtalks/` and `~/.local/share/tuxtalks/`

**Prohibited Patterns:**
- ❌ `subprocess.run(cmd, shell=True)` - Use array syntax instead
- ❌ `eval(user_input)` - No dynamic code execution
- ❌ Memory manipulation (ctypes, mmap with game processes)
- ❌ Process injection (ptrace, LD_PRELOAD)
- ❌ Kernel modules or drivers

**Before Adding Features:**
1. Does it require reading/writing game memory? → **REJECT**
2. Does it hook into game processes? → **REJECT**
3. Does it execute user-provided code? → **SANITIZE**
4. Does it provide superhuman reaction times? → **RECONSIDER**



### ⚠️ Critical Architecture: Wizard Parity

The **Add Game Wizard** (`launcher_games_tab.py:AddGameDialog`) has a strict parity relationship with the internal data model and the main UI:

*   **Wizard "Game Name"** ➡️ **Profile `group`** ➡️ **Main UI "Game" Dropdown**.
*   **Wizard "Profile Variant"** ➡️ **Profile `name`** ➡️ **Main UI "Profile" Dropdown**.

**DO NOT** attempt to "standardize" or "clean" these inputs based on assumptions (e.g., forcing all regex-matched "X-Plane" inputs into a single "X-Plane" group). The user needs full control to create arbitrary groups (e.g., "X-Plane 12" vs "X-Plane 11") by typing into the Wizard's editable fields. Breaking this parity destroys user organization.

---

## Voice Corrections Architecture

TuxTalks uses a multi-source corrections system with priority-based loading.

### File Structure

```
~/.config/tuxtalks/config.json                    # Settings + legacy corrections
~/.local/share/tuxtalks/
  ├── personal_corrections.json                   # User's music artists, personal terms
  └── games/*/config.json                         # Game-specific vocabulary
/usr/.../tuxtalks/data/system_corrections.json    # Shipped common fixes
```

### Loading Priority (Highest Wins)

1. **config.json** - `VOICE_CORRECTIONS` dict (backwards compat, highest priority)
2. **Game Profile** - Loaded only when `GAME_MODE_ENABLED=true`
3. **personal_corrections.json** - User's personal corrections
4. **system_corrections.json** - Shipped defaults (lowest priority)

### Implementation

**text_normalizer.py:**
```python
def _build_aliases(self):
    # Priority 1: Built-in hardcoded aliases
    aliases = {...}
    
    # Priority 2: System corrections
    aliases.update(self._load_system_corrections())
    
    # Priority 3: Personal corrections
    aliases.update(self._load_personal_corrections())
    
    # Priority 4: Game corrections (context-aware)
    if config.get("GAME_MODE_ENABLED"):
        aliases.update(self._load_game_corrections())
    
    # Priority 5: Config.json (backwards compat, overrides all)
    aliases.update(config.get("VOICE_CORRECTIONS", {}))
    
    return aliases
```

### Migration Tool

**tuxtalks-migrate-corrections** auto-categorizes corrections:

```python
ELITE_KEYWORDS = ["gear", "landing", "jump", "fsd", ...]
GAME_MODE_KEYWORDS = ["game mode", "enable game", ...]  
PLAYER_KEYWORDS = ["jriver", "strawberry", "vlc", ...]
```

**Process:**
1. Backup config.json
2. Categorize all corrections by keywords
3. Write personal_corrections.json (music/artists)
4. Update game profile configs (Elite Dangerous terms)
5. Clean config.json (remove migrated items)

**Result:** Typical 50%+ config size reduction.

### File Formats

**personal_corrections.json:**
```json
{
  "VOICE_CORRECTIONS": {
    "i bet owe them": "play beethoven",
    "she economy": "kiri te kanawa"
  },
  "CUSTOM_VOCABULARY": ["Beethoven", "Kiri Te Kanawa"]
}
```

**system_corrections.json** (shipped):
```json
{
  "VOICE_CORRECTIONS": {
    "manga": "mango",
    "jay river": "jriver",
    "oh game mode": "enable game mode"
  }
}
```

### Design Rationale

**Why Multi-Source?**
- config.json bloat (143 lines → 75 lines after migration)
- Music artists can grow indefinitely without bloating config
- Game vocabulary only loaded when gaming (faster, more accurate)
- System fixes ship with installer (better new user experience)

**Why Priority System?**
- User config overrides all (explicit intent)
- Game context beats personal (situational accuracy)
- Personal beats system (user knows their voice best)
- Backwards compatible (existing config.json still works)

### Developer Workflow

**Add System Correction:**
Edit `data/system_corrections.json`, reinstall.

**Test Multi-Source Loading:**
```bash
tuxtalks-cli
# Watch log for:
# DEBUG: Built-in aliases: 89
# DEBUG: After system corrections: 121 total
# DEBUG: After personal corrections: 133 total
# INFO: Text normalizer loaded 133 total corrections
```

**Avoid Regressions:**
- NEVER remove backwards compat for config.json
- ALWAYS maintain priority order (highest = config.json)
- TEST migration tool with real config before release
