# Smart Command Routing - Design Document

**Date:** 2025-12-12  
**Feature:** Game-Mode-Aware Music Command Routing  
**Status:** ✅ Implemented

## Problem Statement

Users sometimes speak fast enough that music commands trigger the "fast keyword" path intended for game commands. This creates two issues:

1. **Out of game:** Fast keywords might misinterpret music requests, reducing accuracy
2. **In game:** Music requests might accidentally trigger game commands (dangerous!)

Example scenario:
```
User: "Alice play landing gear" (meant: "play Pink Floyd song Landing Gear")
System: Uses fast keywords for game commands
Result: Deploys landing gear in Elite Dangerous! ❌
```

## Solution: Three-Tier Smart Routing

### Tier 1: Simple Controls (Always Fast)
**Examples:** "next", "pause", "stop", "volume up"

**Routing:** Always use fast keywords (<100ms)

**Rationale:** 
- These are unambiguous - no risk of game command confusion
- Speed is critical for user experience
- Work identically in all contexts

```python
SIMPLE_CONTROLS = [
    "next", "previous", "pause", "stop", "resume",
    "volume up", "volume down", "louder", "quieter",
    "what's playing", "what is playing"
]

if text in SIMPLE_CONTROLS:
    # Fast keyword path
    return handle_media_control(text)
```

---

### Tier 2: Complex Queries While Gaming (Force Ollama)
**Examples:** "play beethoven", "search for jazz"

**Context:** Game mode enabled

**Routing:** Force Ollama LLM path (2s latency OK)

**Rationale:**
- Gaming = hands on controls, risk of accidental game commands
- 2s latency acceptable when gaming (user focused on game, not music)
- Ollama prevents misrouting music → game commands
- Natural language understanding prevents "landing gear" being interpreted as a game command

```python
is_gaming = game_manager.game_mode_enabled

if is_gaming and is_music_command:
    logger.debug("Music command while gaming, forcing Ollama")
    # Must use Ollama for safety
    result = ollama.extract_intent(text)
    # ... execute if confident ...
```

---

### Tier 3: Complex Queries Not Gaming (Ollama + Keyword Fallback)
**Examples:** "play beethoven", "search for jazz"

**Context:** Game mode disabled

**Routing:** Try Ollama, allow keyword fallback if unavailable

**Rationale:**
- Not gaming = casual music listening, speed matters
- Ollama preferred for accuracy (passive learning!)
- Keyword fallback if Ollama slow/unavailable
- Risk of misrouting is low (no game commands active)

```python
if not is_gaming and is_music_command:
    logger.debug("Music command (not gaming), trying Ollama with keyword fallback")
    
    # Try Ollama
    if ollama_available:
        result = ollama.extract_intent(text)
        if result.success:
            return execute_intent(result)
    
    # Fallback to keywords (fast)
    return handle_playback_command(text)
```

---

## Behavior Matrix

| Command Type | Game Mode | Routing | Latency | Safety |
|-------------|-----------|---------|---------|--------|
| Simple control ("next") | Any | Keywords | <100ms | ✅ Safe |
| Complex query | Enabled | Ollama only | ~2s | ✅ Safe |
| Complex query | Disabled | Ollama + fallback | <500ms | ⚠️ Medium |
| Game command | Any | Keywords | <100ms | ✅ Safe |

---

## Implementation Details

### File Modified
`core/command_processor.py` - `process()` method

### Code Flow
```python
def process(text):
    # 1. Simple control check
    if text in SIMPLE_CONTROLS:
        return handle_fast_keywords()
    
    # 2. Detect music vs game/system
    is_music = quick_media_check(text)
    
    if is_music:
        # 3. Check gaming context
        if game_manager.game_mode_enabled:
            # Tier 2: Force Ollama
            return ollama_only(text)
        else:
            # Tier 3: Ollama + fallback
            return ollama_with_fallback(text)
    
    # 4. Game/system commands
    return handle_fast_keywords()
```

### Game Mode Detection
```python
is_gaming = self.game_manager.game_mode_enabled
```

This checks the current game mode state, which is toggled by:
- Manual: "Alice enable game mode"
- GUI: Game Mode toggle in settings
- Config: `GAME_MODE_ENABLED` in config file

---

## User Experience

### Casual Music Listening (Game Mode OFF)
```
User: "Alice next"
System: [keywords] → Next track (50ms) ✅

User: "Alice play beethoven"  
System: [Ollama] → "play_artist: beethoven" (1.5s)
System: [fallback if needed] → Keywords (200ms) ✅
```

**Fast when possible, accurate when needed**

---

### Active Gaming (Game Mode ON)
```
User: "Alice next"
System: [keywords] → Next track (50ms) ✅

User: "Alice play beethoven"
System: [Ollama only] → "play_artist: beethoven" (2s) ✅
System: [no keyword fallback] → Won't accidentally trigger "landing gear"
```

**Safety first, prevent game command mishaps**

---

## Benefits

### 1. Safety ✅
- Music commands can't accidentally trigger game commands when gaming
- "play landing gear" won't deploy landing gear in Elite Dangerous

### 2. Speed ✅
- Simple controls always instant (<100ms)
- Complex queries fast when not gaming (<500ms)
- Only slower when gaming (acceptable trade-off for safety)

### 3. Flexibility ✅
- User can toggle game mode on/off as needed
- System adapts automatically to context
- No manual configuration required

### 4. Learning ✅
- Ollama path still used frequently
- Passive voice learning continues to improve
- Keyword fallback prevents feature degradation

---

## Edge Cases

### Ollama Unavailable
If Ollama is unavailable (service down, timeout exceeded):
- **Gaming:** Falls back to keywords (logs warning)
- **Not Gaming:** Falls back to keywords immediately

### Game Mode Forgotten
If user forgets to enable game mode:
- **Risk:** Music →game misrouting possible
- **Mitigation:** Simple controls always safe
- **Solution:** UI reminder to enable game mode when launching games

### Fast Speech
If user speaks very fast:
- **Before:** Fast keywords often triggered
- **After:** 
  - Gaming: Ollama parsing (more accurate)
  - Not Gaming: Keyword fallback still available

---

## Testing Recommendations

1. **Test simple controls:** Verify always <100ms (both modes)
2. **Test complex queries (gaming):** Verify Ollama only
3. **Test complex queries (not gaming):** Verify Ollama + fallback
4. **Test mode switching:** Toggle game mode mid-session
5. **Test Ollama unavailability:** Kill Ollama service, verify fallback

---

## Future Enhancements

### Automatic Game Detection
```python
# Auto-enable game mode when game detected
if elite_dangerous_running():
    game_manager.set_enabled(True)
```

### Confidence Feedback
```python
# Let user know when using fallback
if not using_ollama and is_gaming:
    logger.warning("Music command while gaming but Ollama unavailable!")
```

### Per-Game Override
```python
# Some games need strict Ollama, others can use keywords
if game == "elite_dangerous":
    force_ollama = True
elif game == "x4_foundations":
    force_ollama = False  # Music unlikely to conflict
```

---

*Document created: 2025-12-12*  
*Author: Antigravity*  
*Version: 1.0*
