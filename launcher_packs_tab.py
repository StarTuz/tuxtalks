"""
Content Packs Tab for TuxTalks Launcher - LAL Framework GUI.

Provides graphical interface for browsing, installing, and managing
third-party content packs (audio assets and macros).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import zipfile
import tarfile
import shutil
import threading
from pathlib import Path
from i18n import _


class PacksTab:
    """Content Packs management tab for TuxTalks launcher."""
    
    def __init__(self, parent_notebook, lal_manager):
        """
        Initialize the Content Packs tab.
        
        Args:
            parent_notebook: ttk.Notebook to add this tab to
            lal_manager: LALManager instance for pack operations
        """
        self.lal_manager = lal_manager
        self.frame = ttk.Frame(parent_notebook)
        
        # Build UI
        self._build_ui()
        
        # Load initial pack list
        self.refresh_packs()
        
    def _build_ui(self):
        """Construct the UI components."""
        # Top section: Pack list
        list_frame = ttk.LabelFrame(self.frame, text=_("Installed Content Packs"), padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Treeview for pack list
        columns = ("name", "version", "author", "games", "status")
        self.pack_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.pack_tree.heading("name", text=_("Pack Name"))
        self.pack_tree.heading("version", text=_("Version"))
        self.pack_tree.heading("author", text=_("Author"))
        self.pack_tree.heading("games", text=_("Compatible Games"))
        self.pack_tree.heading("status", text=_("Status"))
        
        self.pack_tree.column("name", width=200)
        self.pack_tree.column("version", width=80)
        self.pack_tree.column("author", width=120)
        self.pack_tree.column("games", width=180)
        self.pack_tree.column("status", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.pack_tree.yview)
        self.pack_tree.configure(yscroll=scrollbar.set)
        self.pack_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.pack_tree.bind("<<TreeviewSelect>>", self.on_pack_select)
        
        # Middle section: Pack details
        details_frame = ttk.LabelFrame(self.frame, text=_("Pack Details"), padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Details text widget
        self.details_text = tk.Text(details_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom section: Action buttons
        button_frame = ttk.Frame(self.frame, padding="5")
        button_frame.pack(fill=tk.X)
        
        # Left-aligned buttons
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text=_("📦 Install Pack"), command=self.install_pack, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_buttons, text=_("🗑️  Remove Pack"), command=self.remove_pack, width=15).pack(side=tk.LEFT, padx=2)
        
        # Right-aligned buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text=_("📁 Open Packs Folder"), command=self.open_packs_folder, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(right_buttons, text=_("🔄 Refresh"), command=self.refresh_packs, width=10).pack(side=tk.LEFT, padx=2)
        
        # Help text at bottom
        help_frame = ttk.Frame(self.frame, padding="5")
        help_frame.pack(fill=tk.X)
        
        help_text = (
            "💡 Tip: Content packs provide custom audio responses and macros for games. "
            "Install via GUI, CLI (tuxtalks-install-pack ./pack.zip), or manually extract to packs folder.\n"
            "⚠️  You are responsible for ensuring pack licenses permit your use. TuxTalks does not verify third-party content."
        )
        ttk.Label(help_frame, text=help_text, wraplength=700, font=("Helvetica", 9), foreground="gray").pack()
        
    def refresh_packs(self):
        """Reload and display pack list."""
        # Clear existing items
        for item in self.pack_tree.get_children():
            self.pack_tree.delete(item)
        
        # Reload packs from disk
        self.lal_manager.packs = {}
        self.lal_manager.load_all_packs()
        
        # Populate tree
        pack_list = self.lal_manager.list_packs()
        
        if not pack_list:
            # Show placeholder message
            self.pack_tree.insert("", tk.END, values=("No packs installed", "", "", "", ""))
        else:
            for pack in pack_list:
                games_str = ", ".join(pack['games']) if pack['games'] else "All"
                status = "✅ Loaded" if pack['audio_count'] > 0 or pack['macro_count'] > 0 else "⚠️ Empty"
                
                self.pack_tree.insert("", tk.END, values=(
                    pack['name'],
                    pack['version'],
                    pack['author'],
                    games_str,
                    status
                ))
        
        # Clear details
        self._update_details("")
        
    def on_pack_select(self, event):
        """Handle pack selection - show details."""
        selection = self.pack_tree.selection()
        if not selection:
            self._update_details("")
            return
        
        item = self.pack_tree.item(selection[0])
        pack_name = item['values'][0]
        
        # Check if placeholder
        if pack_name == "No packs installed":
            self._update_details("")
            return
        
        # Find pack in LAL manager
        pack_info = None
        for pack in self.lal_manager.list_packs():
            if pack['name'] == pack_name:
                pack_info = pack
                break
        
        if not pack_info:
            self._update_details("Pack not found")
            return
        
        # Get full pack object
        pack_obj = self.lal_manager.packs.get(pack_name)
        if not pack_obj:
            self._update_details("Pack details unavailable")
            return
        
        # Format details
        metadata = pack_obj.metadata
        description = metadata.get('description', 'No description available')
        license_info = metadata.get('license', 'Not specified')
        
        details = f"""Name: {pack_info['name']}
