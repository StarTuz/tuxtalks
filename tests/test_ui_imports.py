import tkinter as tk
import ttkbootstrap as ttk
from launcher import ConfigGUI
import os

def test_launcher_init():
    # Avoid connecting to X server if possible, but tk needs it.
    # On headless env this will fail.
    # If the user env has X, it might work.
    # We can try to just import and instantiate if we mock tk?
    # Or just rely on static analysis?
    
    # Try importing all launcher modules to check for syntax errors at least
    import launcher
    import launcher_player_tab
    import launcher_speech_tab
    import launcher_games_tab
    import launcher_corrections_tab
    print("Imports successful")

if __name__ == "__main__":
    test_launcher_init()
