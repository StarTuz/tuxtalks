# Handoff: Feature "Sound Pool" & Macro Persistence
**Date:** 2025-12-13
**To:** Next Engineer / Future Self

## 🚀 Status: COMPLETE

We have successfully implemented and verified the "Sound Pool" feature and resolved critical issues with Macro Profile persistence.

### ✅ Completed Features

1.  **Sound Pools (Option A):**
    *   **UI:** Implemented `Listbox` based editor in Macro Step dialog (Add/Remove files).
    *   **Modes:** 
        *   `Random` (Dice roll)
        *   `Simultaneous` (Layering)
        *   `Sequential` (Round-Robin with state tracking)
    *   **Immersion:** "Audio Only" steps supported (leave Key blank).

2.  **Macro Profile Persistence:**
    *   **Fix:** Named Custom Profiles (e.g. "X4 Gog2") now **save immediately** upon creation.
    *   **Fix:** The selected profile is **remembered** per-game across restarts.
    *   **Clean Slate:** Named profiles start **empty** (no built-in "Green" macros), respecting user control.

3.  **Documentation:**
    *   Updated `FEATURE_SOUND_POOL.md`
    *   Updated `help_content.py` (In-App Help)
    *   Updated `ROADMAP.md`

### 🧪 Validation
*   [x] Create new profile "X4 Gog2" -> Survives restart.
*   [x] Add "Feed Mango" macro -> Survives restart.
*   [x] Add Sound Pool (3 files) -> Works.
*   [x] Blank Key + Audio -> Works (No error).
*   [x] "Clean Slate" -> "X4 Gog2" has no green macros.

### ⚠️ Note for Future
*   **Initialization Order:** When creating *any* new file-based entity (Profiles, Macros), ensure the `active_ptr` is updated *immediately* in memory, or the next "Save" operation might write to the old pointer. We fixed this in `create_custom_macro_profile`, but keep it in mind for other features.

Ready for next task!
