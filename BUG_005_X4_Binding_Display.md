# BUG #005: X4 Binding Display Issues

**Status:** ✅ RESOLVED  
**Date Reported:** 2025-12-13  
**Date Resolved:** 2025-12-13  
**Severity:** High (Multiple key bindings showing incorrect values)

---

## Summary

X4 Foundations key bindings were displaying incorrect values in TuxTalks, with multiple issues:
1. Weapon groups showing wrong keys (Group 2 showed "1" instead of "2")
2. Missing weapon group commands entirely
3. "Stop Engines" showing as NOT BOUND despite being bound to Backspace
4. Bindings appearing in random order instead of original action_voice_map order

---

## Root Causes

### Issue #1: Scancode Confusion (Primary Bug)
**Location:** `launcher_games_tab.py:2222-2224`

Elite Dangerous uses **integer scancodes** (2 = "1" key, 3 = "2" key), but X4 uses **character strings** ("1", "2", "3"). The code was treating X4's string "2" as scancode 2, which maps to "1" key.

```python
# OLD (BUGGY) CODE
elif isinstance(key_code, str) and key_code.isdigit():
     kc_int = int(key_code)
     if kc_int in start_codes: key_name = start_codes[kc_int]  # Wrong!
```

**Fix:** Removed scancode lookup for string keys - only use it for integer scancodes (Elite Dangerous).

### Issue #2: Missing Action IDs
**Location:** `game_manager.py` (X4Profile)

Missing action IDs in `action_voice_map` and `friendly_name_map`:
- `INPUT_ACTION_STOP` (Backspace)
- `INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_1-4`
- `INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_1-4`
- `INPUT_ACTION_CYCLE_NEXT/PREV_PRIMARY/SECONDARY_WEAPONGROUP`
- `INPUT_ACTION_TOGGLE_AIM_ASSIST`
- `INPUT_ACTION_NEXT_AMMUNITION`
- `INPUT_ACTION_DEPLOY_COUNTERMEASURES`

**Fix:** Added all 18 missing action IDs with voice commands and friendly names.

### Issue #3: Missing Key Mapping
**Location:** `parsers/x4_parser.py:123`

X4's `INPUT_KEYCODE_BACK` wasn't mapped to "Backspace".

**Fix:** Added `"BACK": "Backspace"` to key mapping dictionary.

### Issue #4: Random Display Order
**Location:** `launcher_games_tab.py:1073`

Dictionary iteration order (`friendly_name_groups.items()`) didn't match original `action_voice_map` order.

**Fix:** Track original order in `action_order` list and iterate using that.

### Issue #5: Unnecessary Sorting
**Location:** `launcher_games_tab.py:1074`

Sorting was running on single-item groups (non-duplicates), potentially corrupting data.

**Fix:** Only sort groups with `len(actions) > 1` (actual duplicates).

---

## Files Modified

### 1. `launcher_games_tab.py`
- **Lines 1048-1050:** Added `action_order` list to track original action order
- **Lines 1057-1058:** Track first occurrence of each friendly name
- **Lines 1073-1077:** Only sort multi-item groups, iterate in original order
- **Lines 2219-2223:** Removed scancode lookup for string digit keys

### 2. `game_manager.py` (X4Profile)
- **Lines 462:** Added `INPUT_ACTION_STOP` to `action_voice_map`
- **Lines 476-496:** Added 17 weapon group actions to `action_voice_map`
- **Lines 534-535:** Added `INPUT_ACTION_STOP` to `friendly_name_map`
- **Lines 543-565:** Added 17 weapon group friendly names

### 3. `parsers/x4_parser.py`
- **Line 123:** Added `"BACK": "Backspace"` key mapping

---

## Testing Performed

**Test Environment:** X4 Foundations (GOG) with `inputmap_1.xml`

**Verified Fixes:**
- ✅ Stop Engines displays "Backspace" (not "NOT BOUND")
- ✅ Select Primary Weapon Group 1 displays "1"
- ✅ Select Primary Weapon Group 2 displays "2" (not "1")
- ✅ Select Primary Weapon Group 3 displays "3" (not "2")
- ✅ Select Primary Weapon Group 4 displays "4" (not "3")
- ✅ Select Secondary Weapon Group 1-4 display "5", "6", "7", "8"
- ✅ All bindings appear in original `action_voice_map` order
- ✅ Duplicate bindings (Travel Mode, etc.) show [Primary]/[Secondary] labels correctly

**Debug Output Verified:**
```
DISPLAY REQUEST: WEAPONGROUP_2 → Data: ('2', [])  ✓ Correct from parser
FORMAT RESULT: WEAPONGROUP_2 → key_code=2, key_name=2, result=2  ✓ Correct formatting
```

---

## Lessons Learned

1. **Game-Specific Formats:** Different games use different binding formats (scancodes vs character strings). Guard conversions carefully.
2. **Dictionary Ordering:** Don't rely on dictionary iteration order when original sequence matters - track it explicitly.
3. **Debug Tracing:** Adding debug at multiple stages (fetch → format → display) was crucial to isolating the exact point of corruption.
4. **Avoid Over-Sorting:** Only apply transformations (like sorting) when necessary (multiple items).

---

## Related Issues

- **BUG #004:** Menu stale results (different subsystem)
- **Elite Dangerous Binding Fixes:** Similar action name mapping issues resolved in previous session

---

## Prevention

- Added comments explaining scancode vs character string distinction
- Documented the original order preservation pattern for future reference
- Added 17 new X4 commands to reduce future "NOT BOUND" reports
