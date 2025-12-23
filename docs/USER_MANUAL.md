# TuxTalks User Manual

Welcome to **TuxTalks**, the privacy-focused, Linux-first voice assistant for gamers and media enthusiasts.

## 🚀 Getting Started

### Installation

TuxTalks is best installed via `pipx` to keep it isolated from your system Python.

```bash
# Install pipx if you haven't valid
# sudo pacman -S python-pipx  (Arch)
# sudo apt install pipx       (Debian/Ubuntu)

pipx install tuxtalks
```

After installation, ensure your `~/.local/bin` is in your PATH.

### First Run

Launch the configuration interface to set up your profile:

```bash
tuxtalks --setup
```

The Setup Wizard will guide you through:
1.  **Language Check:** Verifying your system language support.
2.  **Speech Engine:** Choosing your ASR (Voice Recognition) and TTS (Speech Synthesis) engines.
    *   **Vosk:** Offline, fast, lightweight.
    *   **Wyoming:** High-accuracy (Whisper), requires external server/Docker.
3.  **Media Player:** Connecting to JRiver, Strawberry, Elisa, or standard MPRIS players.
4.  **Game Integration:** Scanning for supported games (Elite Dangerous, X4 Foundations).

---

## 🎙️ Voice Control

### Recognition Modes

1.  **Keyword Mode (Default):** Fast, strict command matching.
    *   "Computer, play music"
    *   "Computer, stop engines"
2.  **Smart Mode (Ollama AI):** Natural language understanding (requires local LLM).
    *   "Put on some jazz music"
    *   "Prepare the ship for docking"

### Improving Accuracy

TuxTalks learns your voice over time!

1.  Open the GUI: `tuxtalks --gui`
2.  Go to the **Training** tab.
3.  Speak a phrase (e.g., "Stop Engines").
4.  If it mishears (e.g., "Stop End Gins"), verify the text and click **Learn**.
5.  TuxTalks will now map your specific pronunciation to the correct command.

---

## 🎮 Game Integration

TuxTalks integrates directly with game configuration files to ensure 1:1 synchronization between your voice commands and game bindings.

### Elite Dangerous
*   **Automatic Import:** Scans your `ControlSchemes`.
*   **Bindings:** Supports primary and secondary binds.
*   **Macros:** Execute complex sequences (e.g., "Request Docking" = standard Menu navigation sequence).

### X4 Foundations
*   **Platform Support:** Works with Native Linux and Proton versions (GOG/Steam).
*   **Sync Bindings:** Click "Sync Bindings" in the Games tab to automatically import `inputmap.xml` profiles.
*   **Context:** Knows if you are in a Menu or Ship to route commands correctly.

### Generic Games
For games without deep integration (like Flight Simulators or Emulators):
1.  Create a **Generic Profile**.
2.  Map voice triggers (e.g., "Gear Up") to Key Presses (e.g., `G`).
3.  TuxTalks uses `ydotool` to simulate hardware input, compliant with anti-cheat (user-level input).

---

## 🎵 Media Control

TuxTalks supports advanced media control beyond simple Play/Pause.

*   "Play artist [Name]"
*   "Play album [Name]"
*   "Play genre [Rock/Jazz/Classical]"
*   "What is playing?"
*   "Volume up/down"

**Supported Players:**
*   **JRiver Media Center:** Full library search, Zone control.
*   **Strawberry / Elisa:** Database integration for fast search.
*   **MPRIS:** Basic control for Spotify, VLC, Firefox, etc.

---

## ⚙️ Advanced Features

### Licensed Asset Loader (LAL)
Import third-party content packs (like HCS VoicePacks) legally.
*   Convert your paid content into TuxTalks Format.
*   Use high-quality celebrity voice responses.
*   See [LAL Quickstart](LAL_QUICKSTART.md).

### Custom Commands
Define your own voice macros:
1.  Go to **Games Tab**.
2.  Select **Custom Commands**.
3.  Add Trigger: "Emergency Power"
4.  Add Action: Press `Arrow Up`, Wait 50ms, Press `Arrow Right`.

### Sound Pools
Add variety to your responses. Instead of a single "Affirmative", assign a folder of sounds. TuxTalks will play a random file (or cycle sequentially) each time.

---

## ❓ Troubleshooting

**"I can't hear anything!"**
*   Check your TTS engine settings.
*   Ensure PulseAudio/PipeWire volume is up.
*   Try `tuxtalks --test-audio`.

**"It doesn't understand me."**
*   Run the Training Wizard.
*   Check microphone input levels.
*   If using Vosk, ensure you downloaded the correct language model (automatically handled in Setup).

**"Game commands aren't working."**
*   Ensure the game window has focus.
*   Check if `ydotool` daemon is running (`systemctl status ydotool`).
*   Verify bindings in the **Games Tab** match your in-game settings.

---

**TuxTalks** - Your Voice, Your Command.
