
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch

# Mock Config
class MockConfig:
    def get(self, key, default=None):
        return default
    def set(self, key, val):
        pass
    def save(self):
        pass

# Setup Environment
import sys
import logging
logging.basicConfig(level=logging.WARNING) # Suppress X4Parser info/debug logs

sys.modules['tkinter.messagebox'] = MagicMock()

from launcher_games_tab import LauncherGamesTab

def test_startup():
    print("--- STARTUP SIMULATION ---")
    
    root = tk.Tk()
    
    # Mock Parent
    class MockLauncher:
        def __init__(self):
            self.root = root
            self.config = MockConfig()
            self.games_tab = ttk.Frame(root)
            self.games_tab.pack()
            
    parent = MockLauncher()
    
    # Initialize Tab
    print("Initialized LauncherGamesTab...")
    launcher = LauncherGamesTab()
    
    # Transplant attributes that usually come from mixin or parent
    launcher.games_tab = parent.games_tab
    launcher.root = root
    launcher.config = parent.config
    
    # Run Build
    print("Building Games Tab...")
    launcher.build_games_tab()
    
    print("\n--- FINAL STATE ---")
    if hasattr(launcher, 'gm') and launcher.gm:
        print(f"GM Active Profile: {getattr(launcher.gm.active_profile, 'name', 'None')}")
        print(f"UI Game Combo: {launcher.game_combo.get()}")
        print(f"UI Profile Combo: {launcher.profile_var.get()}")
    
    root.update()
    root.destroy()

if __name__ == "__main__":
    test_startup()
