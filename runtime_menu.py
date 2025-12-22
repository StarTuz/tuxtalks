"""
TuxTalks Runtime Menu Window

Small, non-blocking GUI for displaying selection options during runtime.
Communicates with tuxtalks-cli via IPC (local sockets).
"""

import tkinter as tk
from tkinter import ttk
import sv_ttk
from ipc_server import IPCServer
from i18n import _, set_language
from config import cfg
import queue
import threading


class RuntimeMenu:
    """Runtime selection menu window with IPC server."""
    
    def __init__(self):
        """Initialize runtime menu."""
        # Load i18n
        set_language(cfg.get("UI_LANGUAGE", "en"))
        
        # Create window
        self.root = tk.Tk()
        self.root.title(_("TuxTalks - Runtime Menu"))
        self.root.geometry("500x400")
        
        # Apply theme
        sv_ttk.set_theme("dark")
        
        # Selection state
        self.current_title = ""
        self.current_items = []
        self.selected_index = -1
        self.selected_child_index = None  # For hierarchical selections
        self.cancelled = True
        self.explicit_cancel = False  # True when user clicks Cancel button
        self.selection_ready = threading.Event()
        self.keep_list_open = tk.BooleanVar(value=False)  # Keep list checkbox state
        
        # Request tracking (for cancelling old requests)
        self.request_id = 0  # Increments with each request
        self.active_request_id = None  # ID of currently displayed request
        self.request_lock = threading.Lock()  # Protects request_id and active_request_id
        
        # Build UI
        self._build_ui()
        
        # IPC server
        self.ipc_server = IPCServer(self._handle_selection_request)
        self.ipc_server.start()
        
        # Request queue (for thread-safe UI updates)
        self.request_queue = queue.Queue()
        self.root.after(100, self._process_queue)
        
        print("[Runtime Menu] Started")
    
    def _build_ui(self):
        """Build the UI."""
        # Title label
        self.title_label = ttk.Label(
            self.root,
            text=_("Waiting for selection..."),
            font=("Helvetica", 14, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Tree frame
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview (replaces Listbox)
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            show='tree'  # Only show tree column, hide headings
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Configure tree appearance
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 11), rowheight=25)
        
        # Bind events
        self.tree.bind('<Double-Button-1>', lambda e: self._on_select())
        self.tree.bind('<Return>', lambda e: self._on_select())
        self.tree.bind('<Escape>', lambda e: self._on_cancel())
        
        # Note: Removed 1-9 keyboard shortcuts as they don't work well with tree structure
        
        # Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text=_("Select"),
            command=self._on_select
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text=_("Cancel"),
            command=self._on_cancel
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text=_("Exit"),
            command=self._on_exit
        ).pack(side=tk.LEFT, padx=5)
        
        # Keep list open checkbox
        ttk.Checkbutton(
            button_frame,
            text=_("Keep list open"),
            variable=self.keep_list_open
        ).pack(side=tk.LEFT, padx=15)
        
        # Status label
        self.status_label = ttk.Label(
            self.root,
            text=_("Hint: Use mouse or voice commands"),
            font=("Helvetica", 9),
            foreground="gray"
        )
        self.status_label.pack(pady=5)
    
    def _handle_selection_request(self, title, items, page):
        """
        Handle IPC selection request (called from IPC thread).
        
        Args:
            title: Selection title
            items: List of items
            page: Page number
        
        Returns:
            (index, cancelled, child_index): User's selection
        """
        # Assign unique request ID
        with self.request_lock:
            my_request_id = self.request_id
            self.request_id += 1
        
        # Create per-request event
        my_event = threading.Event()
        
        print(f"[Runtime Menu] 📨 IPC request #{my_request_id} received: '{title}', {len(items)} items, page {page}")
        print(f"[Runtime Menu] 📊 Queue size before: {self.request_queue.qsize()}")
        
        # Cancel any previous pending request
        if self.active_request_id is not None:
            print(f"[Runtime Menu] ❌ Cancelling previous request #{self.active_request_id}")
            self.cancelled = True
            self.selection_ready.set()  # Wake up old thread
        
        # Reset state for new request
        self.cancelled = True  # Start as cancelled, will be set to False on valid selection
        self.explicit_cancel = False  # Reset cancel flag
        self.selected_index = -1
        self.selected_child_index = None
        
        # CRITICAL: Clear selection_ready for the new request AFTER waking old thread
        self.selection_ready.clear()
        
        # Queue request for main thread (includes our event)
        self.request_queue.put(('request', my_request_id, title, items, page, my_event))
        
        print(f"[Runtime Menu] 📊 Queue size after: {self.request_queue.qsize()}")
        
        # Wait for queue to process and display our request (max 5 seconds)
        print(f"[Runtime Menu] ⏳ Waiting for display (request #{my_request_id})...")
        if not my_event.wait(timeout=5.0):
            print(f"[Runtime Menu] ⚠️  Request #{my_request_id} display timeout!")
            return (-1, True, None)
        
        # Now display is complete, wait for user selection
        print(f"[Runtime Menu] ⏳ Waiting for user selection (request #{my_request_id})...")
        self.selection_ready.wait()
        self.selection_ready.clear()  # Clear for next request
        
        # Check if this request was cancelled by a newer request
        with self.request_lock:
            if self.active_request_id != my_request_id:
                print(f"[Runtime Menu] 🚫 Request #{my_request_id} was superseded by #{self.active_request_id}")
                return (-1, True, None)  # Cancelled
        
        print(f"[Runtime Menu] ✅ Selection completed for request #{my_request_id}: index={self.selected_index}, cancelled={self.cancelled}, child={self.selected_child_index}")
        
        return (self.selected_index, self.cancelled, self.selected_child_index)
    
    def _process_queue(self):
        """Process queued requests (runs in main thread)."""
        try:
            processed = 0
            while not self.request_queue.empty():
                msg = self.request_queue.get_nowait()
                
                if msg[0] == 'request':
                    _, req_id, title, items, page, event = msg
                    print(f"[Runtime Menu] 🔄 Processing queued request #{req_id}: '{title}'")
                    self._display_selection(req_id, title, items, page)
                    # Signal that display is complete
                    event.set()
                    print(f"[Runtime Menu] 🔔 Display complete event signaled for request #{req_id}")
                    processed += 1
            
            if processed > 0:
                print(f"[Runtime Menu] 📦 Processed {processed} request(s) from queue")
        except Exception as e:
            print(f"[Runtime Menu] ❌ Queue processing error: {e}")
        
        # Schedule next check
        self.root.after(100, self._process_queue)
    
    def _display_selection(self, req_id, title, items, page):
        """Display selection options in UI (True hierarchical TreeView)."""
        print(f"[Runtime Menu] 🖥️  _display_selection() called for request #{req_id}")
        print(f"[Runtime Menu]     Title: '{title}'")
        print(f"[Runtime Menu]     Items: {len(items)}")
        print(f"[Runtime Menu]     Item type: {type(items[0]) if items else 'empty'}")
        
        # Set this as the active request
        with self.request_lock:
            self.active_request_id = req_id
        
        self.current_title = title
        self.current_items = items
        
        # Update title
        self.title_label.config(text=f"{title} (Page {page})")
        print(f"[Runtime Menu] 📝 Title updated: '{title} (Page {page})'")
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        print(f"[Runtime Menu] 🗑️  Cleared tree")
        
        # Build tree structure from hierarchical data
        try:
            for i, item_data in enumerate(items):
                # Handle both old format (strings) and new format (dicts)
                if isinstance(item_data, dict):
                    item_text = item_data.get('text', str(item_data))
                    item_type = item_data.get('type', 'simple')
                    children = item_data.get('children', [])
                    
                    # Insert parent node
                    parent_id = self.tree.insert('', 'end', text=f"{i+1}. {item_text}", 
                                                 tags=(f'parent_{i}',))
                    
                    # Insert children if present
                    if children:
                        for j, child_data in enumerate(children):
                            try:
                                child_text = child_data.get('text', str(child_data))
                                self.tree.insert(parent_id, 'end', text=child_text,
                                               tags=(f'child_{i}_{j}',))
                            except Exception as e:
                                print(f"[Runtime Menu] ⚠️  Error adding child {j}: {e}")
                        print(f"[Runtime Menu] Added {len(children)} children to item {i}")
                else:
                    # Old format - plain string
                    item_text = str(item_data)
                    self.tree.insert('', 'end', text=f"{i+1}. {item_text}")
        except Exception as e:
            print(f"[Runtime Menu] ❌ Error building tree: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"[Runtime Menu] ➕ Added {len(items)} items to tree")
        
        # Select first item by default
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.focus(children[0])
            self.tree.see(children[0])  # Scroll to top
        
        # CRITICAL: Bring window to front and focus
        self.root.deiconify()  # Ensure not minimized
        self.root.lift()
        self.root.focus_force()
        self.tree.focus_set()
        
        print(f"[Runtime Menu] ✅ Display complete, window focused")
    
    def _quick_select(self, index):
        """Quick select via number key (disabled for tree view)."""
        # Disabled for tree view as navigation is different
        pass
    
    def _on_select(self):
        """Handle selection button/Enter - supports hierarchical selections."""
        print(f"[Runtime Menu] 📌 _on_select() called")
        selection = self.tree.selection()
        if not selection:
            print(f"[Runtime Menu] ⚠️  No selection found")
            return
        
        item_id = selection[0]
        item_text = self.tree.item(item_id, 'text')
        tags = self.tree.item(item_id, 'tags')
        
        print(f"[Runtime Menu] 📌 Selected item: '{item_text}', tags: {tags}")
        
        # Determine if this is a parent or child selection
        is_child = False
        parent_idx = None
        child_idx = None
        
        for tag in tags:
            if tag.startswith('parent_'):
                # Parent selection - extract index
                parent_idx = int(tag.split('_')[1])
                print(f"[Runtime Menu] 📌 Parent selection: index={parent_idx}")
                self.selected_index = parent_idx
                self.selected_child_index = None
                break
            elif tag.startswith('child_'):
                # Child selection - extract parent and child indices
                parts = tag.split('_')
                parent_idx = int(parts[1])
                child_idx = int(parts[2])
                is_child = True
                print(f"[Runtime Menu] 📌 Child selection: parent={parent_idx}, child={child_idx}")
                self.selected_index = parent_idx
                self.selected_child_index = child_idx
                break
        
        if parent_idx is None:
            # Fallback: Try to parse from text (old format)
            try:
                if ". " in item_text:
                    index_str = item_text.split(". ")[0]
                    self.selected_index = int(index_str) - 1
                    self.selected_child_index = None
                    print(f"[Runtime Menu] 📌 Parsed index from text: {self.selected_index}")
                else:
                    print(f"[Runtime Menu] ⚠️  Could not parse item")
                    return
            except (ValueError, IndexError) as e:
                print(f"[Runtime Menu] ❌ Error parsing selection: {e}")
                return
        
        # Confirm selection
        self.cancelled = False
        self.selection_ready.set()
        print(f"[Runtime Menu] ✅ Selection confirmed, event set")
        
        # If "Keep list open" is unchecked, clear the list after selection
        if not self.keep_list_open.get():
            self.root.after(100, self._clear_list)
    
    def _clear_list(self):
        """Clear the current list and return to waiting state."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.title_label.config(text=_("Waiting for selection..."))
        self.current_items = []
        self.current_title = ""
    
    def _on_cancel(self):
        """Handle cancel button/Escape."""
        self.selected_index = -1
        self.cancelled = True
        self.explicit_cancel = True  # Mark as explicit cancel (not timeout)
        self.selection_ready.set()
    
    def _on_exit(self):
        """Handle exit button - close the window entirely."""
        self.root.quit()
    
    def run(self):
        """Start the main loop."""
        try:
            self.root.mainloop()
        finally:
            self.ipc_server.stop()
            print("[Runtime Menu] Stopped")


def main():
    """Entry point for tuxtalks-menu."""
    menu = RuntimeMenu()
    menu.run()


if __name__ == "__main__":
    main()
