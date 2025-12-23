# TuxTalks Troubleshooting Guide

## 🎤 Audio & Speech Issues

### "TuxTalks doesn't hear me"
1.  **Check Volume:** Ensure microphone input volume is adequate in `pavucontrol` or system settings.
2.  **Test Audio:** Run `tuxtalks --test-audio`. This records 5 seconds and plays it back.
    *   If silent: Linux audio config issue (PipeWire/PulseAudio).
    *   If noisy: Reduce background noise or adjust gain.
3.  **Check Model:** If using Vosk, ensure the language model is loaded properly at startup (`~/.local/share/tuxtalks/models`).

### "TTS is silent"
1.  **Engine:** Check which TTS engine is selected (`--config` or Setup Wizard).
2.  **Piper:** requires voice files (`~/.local/share/tuxtalks/voices`). Setup Wizard normally downloads these.
3.  **System:** 'espeak' or 'spd-say' must be installed on your system.

### "I get 'Interrupted system call' errors"
*   This is normal if you interrupt the TTS by speaking or playing media. It is a debug log, not a failure.

## 🎮 Game Integration Issues

### "Commands work in terminal but not in game"
1.  **Wayland vs X11:**
    *   On Wayland, standard key simulation might be blocked for security.
    *   TuxTalks uses `ydotool` (which simulates hardware input) to bypass this.
    *   **Fix:** Ensure `ydotool` user daemon is running: `ydotoold` (usually auto-started).
2.  **Focus:** The game window MUST be the active window. TuxTalks sends keys to the *active* window.
3.  **Anti-Cheat:** TuxTalks uses standard input events. Most anti-cheats (EAC, BattlEye) allow this for accessibility tools, but verify your game's specific policy.

### "X4 / Elite Bindings show 'NOT BOUND'"
1.  **X4 Foundations:**
    *   Click **Sync Bindings** in the Games tab.
    *   Ensure you have launched the game at least once so `inputmap.xml` exists.
2.  **Elite Dangerous:**
    *   TuxTalks reads the *active* binding file (Custom.x.y.binds).
    *   If you change binds in-game, you may need to restart TuxTalks or reload the profile.

### JRiver Media Center
1.  **"Connection Failed":**
    *   Ensure MCWS (Web Service) is enabled in JRiver Options > Media Network.
    *   Default Port is 52199. Check if authentication (Access Key) is required.
    *   TuxTalks attempts to authenticate automatically if configured.
2.  **Startup Behavior:**
    *   If JRiver is not running, TuxTalks will launch it automatically and wait for it to become ready.
    *   **Note:** The JRiver GUI window appears within 1-2 seconds, but the MCWS background service (which TuxTalks uses for control) may take 10-20 seconds to fully initialize.
    *   You'll see progress dots (`⏳ Waiting for JRiver to start.....`) until the MCWS service responds.
    *   If startup takes longer than 20 seconds, you may see a warning - but commands will work once JRiver finishes loading.

## 🐍 Python/Installation Issues

### "ModuleNotFoundError"
*   Only install via `pipx install tuxtalks`.
*   If installed manually, ensure virtual environment is active.
*   Check requirements: `sudo apt install python3-pyaudio portaudio19-dev` (Debian/Ubuntu) or `pacman -S portaudio` (Arch) required for PyAudio building.

### "Permission Denied (ydotool)"
*   `ydotool` needs permission to access `/dev/uinput`.
*   Solution: Add your user to the `input` group or configure udev rules (see `ydotool` documentation).

---
**Still stuck?** Open an issue on GitHub with your `~/.local/share/tuxtalks/tuxtalks.log`.
