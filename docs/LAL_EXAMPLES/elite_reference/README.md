# Elite Dangerous Reference Pack

This is a reference pack demonstrating the LAL (Licensed Asset Loader) format.

## Contents

- **Audio:** 7 voice responses (confirmations, alerts, acknowledgements)
- **Macros:** 4 macros (combat + exploration)

## Installation

```bash
# Copy to TuxTalks packs directory
cp -r elite_reference ~/.local/share/tuxtalks/packs/

# Or use git
cd ~/.local/share/tuxtalks/packs/
git clone https://github.com/tuxtalks/elite_reference.git
```

## Usage

1. Launch TuxTalks
2. Pack will auto-load
3. Macros available in Elite Dangerous profile
4. Audio feedback will play when macro steps include `audio_feedback` ID

## Macros Included

- **"engage" / "weapons hot"** - Deploy hardpoints, set power distribution
- **"emergency jump"** - Quick FSD activation
- **"scan system"** - FSS discovery scanner
- **"deploy" / "landing sequence"** - Landing gear + retract hardpoints

## Audio Files

**Note:** This reference pack uses placeholder audio file names. For a real pack, include actual WAV/OGG files:

- `landing_gear_down.wav`
- `landing_gear_up.wav`
- `hardpoints_deployed.wav`
- `shields_down.wav`
- `hull_damage.wav`
- `affirmative.wav`
- `negative.wav`

## Learn More

- [LAL_QUICKSTART.md](../../LAL_QUICKSTART.md) - Create your own pack
- [LAL_REFERENCE.md](../../LAL_REFERENCE.md) - Complete specification
- [LAL_DISTRIBUTION.md](../../LAL_DISTRIBUTION.md) - Distribution methods
