# Feature: Sound Pool (Random/Multi-File Audio)

**Date:** 2025-12-13
**Status:** ✅ Implemented

## 🎯 Objective
Enable advanced audio playback for macros, allowing users to define a "pool" of sound files and choose how they are played (Randomly, Simultaneously, or Sequentially).

## 🛠 Features

### 1. Sound Pool Editor
*   In the **Macro Step Dialog**, users can now add multiple audio files to a list.
*   **Add (+):** Select one or more files from disk.
*   **Remove (-):** Remove selected files from the pool.

### 2. Playback Modes
You can switch the playback behavior for the pool at any time:

*   **🎲 Random (Default):** Picks ONE file from the pool at random each time the macro runs. Great for variety (e.g., "Ferret Squeaks").
*   **📢 Simultaneous:** Plays ALL files in the pool at the same time. useful for layering sounds (e.g., "Siren" + "Warning Voice").
*   **🔄 Sequential (Round-Robin):** Cycles through the list one by one.
    *   *Run 1:* Plays File A
    *   *Run 2:* Plays File B
    *   *Run 3:* Plays File C
    *   *Run 4:* Back to File A

### 3. Usage
1.  Go to **Mappings & Macros**.
2.  Edit or Create a Macro.
3.  Add a Step.
4.  Use the **Sound Pool** section to add files.
5.  Select your desired **Mode**.
6.  Save.

### 4. Technical Details
*   **Data Structure:**
    ```json
    {
      "action": "SomeAction",
      "audio_pool": ["/path/to/sound1.wav", "/path/to/sound2.mp3"],
      "playback_mode": "Sequential (Round-Robin)"
    }
    ```
*   **Backward Compatibility:** Old macros with single `audio_feedback_file` paths continue to work seamlessly. They are treated as a Pool of 1.

### 5. Advanced Capabilities
*   **Audio-Only Steps:** You can leave the "Key to Press" field **blank** if you only want to play audio. This is perfect for immersion scripts (background chatter, ambience) without triggering game inputs.
*   **Clean Slate Profiles:** When you create a new **Custom Macro Profile** (e.g., "X4 Gog2"), it starts **completely empty**. Unlike the default "Custom" profile, it does NOT automatically load the built-in "Care Package" (green items). This allows you to build focused, clutter-free profiles.
*   **Persistence:** Your selected Macro Profile is now saved per-game. If you select "X4 Gog2", TuxTalks will remember and load it automatically next time you launch.
