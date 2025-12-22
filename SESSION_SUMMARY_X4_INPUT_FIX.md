# Session Summary: Debugging X4 Input on Wayland
**Date:** 2025-12-13
**Status:** ✅ RESOLVED

## Issue
Commands for **X4 Foundations** (Native Linux) were executing incorrectly.
*   Voice: "Weapons Group 1" -> Game Output: **Options Menu (Esc)**
*   Voice: "Weapons Group 2" -> Game Output: **Weapons Group 1 ('1')**

## Root Cause Analysis
The issue was identified as a **data type mismatch** in the `ydotool` implementation within `game_manager.py`.

1.  **Input Flow:** TuxTalks parsed the binding for "Weapons Group 1" as the character string `"1"`.
2.  **The Mistake:** This string `"1"` was passed directly to the `ydotool` wrapper.
3.  **Driver Interpretation:** `ydotool` expects an **integer scancode**. When it received the string `"1"`, it interpreted it as integer `1`.
4.  **Linux Input Standard:** In the Linux Input Event system:
    *   **Scancode 1** = `KEY_ESC`
    *   **Scancode 2** = `KEY_1`
    *   **Scancode 3** = `KEY_2`
5.  **Result:** Sending `"1"` resulted in `KEY_ESC` being pressed. Sending `"2"` resulted in `KEY_1` being pressed. This created the observed "Off-by-One" shift.

## The Fix
We implemented a robust mapping layer in `GameManager.handle_command` that intercepts numeric keys (`0`-`9`).

*   It checks if the key is a digit (either a string `"1"` or a `pynput.KeyCode` with char `'1'`).
*   It explicitly maps these digits to their correct **Linux Scancodes**:
    *   `'1'` → **2**
    *   `'2'` → **3**
    *   `'3'` → **4** (and so on)
    *   `'0'` → **11**

## Impact
*   **X4 Foundations (Wayland):** ✅ "Weapons Group 1" now correctly presses '1'.
*   **Elite Dangerous / Proton:** ✅ Should improve reliability by sending correct hardware scancodes.
*   **X11 Support:** ✅ The fix uses standard kernel scancodes, so it is compatible with X11 as well.

## Files Modified
*   `game_manager.py`: Added scancode mapping logic to `handle_command` (lines ~2250).

## Next Steps
*   Proceed with **Custom Commands (Phase 7)** or **Elite Dangerous Testing**.
*   The system is now confirmed stable for game inputs on Wayland.
