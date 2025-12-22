# TuxTalks

![Anti-Cheat Safe](https://img.shields.io/badge/Anti--Cheat-Safe-brightgreen?style=flat-square)
![Security Audited](https://img.shields.io/badge/Security-Audited-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

A voice-controlled assistant for Linux gamers and media enthusiasts, featuring game integration (Elite Dangerous, X4 Foundations), media player support (JRiver, Strawberry, Elisa, MPRIS), and **6-language UI support**.

> **🛡️ Anti-Cheat Certified:** TuxTalks has passed comprehensive security auditing and operates as a standard accessibility tool. It uses user-space input only and is functionally equivalent to commercial voice control software like VoiceAttack. [See Security Audit](SECURITY_AUDIT.md)

> **📦 Status:** Voice Learning v1.1 Complete - Self-improving voice recognition live!

## Features
- **Voice Control**: Play music by Artist, Album, or Track using natural language
- **🎓 Voice Learning**: Automatically improves accuracy by learning from your voice (zero training required!)
- **Video Support**: Play video files (.mp4, .mkv, .avi, etc.) via MPRIS players like VLC
- **Player Support**: JRiver, Strawberry, Elisa, and standard MPRIS players
- **6 Languages**: English, Spanish, Ukrainian, Welsh, German, French, Arabic (with RTL support)
- **Game Integration**: Elite Dangerous and X4 Foundations voice commands and macros
- **Customizable**: Wake Word, Speech Recognition Model (Vosk), TTS Voice (Piper)
- **Voice Import**: Easily import new Piper voices from Hugging Face or GitHub
- **Smart Interface**: Auto-detects desktop/CLI environment, `--gui`/`--cli` flags available
- **Content Packs**: Licensed Asset Loader for community macro/voice packs

## Installation
```bash
pipx install .
```

## Configuration
Run the configuration tool to set up your preferences:
```bash
tuxtalks-config
```

### Voice Customization
- **Import Voices**: Easily import new Piper voices from URL or local files via the "Voice" tab.
- **Hugging Face Support**: Paste a folder URL (e.g., `.../en/en_GB/cori/high`) and it will automatically find the voice files.
- **GitHub Support**: Paste a file URL (blob) and it will automatically convert it to a raw download link.
- **Management**: Delete unwanted voices and models directly from the GUI.

## Usage
1. Run the assistant:
   ```bash
   tuxtalks
   ```
2. Say your **Wake Word** (default: "Alice", "Mango", etc.).
3. Speak a command:
   - "Play [Artist]"
   - "Play [Album]"
   - "List tracks"
   - "Next", "Previous", "Pause", "Resume"
   - "Quit"

## Requirements
- Linux
- Python 3.8+
- `vosk`
- `piper-tts` (managed internally)

## 🎓 Voice Learning (NEW!)

TuxTalks automatically learns YOUR voice patterns and improves accuracy over time - **zero training required!**

### How It Works

When you use voice commands, the system:
1. **Detects Corrections**: Notices when Ollama LLM fixes ASR errors
2. **Learns Patterns**: Remembers "I heard X but meant Y"
3. **Improves Future Commands**: Injects learned patterns into prompts

**Example:**
- You say "play Abba" → ASR hears "play ever"
- Ollama corrects to "ABBA" (from your library)
- Music plays → System learns: "ever" → "ABBA"
- Next time: Higher accuracy automatically!

### Privacy

- ✅ **100% Local**: All learning data stored on your machine
- ✅ **No Cloud**: Never uploaded anywhere
- ✅ **User Control**: Clear patterns anytime
- 📁 Data location: `~/.local/share/tuxtalks/voice_fingerprint.json`

### Performance

- First command: ~1s (loads your music library)
- Subsequent commands: <1s  
- Learning overhead: <10ms
- Self-improves with every use!

**Learn More:** See [Voice Learning Analysis](docs/VOICE_LEARNING_ANALYSIS.md) for technical details and roadmap.

## 🎮 Custom Games Framework

TuxTalks now supports adding **ANY** game or application via the Launcher's **Add Game Wizard**.

1.  **Launch Your Game**: Start the game you want to control.
2.  **Open Wizard**: Click `Add` in the Games tab.
3.  **Scan & Select**: Choose your game process from the list.
4.  **Configure**:
    *   **Generic / Other**: Use this for games without built-in presets. You can manually map voice commands to keys.
    *   **Installation Keyword**: Leave this **BLANK** unless you have multiple installs (e.g. distinguishing a Steam install from a GOG install). It acts as a filter for the file path.

Settings are saved persistently to `~/.config/tuxtalks/user_games.json`.

### 🧙 Understanding the Wizard
To ensure your games are organized exactly how you want them in the main UI, it is important to understand how the Wizard fields map to the final result:

*   **Game Name** = **Game Group** (The generic category in the main dropdown).
    *   *Example*: If you type **"X-Plane 12"** here, a new group "X-Plane 12" will be created.
*   **Profile Variant** = **Profile Name** (The specific config in the sub-dropdown).
    *   *Example*: If you type **"Boeing 737"** here, it becomes the profile name under that group.
*   **Result**: You will select **Game: X-Plane 12** -> **Profile: Boeing 737**.

Use "Generic / Other" mode to fully customize these names.


### 🍷 Elite Dangerous (Wine/Lutris/Proton) Support
TuxTalks fully supports Elite Dangerous running in non-standard environments (Lutris, Heroic, custom Wine prefixes).

1.  **Select Game Process**: Use the Wizard to select your running `EliteDangerous64.exe`.
2.  **Set Bindings Path**: In the "Bindings Path" field, point to your custom bindings location.
    *   **Folder**: e.g., `~/Games/elite-dangerous/drive_c/users/steamuser/.../Options/Bindings/` (TuxTalks will auto-detect the latest `.binds` file).
    *   **Specific File**: e.g., `~/Documents/MyBindings.binds` (Forces usage of this specific file).
3.  **Full Feature Support**: Even with a custom path, you get the full "Care Package":
    *   ✅ **Voice Commands**: Automatically mapped to your custom keys.
    *   ✅ **Macro Recording**: New macros are written back to your custom file.
    *   ✅ **Persistence**: Your custom path is remembered forever.

## ⌨️ Editing Game Bindings
You can modify your game keybindings directly from TuxTalks without launching the game:
1.  **Right-Click** any command in the "Active Profile Bindings" list.
2.  Select **"🎹 Edit Mapped Key"**.
3.  **Press and Hold** your desired key combination (e.g., `Ctrl` + `Alt` + `H`).
4.  Release the keys to see the latched combination.
5.  Click **OK** to save. This updates the game's actual config file (e.g. Elite Dangerous `.binds`).

### Advanced Binding Features
- **Context Awareness**: You can reuse keys in different contexts (e.g., use 'A' for both *Ship* and *SRV* functions). The system only warns if you create a conflict within the same mode.
- **Controller Support**: Joystick/Gamepad bindings are detected and displayed (e.g., `Joy_5 (SaitekX52)`), but Voice Control will prioritize Keyboard Emulation for reliability.

---

## 🛡️ Anti-Cheat & Security FAQ

### Is TuxTalks safe to use with online games?

**Yes.** TuxTalks has undergone comprehensive security auditing to verify it cannot be abused as a cheat engine.

### Will I get banned for using TuxTalks?

**No.** TuxTalks operates identically to commercial voice control software (VoiceAttack, VoiceBot) and programmable macro keyboards, which are widely accepted in gaming. It:

- ✅ Uses **user-space input only** (no memory manipulation)
- ✅ Sends keyboard input via standard Linux uinput (same as accessibility tools)
- ✅ Cannot read or modify game memory
- ✅ Cannot hook into game processes
- ✅ Is **slower than manual input** (voice recognition adds ~500ms latency)

### How does TuxTalks work?

TuxTalks listens for voice commands and translates them into keyboard presses using `ydotool` (user-space input daemon). This is identical to how Dragon NaturallySpeaking, VoiceAttack, or a programmable keyboard works.

**Technical Details:**
- Voice → Speech Recognition → Command Lookup → Keyboard Simulation
- No interaction with game memory or processes
- Operates at OS input layer (accessible to all applications)

### What about VAC, EAC, or BattlEye?

TuxTalks complies with all major anti-cheat principles:

| Anti-Cheat | Compliance | Reason |
|------------|------------|--------|
| **VAC** (Valve) | ✅ Safe | No memory access, process injection, or kernel hooks |
| **EAC** (Epic) | ✅ Safe | No game file modification or process hooking |
| **BattlEye** | ✅ Safe | User-space input only, transparent operation |

See [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for the complete security audit report.

### Does TuxTalks provide an unfair advantage?

**No.** Voice commands are **slower** than manual keyboard input:
- Voice recognition latency: ~500ms
- Manual keyboard press: <50ms

TuxTalks is an **accessibility tool** for players who:
- Have physical limitations
- Want hands-free operation during complex maneuvers
- Prefer voice control for immersion

### Can I use TuxTalks in competitive play?

While TuxTalks is technically safe, **always check your game's specific rules**. Most games allow:
- ✅ Voice control software
- ✅ Macro keyboards
- ✅ Accessibility tools

Some competitive leagues may have stricter rules. When in doubt, ask tournament organizers.

### What games are supported?

- **🎮 Native Support:** Elite Dangerous, X4 Foundations
- **🕹️ Generic Framework:** Any game via custom profile creation
- **🎵 Media:** JRiver, Strawberry, Elisa, VLC, Spotify (via MPRIS)

### Where can I learn more?

- **Security Details:** [SECURITY_AUDIT.md](SECURITY_AUDIT.md)
- **Development Guide:** [DEVELOPMENT.md](DEVELOPMENT.md)
- **Roadmap:** [ROADMAP.md](ROADMAP.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📦 Content Packs (LAL Framework)

TuxTalks supports third-party **Licensed Asset Loader (LAL)** content packs for custom audio responses and macros.

### Installing Packs

**GUI Method:**
1. Launch `tuxtalks-launcher`
2. Go to "Content Packs" tab
3. Click "Install Pack" and select your `.zip` or `.tar.gz` file

**CLI Method:**
```bash
tuxtalks-install-pack ./my-pack.zip
tuxtalks-install-pack https://example.com/pack.tar.gz
```

**Manual Method:**
Extract pack folder to `~/.local/share/tuxtalks/packs/`

### Creating Packs

See [LAL_QUICKSTART.md](docs/LAL_QUICKSTART.md) for pack creation guide.

**Supported Formats:**
- Audio: WAV, OGG, MP3, FLAC (10MB max per file)
- Macros: JSON only (1MB max per file)
- Pack size: 500MB max total

### ⚠️ Licensing Responsibility

**TuxTalks is MIT licensed**, but third-party content packs may have different licenses. **You are responsible for:**
- Respecting pack licenses (check `pack.json` → `license` field)
- Not distributing copyrighted audio without permission
- Complying with terms of commercial voice packs (e.g., HCS VoicePacks)

TuxTalks developers **do not endorse, verify, or assume liability** for third-party content. The LAL framework is provided as-is for user convenience, similar to package managers like npm or pip.

---

Edit `~/.local/share/tuxtalks/personal_corrections.json`:
```json
{
  "VOICE_CORRECTIONS": {
    "chop in": "chopin",
    "mo sart": "mozart"
  },
  "CUSTOM_VOCABULARY": ["Chopin", "Mozart"]
}
```

### Migration from Older Versions

If upgrading with corrections in config.json:
```bash
tuxtalks-migrate-corrections
```

This automatically categorizes and splits your corrections, reducing config.json by ~50%!

---

## Development
See [DEVELOPMENT.md](DEVELOPMENT.md) for architecture details.

## License
MIT License - See [LICENSE](LICENSE) for details.
