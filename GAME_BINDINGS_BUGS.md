# Game Bindings UI - Active Bugs

**Date:** 2025-12-12  
**Session:** Post-rename from "Binds" to "Game Bindings"  
**Priority:** High

---

## BUG #1: Name Input Ignored in Add Dialog

**Severity:** Medium  
**Status:** 🔴 Active

### Symptoms:
- User enters "test" in Configuration Name field
- Profile created as "X4 Foundations (GOG) (Custom)" instead
- "Custom" is the default value, suggesting input not being read

### Steps to Reproduce:
1. Click "Add Bind"
2. Dialog opens with "Configuration Name" field showing "Custom"
3. User types "test" replacing "Custom"
4. Clicks "Create Game Binding"
5. Profile created with name "Custom" not "test"

### Root Cause:
Unknown - need to investigate if:
- Entry widget not binding correctly to `name_var`
- Value being reset between entry and save
- Dialog being created/reused incorrectly

### Files Involved:
- `launcher_games_tab.py` - `AddProfileDialog.__init__`, `save_profile`

---

## BUG #2: Remove Bind Not Working

**Severity:** High  
**Status:** 🔴 Active (Partially fixed)

### Symptoms:
- User selects a game binding in dropdown
- Clicks "Remove Bind"
- Confirmation dialog appears
- User confirms
- Success message shows
- Profile STAYS in dropdown (not removed)

### Previous Fix Attempt:
- Fixed `get_active_profile()` to handle display name mapping
- Should have resolved "No profile selected" error
- Appears removal is happening but UI not refreshing properly

### Possible Causes:
1. Profile removed from `gm.profiles` but not from UI
2. `full_refresh_command()` not rebuilding dropdown correctly
3. Display name mapping not being cleared after removal
4. Duplicate profile being selected (not the one user thinks)

### Files Involved:
- `launcher_games_tab.py` - `remove_profile_command`, `get_active_profile`, `refresh_profile_list`

---

## BUG #3: UI Corruption After Default Binds

**Severity:** Medium  
**Status:** 🔴 Active

### Symptoms:
- User clicks "Default Binds" button
- Multiple profiles imported (inputmap.xml, inputmap_1.xml, inputmap_2.xml)
- Game Bindings dropdown shows garbled text: "X4 Fou**ndations (GOG) (Custom)**"
- Text appears to be overlapping/truncated
- Selecting any other binding clears the corruption

### Evidence from Screenshots:
**Screenshot 1** (corrupted state):
```
Game Bindings: X4 Foundations (GOG) (Custom)  ← Overlapping text visible
```

**Screenshot 2** (dropdown opened):
```
Game Bindings dropdown shows:
- inputmap.xml
- inputmap_1.xml
- inputmap_2.xml
```

### Root Cause Hypothesis:
1. `import_defaults_command()` creates multiple profiles
2. `full_refresh_command()` called
3. `refresh_profile_list()` rebuilds `profile_display_map`
4. Display name logic failing for imported profiles
5. Dropdown widget getting cached/stale value

### Display Name Mapping Issue:
Current logic strips group name to create display:
```python
# Real name: "X4 Foundations (GOG) (inputmap.xml)"
# Display: "inputmap.xml"  ← What it should be

# But if logic fails:
# Display: "X4 Foundations (GOG) (Custom)"  ← Full name leaking through
```

### Files Involved:
- `launcher_games_tab.py` - `import_defaults_command`, `refresh_profile_list`, `on_game_select`

---

## Root Cause Analysis - Display Name Mapping

### The Problem:
The `profile_display_map` system has race conditions and inconsistencies:

1. **Created in:** `on_game_select()` and `refresh_profile_list()`
2. **Used in:** `get_active_profile()`, `remove_profile_command()`
3. **Cleared/Reset:** Only when game selection changes or refresh

### When It Breaks:
- After `Default Binds` import → Multiple profiles added
- `full_refresh_command()` → `refresh_profile_list()` → `on_game_select()`
- If `profile_display_map` not fully rebuilt, stale mappings persist
- UI shows old display names but dropdown has new values

---

## Recommended Fix Approach

### Short-term (Immediate):
1. **Add logging** to track when `profile_display_map` is rebuilt
2. **Force clear** `profile_display_map` at start of `refresh_profile_list()`
3. **Verify** dropdown values match map keys after rebuild

### Medium-term (Stable):
1. **Centralize** display name logic into a single method
2. **Always** rebuild map when profile list changes
3. **Add** validation: dropdown values must exist in map

### Long-term (Robust):
1. **Eliminate** display name mapping entirely
2. **Use** full profile names everywhere
3. **Add** tooltips to show full path/details
4. **OR:** Store display name in profile object itself

---

## Testing Checklist

After fixes applied:

- [ ] Can create game binding with custom name (not "Custom")
- [ ] Custom name appears correctly in dropdown
- [ ] Can delete game binding
- [ ] Game binding actually removed from list
- [ ] Can import default binds
- [ ] All imported bindings show correct display names
- [ ] No UI corruption after import
- [ ] Selecting different bindings works smoothly
- [ ] No "No profile selected" errors

---

## Priority Actions

1. **DEBUG BUG #1:** Add print statements in `AddProfileDialog.save_profile()` to see what `variant` actually contains
2. **DEBUG BUG #2:** Add logging in `remove_profile_command()` to verify profile is actually removed from `gm.profiles`
3. **DEBUG BUG #3:** Add logging to `refresh_profile_list()` to see `profile_display_map` contents after rebuild

---

**Status:** Multiple interconnected bugs - need systematic debugging approach
