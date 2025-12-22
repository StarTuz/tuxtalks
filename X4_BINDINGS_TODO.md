# X4 Foundations - Bindings Configuration TODO

**Date Created:** 2025-12-12  
**Priority:** Medium  
**Status:** 🟡 Pending Review  
**Game:** X4 Foundations (GOG) - Native

---

## Issue Summary

During pre-beta testing session, user identified missing keybindings in the X4 Foundations profile. Several critical voice commands are configured but show **"NOT BOUND"** in the game's inputmap.xml, preventing voice control functionality.

---

## Missing Bindings Identified

### ⚠️ Critical (Game Control)
- **Stop Engines** (Standard)
  - Voice Commands: "stop engines, stop, all stop"
  - Current State: `NOT BOUND`
  - Impact: Cannot stop ship via voice

- **Stop Engines (Decel)**
  - Voice Commands: "stop engines, stop, all stop"
  - Current State: `NOT BOUND`
  - Impact: Alternative stop method unavailable

### 🔶 Important (Navigation)
- **Travel Mode** (First instance)
  - Voice Commands: "travel mode, engage travel mode"
  - Current State: `NOT BOUND`
  - Note: Second instance is bound to `Shift+1`

- **Scan Mode** (First instance)
  - Voice Commands: "scan mode, scanner"
  - Current State: `NOT BOUND`
  - Note: Second instance is bound to `Shift+1`

- **Long Range Scan** (First instance)
  - Voice Commands: "long range scan, pulse scan"
  - Current State: `NOT BOUND`
  - Note: Second instance is bound to `Shift+2`

---

## Working Bindings (Reference)
✅ **Match Speed** - `Shift+x`  
✅ **Boost Engines** - `Tab`  
✅ **Travel Mode** (variant) - `Shift+1`  
✅ **Scan Mode** (variant) - `Shift+1`  
✅ **Long Range Scan** (variant) - `Shift+2`

---

## Root Cause Analysis

**Hypothesis 1:** Duplicate voice commands pointing to different game actions
- Some commands have 2 entries (e.g., "Travel Mode" appears twice)
- First instance is NOT BOUND, second instance is bound
- May indicate alternative methods or different contexts in X4

**Hypothesis 2:** X4 inputmap.xml key naming mismatch
- TuxTalks expects certain action names that don't exist in X4's config
- Binding parser may be looking for wrong action IDs

**Hypothesis 3:** User has not configured these keys in X4 yet
- Game may have optional/unmapped controls by default
- User needs to set these in X4's in-game keybinding menu first

---

## Proposed Solutions

### Option 1: Auto-Assign Default Keys (Recommended)
- Define sensible default keys for NOT BOUND actions
- Write these defaults to inputmap.xml on first detection
- Warn user via GUI notification
- **Pros:** Automated, frictionless
- **Cons:** Might conflict with existing user bindings

### Option 2: Interactive Binding Wizard
- Detect NOT BOUND actions on game detection
- Prompt user to press desired key for each action
- Update inputmap.xml immediately
- **Pros:** User control, no conflicts
- **Cons:** Requires user interaction

### Option 3: Smart Duplicate Consolidation
- If two identical voice commands exist, bind both to same key
- "travel mode" → Bind both instances to `Shift+1`
- **Pros:** Quick fix, maintains consistency
- **Cons:** May not respect X4's context differences

### Option 4: Manual Binding via TuxTalks GUI
- User right-clicks NOT BOUND items in Bindings tab
- Selects "Edit Mapped Key" and presses desired key
- System updates inputmap.xml
- **Pros:** Full control, existing workflow
- **Cons:** User must do it manually

---

## Recommended Action Plan

1. **Immediate (Next Session):**
   - Investigate why duplicate voice commands exist
   - Check X4 inputmap.xml structure for action naming
   - Verify if these actions are context-specific (Ship vs SRV-like modes)

2. **Short-term (Pre-Beta Testing):**
   - Implement Option 3 (Smart Duplicate Consolidation) as quick fix
   - Document X4-specific binding quirks
   - Add warning in GUI when NOT BOUND actions detected

3. **Long-term (Post-Beta):**
   - Implement Option 2 (Interactive Binding Wizard) for new users
   - Add X4 "Recommended Bindings" preset
   - Create troubleshooting guide for common X4 binding issues

---

## Files to Review
- `game_manager.py` - Binding parser for X4
- `games/x4_foundations.py` - X4 profile definition
- `X4 Macro 1.json` - User's macro profile
- `~/.../.../X4/inputmap.xml` - X4's actual keybind config

---

## Testing Checklist (When Fixed)
- [ ] All voice commands trigger correct in-game actions
- [ ] No "NOT BOUND" warnings in Bindings tab
- [ ] Duplicate commands consolidated or explained
- [ ] No key conflicts with user's existing bindings
- [ ] inputmap.xml updated correctly

---

## Notes
- User is currently in X4 Foundations (GOG) - Native version
- Game process detected successfully (inputmap.xml found)
- This is part of **Pre-Beta Test & Learning Cycle** (Day 2)
- Related to overall game integration testing

---

**Next Review:** When user returns to X4 binding configuration  
**Blocked By:** None (can be worked on anytime)  
**Blocks:** Full X4 voice control functionality
