"""
IPC Server for TuxTalks Runtime Menu

Implements socket-based IPC server for receiving selection requests
from tuxtalks-cli and sending user selections back.
"""

import socket
import json
import os
import threading
from pathlib import Path


class IPCServer:
    """Socket server for runtime menu IPC."""
    
    def __init__(self, callback):
        """
        Initialize IPC server.
        
        Args:
            callback: Function to call when request received.
                     Should accept (title, items, page) and return (index, cancelled)
        """
        self.callback = callback
        self.socket_path = self.get_socket_path()
        self.server_socket = None
        self.running = False
        self.thread = None
        
    @staticmethod
    def get_socket_path():
        """Get platform-appropriate socket path."""
        if os.name == 'posix':
            # Linux/Unix
            return f"/tmp/tuxtalks-menu-{os.getuid()}.sock"
        else:
            # Windows (Named pipe)
            return r"\\.\pipe\tuxtalks-menu"
    
    def start(self):
        """Start listening on socket."""
        # Clean up stale socket
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except:
                pass
        
        # Create socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(1)
        self.running = True
        
        # Start listener thread
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
        print(f"[IPC Server] Listening on {self.socket_path}")
    
    def stop(self):
        """Stop server and clean up."""
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except:
                pass
        
        print("[IPC Server] Stopped")
    
    def _listen_loop(self):
        """Main listener loop (runs in thread)."""
        while self.running:
            try:
                # Accept connection (blocking with timeout)
                self.server_socket.settimeout(1.0)
                try:
                    client_socket, _ = self.server_socket.accept()
                except socket.timeout:
                    continue
                
                # Handle request in a separate thread (non-blocking)
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                print(f"[IPC Server] 🧵 Started client thread {client_thread.name}")
                
            except Exception as e:
                if self.running:
                    print(f"[IPC Server] Error: {e}")
    
    def _handle_client(self, client_socket):
        """Handle single client request."""
        try:
            # Receive data
            data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Check for message end (newline)
                if b"\n" in data:
                    break
            
            if not data:
                return
            
            # Parse JSON
            request = json.loads(data.decode('utf-8').strip())
            
            if request.get('type') == 'selection_request':
                # Extract data
                title = request.get('title', 'Select Item')
                items = request.get('items', [])
                page = request.get('page', 1)
                
                # Call callback (blocks until user selects)
                index, cancelled, child_index = self.callback(title, items, page)
                
                # Get explicit_cancel flag from menu
                from runtime_menu import RuntimeMenu
                explicit_cancel = False
                if hasattr(self.callback, '__self__'):
                    menu = self.callback.__self__
                    if hasattr(menu, 'explicit_cancel'):
                        explicit_cancel = menu.explicit_cancel
                        print(f"[IPC Server] DEBUG: explicit_cancel = {explicit_cancel}")
                    else:
                        print(f"[IPC Server] DEBUG: Menu has no explicit_cancel attribute")
                else:
                    print(f"[IPC Server] DEBUG: Callback has no __self__")
                
                # Send response
                response = {
                    'type': 'selection_response',
                    'index': index,
                    'cancelled': cancelled,
                    'child_index': child_index,  # For hierarchical selections
                    'explicit_cancel': explicit_cancel  # True if user clicked Cancel
                }
                
                response_data = json.dumps(response).encode('utf-8') + b"\n"
                client_socket.sendall(response_data)
            
        except Exception as e:
            print(f"[IPC Server] Client error: {e}")
        finally:
            client_socket.close()
