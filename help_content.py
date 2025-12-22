"""Help content for TuxTalks configuration GUI"""

def get_help_text():
    return """
╔════════════════════════════════════════════════════════════════╗
║                     TuxTalks Help                              ║
╚════════════════════════════════════════════════════════════════╝

🛡️ ANTI-CHEAT SAFE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TuxTalks has passed comprehensive security auditing and operates
as a standard accessibility tool (like VoiceAttack or Dragon).

• Uses user-space input only (no memory manipulation)
• Cannot read or modify game memory
• Complies with VAC, EAC, and BattlEye principles
• Slower than manual input (~500ms voice latency)

See SECURITY_AUDIT.md for complete details.

SUPPORTED PLAYERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WAKE WORD
  Default: "Mango"
  Usage: Say the wake word before each command
  
  Two-Stage Mode:
    • Say wake word alone → "Yes?" (20 second window)
    • Then give command without wake word
    
  One-Stage Mode:
    • Say wake word + command in same phrase
    • Example: "Mango, play Beethoven"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLAYER SWITCHING
  Switch between media players on the fly:
  
  Commands (any of these work):
    • "change player to [name]"
    • "switch player to [name]"
    • "change to player [name]"
    • "use player [name]"
  
  Supported Players:
    • JRiver - "change player to jriver"
    • Strawberry - "switch to player strawberry"
    • Elisa - "use player elisa"
    • VLC/MPRIS - "change player to vlc"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLAYBACK COMMANDS
  Music Control:
    • "play [artist/album/song]"
    • "play random [genre]"
    • "play playlist [name]"
    • "play smartlist [name]"
    • "pause" / "play pause"
    • "stop"
    • "next" / "next track"
    • "previous" / "previous track"
    • "what's playing?"
    • "what are we listening to?"
  
  Volume:
    • "volume up"
    • "volume down"
    • "set volume to [0-100]"
    • "mute"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLAYLIST & SMARTLIST COMMANDS
  JRiver/Strawberry/Elisa:
    • "play playlist [name]" - Plays playlist in order
    • "shuffle playlist [name]" - Randomizes playlist
    • "play smartlist [name]" - JRiver smartlists
    • "shuffle smartlist [name]" - Randomize smartlist

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VOICE CORRECTIONS
  If the ASR mishears you:
  1. Check "Recent Ignored/Missed Commands" in Corrections tab
  2. Select one or more misheard phrases (Ctrl+Click)
  3. Click "Use Selected"
  4. Enter what it should recognize
  5. Batch corrections save time with Vosk!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEYBOARD SHORTCUTS
  Global Shortcuts (configurable in Input tab):
    • Right Arrow - Next page/track (default)
    • Left Arrow - Previous page/track (default)
  
  Console Commands:
    • Type number ("1", "12") or command text
    • Press Enter to execute

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SPEECH ENGINES
  ASR (Speech Recognition):
    • Vosk - Fast, offline, privacy-focused (recommended)
    • Whisper - High accuracy, needs NVIDIA GPU
  
  TTS (Text-to-Speech):
    • Piper - Natural, offline (recommended)
    • System - Basic eSpeak fallback

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING

"I didn't understand..." spam:
  → Go to Corrections tab and disable announcements
  → Or train voice corrections for common phrases

Player connection failed:
  → Ensure player is running before switching
  → Check Player tab for connection status

Commands not working:
  → Check wake word is correct
  → Train voice (Corrections → Record button)
  → Add phonetic corrections for misheard words

MPRIS/VLC not found:
  → Set Service Name: org.mpris.MediaPlayer2.vlc
  → Or use: org.mpris.MediaPlayer2.[appname]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GAME INTEGRATION & SETUP

  Elite Dangerous - Automatic:
    • Steam: TuxTalks auto-detects standard Proton paths.
    • Status: "Detected: X4 Foundations" means the process is running.

  Elite Dangerous - Manual Setup (Wine/Lutris/Non-Steam):
    If the auto-scanner doesn't find your bindings (e.g. you use Wine or Lutris),
    you can manually point TuxTalks to the correct folder:

    1. Go to Games Tab → "Add Game" (or "Edit Game").
    2. Set Game Type to "Elite Dangerous".
    3. Click "Browse" next to Bindings Path.
    4. Navigate to your bindings folder. Common locations:

    Steam (Default):
      ~/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings

    Lutris / Wine:
      ~/.wine/drive_c/users/[your_user]/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings
      (Replace ~/.wine with your custom Wine prefix if applicable)

    5. Select any *.binds file in that folder (TuxTalks will auto-detect the latest version).

  Interactive Binding Editing:
    • Right-Click any command in the table to "Edit Mapped Key".
    • Press and Hold your key combo (e.g. Ctrl+Alt+H).
    • Release keys to see the latched combination.
    • Click OK to save directly to your game's config file.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LIBRARY SCANNING (MPRIS only)
  Update library:
    1. Go to Player tab → Select MPRIS
    2. Click "Scan Now"
    3. Choose:
       • Replace - Clear all and rescan
       • Update - Keep existing, add new
       • Cancel - Abort

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTENT PACKS (LAL FRAMEWORK)

  What are Content Packs?
    Third-party audio responses and macros for games.
    Example: Custom voice packs, audio feedback, macro libraries

  Installing Packs:

    GUI Method (Easiest):
      1. Go to \"Content Packs\" tab in launcher
      2. Click \"Install Pack\"
      3. Select your .zip or .tar.gz file
      4. Pack installs automatically

    CLI Method (Power Users):
      tuxtalks-install-pack ./my-pack.zip
      tuxtalks-install-pack https://example.com/pack.tar.gz
      tuxtalks-install-pack --list

    Manual Method:
      Extract pack folder to: ~/.local/share/tuxtalks/packs/

  Creating Your Own Pack:
    See: docs/LAL_QUICKSTART.md for step-by-step guide
    
    Supported Formats:
      • Audio: WAV, OGG, MP3, FLAC (10MB max per file)
      • Macros: JSON only (1MB max per file)
      • Total pack: 500MB max

  Converting VoiceAttack Packs:
    VoiceAttack packs (like KICS, HCS VoicePacks) need conversion:
    1. Extract VoiceAttack pack manually
    2. Create pack.json (see LAL_QUICKSTART.md)
    3. Copy audio files to proper structure
    4. Copy to ~/.local/share/tuxtalks/packs/
    
    See \"Converting VoiceAttack Packs\" section in LAL_QUICKSTART.md

  ⚠️ Licensing Responsibility:
    • TuxTalks is MIT licensed
    • Third-party packs may have different licenses
    • Check pack.json → license field
    • You are responsible for respecting pack licenses
    • TuxTalks does not endorse or verify third-party content

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MACRO & SOUND POOLS
  
  Sound Pool (Random/Multi-Audio):
    • Add multiple audio files to a single macro step.
    • Modes:
      - Random: Plays one file at random (e.g. variable responses).
      - Simultaneous: Plays all files at once (layers).
      - Sequential: Cycles through files one by one.
    • Audio Only: Leave the "Key" field blank to play sound without pressing keys.

  Macro Profiles:
    • Built-in: Standard macros included with TuxTalks (Green).
    • Custom (Default): Your additions overlaying the Built-in set.
    • Named Profiles (New): Create specific profiles (e.g. "Trading", "Combat").
      - Starts EMPTY (Clean Slate) - no built-in clutter.
      - Selection is saved per-game.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIPS
  • Use Vosk for low latency, Whisper for noisy environments
  • Train voice corrections for better accuracy
  • Select multiple ignored commands for batch corrections
  • Use player switching to handle different media types
  • Check logs for detailed error messages

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For more help, visit: https://github.com/YourRepo/tuxtalks
"""
