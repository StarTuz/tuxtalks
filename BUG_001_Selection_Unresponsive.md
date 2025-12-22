# Pre-Beta Testing - Bug Report

**Date:** 2025-12-12  
**Bug ID:** #001  
**Severity:** Medium  
**Status:** ✅ **VERIFIED** - Working correctly

## Issue Description

System becomes unresponsive after presenting selection options and waiting for user input.

## Steps to Reproduce

1. Say wake word + command (e.g., "Alice play vaughan williams")
2. System finds multiple matches and speaks options
3. System says "Say 'next' for more"
4. User says/types a number (e.g., "4")
5. **System does not respond**

## Expected Behavior

- System should process the selection (number "4")
- Play the selected item
- Return to listening mode

## Actual Behavior

- System appears frozen/unresponsive
- No feedback to user input
- State appears stuck in `STATE_WAITING_SELECTION`

## Debug Information

**Log Output:**
```
Wake word detected! Command: 'play vaughan williams'
DEBUG: Music command, trying Ollama: 'play vaughan williams'
DEBUG: Cache hit for: 'play vaughan williams'
INFO: Ollama: play_artist (confidence: 0.95)
🗣 Queued to speak: Searching for vaughan williams
🗣 Speaking (Piper): Searching for vaughan williams
🗣 Queued to speak: Page 1. Found 10 matches. 1. Artist: Vaughan Williams, ...
🗣 Speaking (Piper): Page 1. Found 10 matches. ...
4  # <--- User input here, no response
```

## Hypothesis

~~Possible causes:~~
~~1. Wake word requirement~~
~~2. Console input not being captured~~
~~3. State machine timeout~~
~~4. Voice vs keyboard input~~

## ✅ **ROOT CAUSE IDENTIFIED**

**TTS Blocking During Selection**

The issue is a timing/threading problem:

1. System speaks long selection list (blocking TTS call on line 766 of tuxtalks.py)
2. User types "4" + Enter **while TTS is still speaking**
3. Console input thread reads "4" and calls `process_command("4")`
4. Selection handler processes correctly BUT:
   - Any feedback/confirmation speech is queued behind ongoing TTS
   - Visual feedback may be minimal
   - Appears unresponsive to user

**Why voice input works:**
- Voice input waits for TTS to finish (ASR is paused during TTS)
- User naturally waits for system to stop talking before speaking
- Selection is processed after TTS completes

**Why console input appears broken:**
- User can type immediately (no natural waiting)
- No visual indicator that input was received
- Command processes but feedback is delayed/invisible

## Proposed Fix

**Option 1: Interruptible TTS (Recommended)**
```python
# Allow console input to interrupt TTS when in selection mode
if self.state == STATE_WAITING_SELECTION and console_input_detected:
    assistant.tts.stop()  # Interrupt TTS
    process_selection()
```

**Option 2: Visual Feedback**
```python
# Show immediate console feedback for selections
print(f"✅ Selection received: '{text}' (processing...)")
```

**Option 3: Non-blocking TTS**
- Make TTS.speak() non-blocking
- Use threading for TTS playback
- More complex but cleanest solution

**Recommended: Option 2** (simplest, no breaking changes)

## ✅ Fix Implemented

**Date:** 2025-12-12  
**Solution:** Option 1 - TTS Interruption (+ Option 2 visual feedback)
**File Modified:** `tuxtalks.py` (lines 371-380)

**Change:**
```python
# When selection is received, interrupt TTS immediately
if self.state == self.STATE_WAITING_SELECTION:
    # Interrupt TTS if it's speaking (allows instant CLI selection)
    if hasattr(self, 'tts') and self.tts:
        try:
            self.tts.stop()  # Stop ongoing TTS playback
            print(f"🔇 TTS interrupted by selection")
        except:
            pass
    
    print(f"✅ Selection received: '{text}' (processing...)")
    self.handle_selection(text)
    # Process selection...
```

**User Experience:**
```
TuxTalks: "1. Vaughan Williams, 2. Composer Vaugh..."
User: [types "3" + Enter]
TuxTalks: [STOPS speaking immediately]
Console: "🔇 TTS interrupted by selection"
Console: "✅ Selection received: '3' (processing...)"
TuxTalks: [Starts playing #3]
```

**Impact:**
- ✅ **Instant response** - No waiting for TTS to finish
- ✅ **Natural UX** - Hear item you want, press number, it plays immediately  
- ✅ **CLI-friendly** - Quick keyboard controls work as expected
- ✅ **Voice still works** - Doesn't break voice input (ASR is paused during TTS anyway)

**Testing:** ✅ **VERIFIED** (2025-12-12)

**Test Results:**
- ✅ Console input captured correctly
- ✅ TTS interrupted immediately when selection typed
- ✅ Selection processed instantly
- ✅ Music started playing without delay
- ✅ No orphaned input in bash after exit

**Conclusion:** Bug fully resolved. CLI selection now works as intended.

---

## Workaround

**Try these alternatives:**
1. Say the wake word first: "Alice 4"
2. Use voice instead of typing: Say "four" out loud
3. Say "play number 4"
4. Say "option 4"

## Next Steps

1. Add debug logging to show current state when input is received
2. Check if console input is being read during `STATE_WAITING_SELECTION`
3. Verify selection_handler.handle_selection_command() is being called
4. Add timeout feedback ("Still waiting for your selection...")

## Proposed Fix

Add explicit feedback when in selection mode:
- Visual indicator showing "Waiting for selection..." in console
- Periodic reminder if no input received within 10s
- Clear documentation of input methods (voice, keyboard, wake word requirements)

---

**Tester:** startux  
**Platform:** Linux (Garuda)  
**Input Method:** Console (typed "4")  
**ASR Engine:** Wyoming/Faster-Whisper  
**TTS Engine:** Piper
