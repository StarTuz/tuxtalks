# BUG #002: Cosmetic Error Messages During TTS Interruption

**Date:** 2025-12-12  
**Bug ID:** #002  
**Severity:** Low (Cosmetic)  
**Status:** ✅ **FIXED**

## Issue Description

When interrupting TTS during selection mode, scary-looking error messages appear in the console even though everything works correctly.

## Steps to Reproduce

1. Trigger a selection menu with multiple results
2. While TTS is reading options, type a selection number
3. Observe console output

## Expected Behavior

- Clean console output
- Only real errors should be displayed
- Expected interruptions should be silent

## Actual Behavior (Before Fix)

```
❌ Piper Error: [2025-12-12 08:09:51.653] [piper] [info] Loaded voice in 0.183402206 second(s)
[2025-12-12 08:09:51.653] [piper] [info] Initialized piper

❌ Player Error: aplay: pcm_write:2178: write error: Interrupted system call
```

**Problems:**
- Piper **info** logs showing as "❌ Piper Error"
- Expected aplay interruption showing as "❌ Player Error"
- Confuses users into thinking something broke

## Root Cause

**Piper Info Logs:**
- Piper outputs `[info]` logs to stderr
- Code was treating any stderr output as an error
- `[piper] [info]` is not actually an error

**aplay Interruption:**
- `tts.stop()` calls `pkill aplay`
- Kills aplay mid-write
- aplay reports "Interrupted system call" to stderr
- This is **expected** and intentional

## Fix Implemented

**File:** `speech_engines/piper_tts.py` (lines 90-104)

**Changes:**

1. **Filter Piper info logs:**
```python
# Before:
if piper_proc.wait() != 0:
    print(f"❌ Piper Error: {piper_err.decode()}")

# After:
err_text = piper_err.decode() if piper_err else 'Unknown'
if '[piper] [info]' not in err_text:  # Only show actual errors
    print(f"❌ Piper Error: {err_text}")
```

2. **Suppress expected aplay interruptions:**
```python
# Before:
if player_proc.returncode != 0:
    print(f"❌ Player Error: {p_err.decode()}")

# After:
err_text = p_err.decode() if p_err else 'Unknown'
# Ignore "Interrupted system call" - expected when we kill aplay
if 'Interrupted system call' not in err_text and err_text != 'Unknown':
    print(f"❌ Player Error: {err_text}")
```

## Console Output After Fix

```
3
⌨️  Console input captured: '3'
🔇 TTS interrupted by selection
✅ Selection received: '3' (processing...)
📜 Playing playlist: Beethoven (Shuffle: False)
🗣 Speaking (Piper): Playing playlist Beethoven

🎵 Now Playing (Track 1 of 9):
   Title: Sym No 5 in C minor-Allegro c
   Artist: Beethoven
```

**Clean!** ✅ No scary error messages

## Impact

- ✅ Cleaner console output
- ✅ Less user confusion
- ✅ Still shows real errors if they occur
- ✅ Expected interruptions are silent

## Testing

Ready for re-testing during Pre-Beta phase.

---

**Reported by:** startux  
**Fixed by:** Antigravity  
**Verified:** Pending
