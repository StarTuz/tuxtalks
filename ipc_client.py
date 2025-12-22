"""
IPC Client for TuxTalks CLI

Implements socket-based IPC client for sending selection requests
to tuxtalks-menu and receiving user selections.
"""

import socket
import json
import os


def get_socket_path():
    """Get platform-appropriate socket path."""
    if os.name == 'posix':
        # Linux/Unix
        return f"/tmp/tuxtalks-menu-{os.getuid()}.sock"
    else:
        # Windows (Named pipe)
        return r"\\.\pipe\tuxtalks-menu"


def is_menu_running():
    """
    Check if tuxtalks-menu is running and accepting connections.
    
    Returns:
        bool: True if menu is available
    """
    socket_path = get_socket_path()
    
    # Check if socket exists
    if not os.path.exists(socket_path):
        return False
    
    # Try to connect
    try:
        test_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        test_socket.settimeout(0.5)
        test_socket.connect(socket_path)
        test_socket.close()
        return True
    except:
        return False


def send_selection_request(title, items, page=1, timeout=180.0):
    """
    Send selection request to menu window.
    
    Args:
        title: Selection title (e.g., "Select Artist")
        items: List of selectable items (strings)
        page: Current page number
        timeout: Timeout in seconds (default: 180s for user to select)
    
    Returns:
        dict: {"index": int, "cancelled": bool} or None if error/timeout
    """
    socket_path = get_socket_path()
    
    print(f"[IPC Client] Waiting for selection (timeout: {timeout:.0f}s)...")
    
    try:
        # Connect to menu
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.settimeout(timeout)
        client_socket.connect(socket_path)
        
        # Send request
        request = {
            'type': 'selection_request',
            'title': title,
            'items': items,
            'page': page
        }
        
        request_data = json.dumps(request).encode('utf-8') + b"\n"
        client_socket.sendall(request_data)
        
        # Receive response
        data = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\n" in data:
                break
        
        if not data:
            return None
        
        # Parse response
        response = json.loads(data.decode('utf-8').strip())
        
        client_socket.close()
        
        return {
            'index': response.get('index', -1),
            'cancelled': response.get('cancelled', True)
        }
        
    except socket.timeout:
        print(f"[IPC Client] ⏱️  Selection timed out after {timeout:.0f} seconds")
        print(f"[IPC Client] You can re-issue the command to see options again")
        try:
            client_socket.close()
        except:
            pass
        return {'index': -1, 'cancelled': True}
    except Exception as e:
        print(f"[IPC Client] Error: {e}")
        return None
