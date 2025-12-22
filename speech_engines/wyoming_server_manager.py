"""
Wyoming Server Manager
Handles lifecycle management for Wyoming protocol servers (e.g., wyoming-faster-whisper).
"""
import subprocess
import socket
import time
import os
import pathlib
import shutil


def is_server_running(host="127.0.0.1", port=10301, timeout=0.5):
    """
    Check if a Wyoming server is running on the specified host:port.
    
    Args:
        host: Server hostname
        port: Server port number
        timeout: Socket connection timeout in seconds
    
    Returns:
        bool: True if server is reachable, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_wyoming_whisper(config):
    """
    Start a wyoming-faster-whisper server process.
    
    Args:
        config: Config object with Wyoming settings
    
    Returns:
        subprocess.Popen: Process handle if successful, None if failed or already running
    """
    # Check if already running
    port = config.get("WYOMING_PORT", 10301)
    host = config.get("WYOMING_HOST", "127.0.0.1")
    if host == "localhost":
        host = "127.0.0.1"
    
    if is_server_running(host, port):
        print(f"log: Wyoming server already running on {host}:{port}")
        return None
    
    # Check if wyoming-faster-whisper is installed
    if not shutil.which("wyoming-faster-whisper"):
        print("err: wyoming-faster-whisper not found in PATH. Please install it:")
        print("    pip install wyoming-faster-whisper")
        return None
    
    # Get configuration
    model = config.get("WYOMING_MODEL", "tiny")
    device = config.get("WYOMING_DEVICE", "cpu")
    compute_type = config.get("WYOMING_COMPUTE_TYPE", "int8")
    language = config.get("WYOMING_LANGUAGE", "en")
    beam_size = config.get("WYOMING_BEAM_SIZE", 1)
    
    # Data directory setup
    data_dir = config.get("WYOMING_DATA_DIR")
    if not data_dir:
        data_dir = str(pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "wyoming-data")
    
    os.makedirs(data_dir, exist_ok=True)
    
    # Log file setup
    log_dir = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "wyoming_server.log"
    
    # Build command
    cmd = [
        "wyoming-faster-whisper",
        "--uri", f"tcp://{host}:{port}",
        "--model", model,
        "--language", language,
        "--device", device,
        "--compute-type", compute_type,
        "--beam-size", str(beam_size),
        "--data-dir", data_dir
    ]
    
    print(f"log: Starting Wyoming Whisper server...")
    print(f"     Host: {host}:{port}")
    print(f"     Model: {model}")
    print(f"     Device: {device} ({compute_type})")
    print(f"     Data: {data_dir}")
    print(f"     Log: {log_file}")
    
    try:
        # Open log file for output
        log_fd = open(log_file, "a")
        log_fd.write(f"\n{'='*60}\n")
        log_fd.write(f"Wyoming Server Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_fd.write(f"Command: {' '.join(cmd)}\n")
        log_fd.write(f"{'='*60}\n\n")
        log_fd.flush()
        
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=log_fd,
            stderr=subprocess.STDOUT,
            start_new_session=True  # Detach from parent process group
        )
        
        # Wait briefly to check if it started successfully
        time.sleep(1.5)
        
        if process.poll() is not None:
            # Process already exited
            print(f"err: Wyoming server failed to start (exit code: {process.returncode})")
            print(f"     Check log: {log_file}")
            log_fd.close()
            return None
        
        # Verify server is responding
        max_wait = 10
        for i in range(max_wait):
            if is_server_running(host, port):
                print(f"log: Wyoming server started successfully (PID: {process.pid})")
                return process
            time.sleep(0.5)
        
        # Timeout waiting for server
        print(f"err: Wyoming server started but not responding on {host}:{port}")
        print(f"     Check log: {log_file}")
        process.terminate()
        log_fd.close()
        return None
        
    except Exception as e:
        print(f"err: Failed to start Wyoming server: {e}")
        return None


def stop_server(process):
    """
    Gracefully stop a Wyoming server process.
    
    Args:
        process: subprocess.Popen object
    """
    if not process:
        return
    
    try:
        print(f"log: Stopping Wyoming server (PID: {process.pid})...")
        
        # Try graceful termination first
        process.terminate()
        
        # Wait up to 5 seconds for clean shutdown
        try:
            process.wait(timeout=5)
            print("log: Wyoming server stopped gracefully")
        except subprocess.TimeoutExpired:
            # Force kill if not responding
            print("warn: Wyoming server not responding, forcing shutdown...")
            process.kill()
            process.wait()
            print("log: Wyoming server killed")
            
    except Exception as e:
        print(f"warn: Error stopping Wyoming server: {e}")
