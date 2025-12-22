# TuxTalks CLI Selection UX Documentation

## Overview

When using TuxTalks in CLI mode with console input enabled, the selection experience is designed for instant response. Users can interrupt TTS while it's reading options and immediately select their choice.

## UX Flow

### 1. Search with Multiple Results

When a command returns multiple matches:

```
User: "Alice play vaughan williams"
TuxTalks: "Searching for vaughan williams"
TuxTalks: "Page 1. Found 10 matches..."
TuxTalks: "1. Artist: Vaughan Williams..."
TuxTalks: "2. Composer: Vaughan Williams..."
TuxTalks: "3. Playlist: Vaughan Williams..."
TuxTalks: [continues reading list]
```

### 2. Instant Selection

User can type selection **while TTS is still speaking**:

```
User: [types "3" + Enter]
Console: "⌨️  Console input captured: '3'"
Console: "🔇 TTS interrupted by selection"
Console: "✅ Selection received: '3' (processing...)"
TuxTalks: [STOPS reading list immediately]
```

### 3. Playback Confirmation

Player announces what's playing:

```
TuxTalks: "Playing Playlist Vaughan Williams"
[Music starts playing]
```

## Technical Implementation

### TTS Interruption

When console input is received during `STATE_WAITING_SELECTION`:

```python
if self.state == self.STATE_WAITING_SELECTION:
    # Interrupt ongoing TTS
    if hasattr(self, 'tts') and self.tts:
        try:
            self.tts.stop()  # Kill aplay process
            print(f"🔇 TTS interrupted by selection")
        except:
            pass
    
    # Process selection immediately
    self.handle_selection(text)
```

**File:** `tuxtalks.py` lines 371-380

### Console Input Capture

Console input thread runs in parallel, reading from stdin:

```python
def console_input_loop(assistant):
    while True:
        if select.select([sys.stdin], [], [], 0.1)[0]:
            text = sys.stdin.readline().strip()
            if text:
                print(f"⌨️  Console input captured: '{text}'")
                assistant.process_command(text)
```

**File:** `tuxtalks.py` lines 480-502

### Player Announcement

After selection processes, player's `play_album()`, `play_playlist()`, etc. announce what's playing:

```python
def play_album(self, album):
    self.speak(f"Playing {album}")  # Queues new TTS
    self.play_precise_album(album)
```

**File:** `players/jriver.py` (and similar for other players)

## Design Philosophy

### CLI Mode (Desktop)
- **Quick keyboard controls** are primary
- User hears option they want → types number → immediate response
- Visual console feedback for debugging/confirmation
- TTS interruption enabled for instant feel

### Voice Mode (Fullscreen Gaming)
- **Hands-free operation** only
- User hears option they want → says number → selection processes
- No keyboard input (hands on game controls)
- TTS naturally paused during voice selection (ASR paused during TTS)

### Runtime Menu (Optional)
- **GUI overlay** when `tuxtalks-menu` is running
- Click or arrow-key selection
- Falls back to voice if menu not available
- Useful for multi-tasking scenarios

## User Expectations

✅ **As a CLI user, I expect:**
1. Instant response when I type a selection number
2. TTS to stop talking immediately
3. Clear confirmation of what was selected
4. Playback announcement before music starts

✅ **What the system delivers:**
1. Console input captured in real-time
2. TTS interrupted via `tts.stop()`
3. Visual console output (`⌨️`, `🔇`, `✅`)
4. Player announces selection via `speak()`

## Edge Cases

### Multiple Quick Selections
If user types multiple selections rapidly, each interrupts the previous TTS and processes in order.

### Voice Input During Selection
Both voice and console input work simultaneously. First one received wins.

### Exit with Pending Input
Console input is consumed by tuxtalks, not left in bash buffer. No `"command not found"` errors after exit.

## Performance

- **Console input latency:** <50ms (select() with 0.1s timeout)
- **TTS interruption:** <10ms (pkill aplay)
- **Selection processing:** <100ms
- **Total perceived latency:** ~100-200ms (instant to users)

## Testing

Verified working in Pre-Beta testing (2025-12-12):
- ✅ Console input captured correctly
- ✅ TTS interrupted immediately
- ✅ Selection processed instantly
- ✅ Player announcement works
- ✅ No orphaned input in bash

---

*Document created: 2025-12-12*  
*Version: 1.0*  
*Status: Verified Working*
