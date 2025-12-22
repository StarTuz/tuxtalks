# Pre-Beta Testing Quick Reference

## What to Watch For During Testing

### ✅ Good Signs
- Voice patterns accumulating in fingerprint (check Voice Training tab)
- Ollama correctly routing music vs game commands
- No application crashes or freezes
- Response time stays consistent (<2s for Ollama, <100ms for keywords)
- IPC communication working (if using runtime menu/CLI integration)

### ⚠️ Red Flags
- Application crashes or hangs
- Voice fingerprint data loss or corruption
- Ollama routing wrong (music commands going to game, vice versa)
- Memory usage growing over time (memory leak)
- Response time degrading over session
- IPC errors or timeouts

### 💡 CLI Selection Behavior
When testing selections in CLI mode:
- ✅ **You can interrupt TTS** - Type selection number while TTS is reading options
- ✅ **Instant response** - TTS stops immediately, selection processes
- ✅ **Playback announcement** - System announces what's playing after selection
- 📖 See `docs/CLI_Selection_UX.md` for complete UX documentation

---

## Quick Commands

### Check Voice Fingerprint Status
```bash
cat ~/.local/share/tuxtalks/voice_fingerprint.json | jq
```

### View Current Patterns
```bash
# Count patterns
cat ~/.local/share/tuxtalks/voice_fingerprint.json | jq '.asr_patterns | length'

# List all patterns
cat ~/.local/share/tuxtalks/voice_fingerprint.json | jq '.asr_patterns | keys'
```

### Check Logs
```bash
# Main application log
tail -f ~/.local/share/tuxtalks/logs/tuxtalks.log

# Wyoming ASR server log (if using)
tail -f /path/to/wyoming/server.log
```

### Monitor Memory Usage
```bash
# Check TuxTalks memory usage
ps aux | grep tuxtalks | grep -v grep

# Continuous monitoring
watch -n 5 "ps aux | grep tuxtalks | grep -v grep"
```

---

## Testing Checklist

### Daily Testing (Each Gaming Session)

**Before Starting:**
- [ ] Check voice fingerprint pattern count
- [ ] Note starting memory usage
- [ ] Verify Ollama is running (if using)

**During Gaming:**
- [ ] Test voice commands in game
- [ ] Try music commands while gaming (test Ollama routing)
- [ ] Use both wake word and PTT modes
- [ ] Note any misrecognitions or errors

**After Gaming:**
- [ ] Check voice fingerprint pattern count (should increase)
- [ ] Check memory usage (shouldn't have grown significantly)
- [ ] Review Voice Training tab for new passive patterns
- [ ] Note any issues in testing journal

---

## Common Scenarios to Test

### Elite Dangerous
1. **Docking Sequence**
   - "Request docking"
   - "Landing gear" 
   - "Flight assist off"
   
2. **Combat**
   - "Hardpoints"
   - "Deploy chaff"
   - "Shield cell"
   
3. **Navigation**
   - "Frame shift drive"
   - "Supercruise"
   - "Jump to [system]"

### X4 Foundations
1. **Ship Control**
   - "Stop engines"
   - "Travel mode"
   - "Autopilot"
   
2. **Menu Navigation**
   - "Open map"
   - "Property owned"
   - "Show missions"

### X-Plane 12
1. **Flight Controls**
   - "Flaps [up/down]"
   - "Gear [up/down]"
   - "Autopilot"
   
2. **Radio**
   - "Toggle radio"
   - "Transponder"

---

## Music Commands to Test (Ollama Routing)

While gaming, try these music commands to verify Ollama routing:
- "Play some jazz"
- "Play Beethoven"
- "Next track"
- "What's playing?"
- "Pause music"

These should be routed to Ollama (not keyword matching) and should work correctly without interfering with game.

---

## Manual Training Workflow

If you encounter a persistently misheard phrase:

1. **Open TuxTalks Launcher**
   ```bash
   tuxtalks-gui
   ```

2. **Navigate to Voice Training Tab**

3. **Click "Train New Command"**

4. **Enter the CORRECT phrase** (e.g., "Cradle of Filth")

5. **Record 5 samples**
   - Speak clearly in natural voice
   - Wait for countdown between samples

6. **Review transcriptions**
   - Check what ASR heard
   - If mostly correct, click "Yes" to save
   - If mostly wrong, click "No" and try again

7. **Verify in patterns list**
   - Should appear in green (manual)
   - Confidence should be 55%
   - Count should be 3 (or 15 if you trained it 5 times)

---

## Success Metrics (After 7 Days)

### Minimum Bar
- [ ] No critical crashes or data loss
- [ ] 20+ voice patterns in fingerprint
- [ ] Can complete full game session without issues

### Good Performance
- [ ] 50+ voice patterns in fingerprint
- [ ] Ollama routing 100% accurate
- [ ] No memory leaks detected
- [ ] Subjectively improved voice recognition

### Excellent Performance
- [ ] 100+ voice patterns in fingerprint
- [ ] Most common commands recognized 90%+ of time
- [ ] System feels "trained to your voice"
- [ ] Rarely need manual training

---

## Issue Reporting Template

If you find a bug, use this template:

```
**Issue:** [Brief description]
**Severity:** Critical / High / Medium / Low
**Frequency:** Every time / Often / Sometimes / Rare
**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [etc]

**Expected Behavior:** [What should happen]
**Actual Behavior:** [What actually happens]
**Log Output:** [Paste relevant logs]
**Voice Fingerprint State:** [Pattern count, any corruption?]
**System Info:** [Memory usage, Ollama status, etc]
```

---

## Emergency Recovery

### If Voice Fingerprint Gets Corrupted
```bash
# Backup current file
cp ~/.local/share/tuxtalks/voice_fingerprint.json \
   ~/.local/share/tuxtalks/voice_fingerprint.json.bak

# Reset to empty
rm ~/.local/share/tuxtalks/voice_fingerprint.json

# Restart TuxTalks - it will create new empty file
```

### If Application Won't Start
```bash
# Check for stuck processes
ps aux | grep tuxtalks

# Kill all TuxTalks processes
pkill -9 -f tuxtalks

# Clear Python cache
cd ~/code/tuxtalks
find . -type d -name __pycache__ -exec rm -rf {} +

# Reinstall
pipx install -e . --force

# Try starting again
cd ~ && tuxtalks-gui
```

---

## End of Testing Report Template

After 7-14 days of testing, compile this report:

```markdown
# Pre-Beta Testing Results

**Testing Period:** [Start Date] to [End Date]
**Total Gaming Hours:** [Approximate]
**Games Tested:** Elite Dangerous / X4 / X-Plane 12

## Voice Fingerprint Statistics
- **Total Patterns:** [Count]
- **Passive Patterns:** [Count]
- **Manual Patterns:** [Count]
- **Average Confidence:** [%]

## Critical Issues Found
- [List any critical bugs]
- [None if testing went smoothly]

## Non-Critical Issues
- [UI improvements]
- [Performance observations]
- [Feature requests]

## Subjective Assessment
- **Voice Recognition Accuracy:** [Improved / Same / Worse]
- **System Stability:** [Excellent / Good / Fair / Poor]
- **Ollama Routing:** [Perfect / Good / Needs Work]
- **Overall Experience:** [Love it / Like it / Neutral / Dislike it]

## Recommendations
- [Ready for QA Checkpoint A / Needs more testing / Critical issues must be fixed]
```

---

*Quick Reference created: 2025-12-11*  
*Phase: Pre-Beta Test & Learning Cycle*  
*Happy Testing! 🚀*
