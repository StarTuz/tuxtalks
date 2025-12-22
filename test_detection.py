import sys
import os
import unittest.mock

# Mock pynput
sys.modules['pynput'] = unittest.mock.MagicMock()
sys.modules['pynput.keyboard'] = unittest.mock.MagicMock()

sys.path.append(os.getcwd())

try:
    from game_manager import X4Profile
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

print("--- Testing X4 Profile Detection ---")
try:
    profile = X4Profile()
    path = profile._detect_x4_folder()
    print(f"Result: {path}")
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