Version: {pack_info['version']}
Author: {pack_info['author']}
License: {license_info}
Compatible Games: {', '.join(pack_info['games']) if pack_info['games'] else 'All'}

Description:
{description}

Content:
• Audio files: {pack_info['audio_count']}
• Macros: {pack_info['macro_count']}
"""
        
        self._update_details(details)
        
    def _update_details(self, text):
        """Update the details text widget."""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert("1.0", text)
        self.details_text.config(state=tk.DISABLED)
        
    def install_pack(self):
        """Install a pack from archive file."""
        # File browser for archive
        filetypes = [
            ("Archive files", "*.zip *.tar.gz *.tgz"),
            ("Zip files", "*.zip"),
            ("Tar files", "*.tar.gz *.tgz"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            parent=self.frame,
            title="Select Content Pack Archive",
            filetypes=filetypes
        )
        
        if not filepath:
            return
        
        # Validate file exists
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"File not found: {filepath}", parent=self.frame)
            return
        
        # Start installation in background thread
        self._install_pack_async(filepath)
        
    def _install_pack_async(self, filepath):
        """Install pack in background thread to avoid UI freeze."""
        # Disable buttons during installation
        self._set_buttons_state(tk.DISABLED)
        
        # Create progress indicator
        progress_window = tk.Toplevel(self.frame)
        progress_window.title("Installing Pack")
        progress_window.geometry("400x150")
        progress_window.transient(self.frame)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text=_("Installing content pack..."), font=("Helvetica", 10)).pack(pady=20)
        progress_label = ttk.Label(progress_window, text=_("Extracting archive..."), foreground="gray")
        progress_label.pack(pady=10)
        
        def install_worker():
            """Background worker for installation."""
            try:
                # Extract to temp directory
                temp_dir = os.path.join(self.lal_manager.PACKS_DIR, ".temp_extract")
                os.makedirs(temp_dir, exist_ok=True)
                
                progress_label.config(text=_("Extracting archive..."))
                
                # Extract archive
                if filepath.endswith('.zip'):
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                elif filepath.endswith(('.tar.gz', '.tgz')):
                    with tarfile.open(filepath, 'r:gz') as tar_ref:
                        tar_ref.extractall(temp_dir)
                else:
                    raise ValueError("Unsupported archive format")
                
                progress_label.config(text=_("Validating pack..."))
                
                # Find pack.json (might be in subdirectory)
                pack_json_path = None
                for root, dirs, files in os.walk(temp_dir):
                    if 'pack.json' in files:
                        pack_json_path = os.path.join(root, 'pack.json')
                        break
                
                if not pack_json_path:
                    raise ValueError(
                        "No pack.json found in archive.\n\n"
                        "This appears to be a VoiceAttack profile or other non-LAL pack.\n\n"
                        "To use VoiceAttack packs with TuxTalks:\n"
                        "1. Extract the archive manually\n"
                        "2. Create a pack.json file (see LAL_QUICKSTART.md)\n"
                        "3. Copy audio files to a TuxTalks-compatible structure\n\n"
                        "For help, see: docs/LAL_QUICKSTART.md"
                    )
                
                # Load and validate pack.json
                import json
                with open(pack_json_path, 'r') as f:
                    metadata = json.load(f)
                
                # Extract pack directory (parent of pack.json)
                pack_dir = os.path.dirname(pack_json_path)
                pack_name = metadata.get('name', 'Unknown Pack')
                
                # Validate required fields
                required_fields = ['name', 'version', 'author', 'compatibility']
                for field in required_fields:
                    if field not in metadata:
                        raise ValueError(f"Missing required field: {field}")
                
                progress_label.config(text=_("Installing pack..."))
                
                # Determine target directory name (sanitize pack name)
                target_name = pack_name.replace(' ', '_').replace('/', '_').lower()
                target_path = os.path.join(self.lal_manager.PACKS_DIR, target_name)
                
                # Check if pack already exists
                if os.path.exists(target_path):
                    # Ask for overwrite (from main thread)
                    def ask_overwrite():
                        return messagebox.askyesno(
                            "Pack Exists",
                            f"Pack '{pack_name}' is already installed.\n\nOverwrite?",
                            parent=self.frame
                        )
                    
                    self.frame.after(0, lambda: setattr(self, '_overwrite_result', ask_overwrite()))
                    while not hasattr(self, '_overwrite_result'):
                        import time
                        time.sleep(0.1)
                    
                    if not self._overwrite_result:
                        delattr(self, '_overwrite_result')
                        raise ValueError("Installation cancelled by user")
                    delattr(self, '_overwrite_result')
                    
                    # Remove existing pack
                    shutil.rmtree(target_path)
                
                # Copy pack to packs directory
                shutil.copytree(pack_dir, target_path)
                
                # Cleanup temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                # Success
                self.frame.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Content pack '{pack_name}' installed successfully!",
                    parent=self.frame
                ))
                
            except Exception as e:
                # Error
                self.frame.after(0, lambda: messagebox.showerror(
                    "Installation Failed",
                    f"Failed to install pack:\n\n{str(e)}",
                    parent=self.frame
                ))
                
            finally:
                # Close progress window
                progress_window.destroy()
                
                # Re-enable buttons
                self._set_buttons_state(tk.NORMAL)
                
                # Cleanup temp directory (always, even on error)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                
                # Refresh pack list
                self.refresh_packs()
        
        # Start worker thread
        thread = threading.Thread(target=install_worker, daemon=True)
        thread.start()
        
    def remove_pack(self):
        """Remove selected pack."""
        selection = self.pack_tree.selection()
        if not selection:
            messagebox.showwarning(_("No Selection"), _("Please select a pack to remove."), parent=self.frame)
            return
        
        item = self.pack_tree.item(selection[0])
        pack_name = item['values'][0]
        
        # Check if placeholder
        if pack_name == "No packs installed":
            return
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Removal",
            f"Remove content pack '{pack_name}'?\n\nThis will delete all pack files.",
            parent=self.frame
        ):
            return
        
        try:
            # Find pack directory
            pack_obj = self.lal_manager.packs.get(pack_name)
            if not pack_obj:
                messagebox.showerror("Error", f"Pack '{pack_name}' not found.", parent=self.frame)
                return
            
            pack_path = pack_obj.path
            
            # Delete pack directory
            if os.path.exists(pack_path):
                shutil.rmtree(pack_path)
            
            # Refresh
            self.refresh_packs()
            
            messagebox.showinfo("Success", f"Pack '{pack_name}' removed successfully.", parent=self.frame)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove pack:\n\n{str(e)}", parent=self.frame)
            
    def open_packs_folder(self):
        """Open packs directory in file manager."""
        packs_dir = self.lal_manager.PACKS_DIR
        
        # Ensure directory exists
        os.makedirs(packs_dir, exist_ok=True)
        
        # Open in file manager (Linux)
        try:
            import subprocess
            subprocess.Popen(['xdg-open', packs_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n\n{str(e)}", parent=self.frame)
            
    def _set_buttons_state(self, state):
        """Enable/disable all buttons (for progress indication)."""
        for child in self.frame.winfo_children():
            if isinstance(child, ttk.Frame):
                for button in child.winfo_children():
                    if isinstance(button, ttk.Button):
                        button.config(state=state)
