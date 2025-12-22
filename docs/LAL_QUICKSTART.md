# Create Your First TuxTalks Content Pack

Get started in 5 minutes!

> **⚠️ Legal Notice:**  
> Content packs you create must comply with applicable copyright and licensing laws. If your pack includes audio from commercial sources (e.g., voice actors, sound effects libraries), ensure you have the legal right to distribute those assets. TuxTalks developers are not responsible for copyright violations in third-party content packs. Always specify the correct license in your `pack.json`.

## Quick Start

### 1. Create Directory Structure

```bash
mkdir -p my_pack/{audio,macros}
cd my_pack
```

### 2. Create `pack.json`

```json
{
  "name": "My Awesome Pack",
  "version": "1.0.0",
  "author": "Your Name",
  "license": "MIT",
  "description": "Custom voice responses and macros",
  "compatibility": {
    "tuxtalks_version": ">=1.1.0",
    "games": ["EliteDangerous"]
  },
  "content": {
    "audio": {
      "index_file": "audio/index.json"
    },
    "macros": ["macros/my_macros.json"]
  }
}
```

### 3. Add Audio (Optional)

Create `audio/index.json`:

```json
{
  "version": "1.0",
  "categories": {
    "confirmations": [
      {
        "id": "confirm_landing_gear",
        "file": "landing_gear.wav",
        "duration_ms": 1200,
        "tags": ["elite", "ship"]
      }
    ]
  }
}
```

Place your audio files in `audio/` directory.

###  4. Add Macros (Optional)

Create `macros/my_macros.json`:

```json
{
  "pack_name": "My Macros",
  "game_type": "EliteDangerous",
  "macros": {
    "combat_ready": {
      "triggers": ["combat mode", "weapons hot"],
      "description": "Prepare for combat",
      "steps": [
        {"action": "deploy hardpoints", "delay": 100},
        {"audio_feedback": "confirm_weapons_hot", "delay": 500}
      ]
    }
  }
}
```

### 5. Install

```bash
# Copy to TuxTalks packs directory
cp -r my_pack ~/.local/share/tuxtalks/packs/

# TuxTalks will auto-discover on next launch!
```

## File Limits

- **Audio files:** 10MB per file (WAV, OGG, MP3, FLAC)
- **Macro files:** 1MB per file (JSON only)
- **Total pack:** 500MB max

## Supported Formats

- **Audio:** WAV, OGG, MP3, FLAC
- **Macros:** JSON only

---

## Converting VoiceAttack Packs

Already have a VoiceAttack profile pack (like KICS, HCS VoicePacks)? Here's how to use the audio with TuxTalks:

### Example: Converting KICS

1. **Download and extract** the VoiceAttack pack
   ```bash
   unzip KICS-4.1.zip
   cd KICS-4.1/Ripley\ Galactic/KICS\ 4/Audio
   ```

2. **Create TuxTalks pack structure**
   ```bash
   mkdir -p ~/.local/share/tuxtalks/packs/kics/audio
   ```

3. **Copy audio files**
   ```bash
   cp *.mp3 ~/.local/share/tuxtalks/packs/kics/audio/
   ```

4. **Create pack.json**
   ```bash
   cd ~/.local/share/tuxtalks/packs/kics
   nano pack.json
   ```

   Paste this:
   ```json
   {
     "name": "KICS Audio Pack",
     "version": "4.1",
     "author": "mwerle (VoiceAttack) - Converted for TuxTalks",
     "description": "KICS (Keep It Classy Shipmate) audio responses for Elite Dangerous",
     "license": "See original KICS License.txt",
     "compatibility": {
       "tuxtalks_version": ">=1.0.29",
       "games": ["Elite Dangerous"]
     },
     "content": {
       "audio": {
         "responses": "audio/"
       }
     }
   }
   ```

5. **Copy LICENSE** (important!)
   ```bash
   cp ../KICS-4.1/License.txt ~/.local/share/tuxtalks/packs/kics/
   ```

6. **Restart TuxTalks** - Pack auto-loads on startup

**Note:** VoiceAttack packs often have hundreds of audio files with specific naming conventions. You'll need to map these to TuxTalks game actions manually, or use them as generic audio feedback. Check the original pack's documentation for audio file descriptions.

---

## That's It!

Your pack will be automatically discovered when TuxTalks starts. No registration, no approval needed!

---

## Next Steps

- **Learn More:** See [LAL_REFERENCE.md](LAL_REFERENCE.md) for complete specification
- **Distribution:** See [LAL_DISTRIBUTION.md](LAL_DISTRIBUTION.md) for sharing your pack
- **Examples:** Check `LAL_EXAMPLES/` for working examples
