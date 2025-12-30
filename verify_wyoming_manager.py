#!/usr/bin/env python3
"""
Test script for Wyoming server manager.
Tests the auto-start/stop functionality without launching full TuxTalks.
"""
import sys
import time
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from speech_engines import wyoming_server_manager
from config import cfg

def test_server_detection():
    """Test 1: Server detection"""
    print("\n" + "="*60)
    print("TEST 1: Server Detection")
    print("="*60)
    
    host = "127.0.0.1"
    port = 10301
    
    print(f"Checking for Wyoming server on {host}:{port}...")
    is_running = wyoming_server_manager.is_server_running(host, port)
    
    if is_running:
        print("✅ Server detected!")
    else:
        print("❌ Server not detected")
    
    return is_running

def test_server_start():
    """Test 2: Server auto-start"""
    print("\n" + "="*60)
    print("TEST 2: Server Auto-Start")
    print("="*60)
    
    print("Attempting to start Wyoming server...")
    process = wyoming_server_manager.start_wyoming_whisper(cfg)
    
    if process:
        print(f"✅ Server started successfully (PID: {process.pid})")
        return process
    else:
        print("❌ Failed to start server")
        return None

def test_server_stop(process):
    """Test 3: Server auto-stop"""
    print("\n" + "="*60)
    print("TEST 3: Server Auto-Stop")
    print("="*60)
    
    if not process:
        print("⚠️  No process to stop (skipping)")
        return
    
    print("Stopping Wyoming server...")
    wyoming_server_manager.stop_server(process)
    
    # Wait and verify it's stopped
    time.sleep(1)
    
    if wyoming_server_manager.is_server_running("127.0.0.1", 10301):
        print("❌ Server still running!")
    else:
        print("✅ Server stopped successfully")

def main():
    print("\n" + "="*60)
    print("Wyoming Server Manager - Test Suite")
    print("="*60)
    
    # Test 1: Detection
    initially_running = test_server_detection()
    
    if initially_running:
        print("\n⚠️  Server is already running.")
        print("   To test auto-start, please stop it first:")
        print("   pkill -f wyoming-faster-whisper")
        print("\n   Then run this test again.")
        return
    
    # Test 2: Start
    process = test_server_start()
    
    if not process:
        print("\n❌ Cannot continue - server failed to start")
        print("   Check that wyoming-faster-whisper is installed:")
        print("   pip install wyoming-faster-whisper")
        return
    
    # Wait for server to fully initialize
    print("\nWaiting 3 seconds for server to stabilize...")
    time.sleep(3)
    
    # Test 3: Stop
    test_server_stop(process)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Test with actual TuxTalks: tuxtalks")
    print("2. Verify auto-start on launch")
    print("3. Verify auto-stop on exit")

if __name__ == "__main__":
    main()
