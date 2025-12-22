import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import dbus
import threading

import pathlib
import sqlite3
from config import PLAYER_SCHEMAS
from local_library import LocalLibrary
from i18n import _

class LauncherPlayerTab:
    def build_player_tab(self):
        """Builds the Player Selection and Configuration UI."""
        self.player_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.player_tab, text=_("Player"))
        
        # Player Selection
        player_sel_frame = ttk.Frame(self.player_tab)
        player_sel_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(player_sel_frame, text=_("Select Player:")).pack(side=tk.LEFT)
        
        # Get players from schema
        self.player_options = list(PLAYER_SCHEMAS.keys())
        current_player = self.config.get("PLAYER")
        if current_player not in self.player_options:
            current_player = self.player_options[0] if self.player_options else ""
            
        self.player_var = tk.StringVar(value=current_player)
        self.player_combo = ttk.Combobox(player_sel_frame, textvariable=self.player_var, values=self.player_options, state="readonly")
        self.player_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.player_combo.bind("<<ComboboxSelected>>", self.on_player_change)

        # Player Buttons (New Row)
        player_btn_frame = ttk.Frame(self.player_tab)
        player_btn_frame.pack(fill=tk.X, pady=2)
        ttk.Button(player_btn_frame, text=_("Scan"), command=self.scan_players).pack(side=tk.LEFT, padx=2)
        ttk.Button(player_btn_frame, text=_("Add Custom"), command=self.add_custom_player).pack(side=tk.LEFT, padx=2)
        
        # Connection Settings (Dynamic)
        self.conn_frame = ttk.LabelFrame(self.player_tab, text=_("Connection Settings"), padding="10")
        self.conn_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Test Connection Button (Moved to Player Tab)
        ttk.Button(self.player_tab, text=_("Test Connection"), command=self.test_connection).pack(fill=tk.X, pady=10)

        # Initialize fields
        self.update_dynamic_fields()

    def scan_players(self):
        found = []
        # Check for binaries
        if shutil.which("elisa"):
            found.append("elisa")
        if shutil.which("strawberry"):
            found.append("strawberry")
        if shutil.which("mediacenter28") or shutil.which("mediacenter29") or shutil.which("mediacenter30") or shutil.which("mediacenter31") or shutil.which("mediacenter32") or shutil.which("mediacenter33"):
             found.append("jriver")

        # Check for running MPRIS services
        try:
            bus = dbus.SessionBus()
            for service in bus.list_names():
                if service.startswith("org.mpris.MediaPlayer2."):
                    name = service.replace("org.mpris.MediaPlayer2.", "")
                    if name not in found and name not in ["elisa", "strawberry"]:
                        found.append("mpris")
        except Exception:
            pass

        if found:
            message = f"Found players: {', '.join(found)}\n\nSelect one to configure?"
            if messagebox.askyesno("Scan Complete", message):
                player = found[0]
                self.player_var.set(player)
                self.on_player_change(None)
                
                if player == "mpris":
                    try:
                        bus = dbus.SessionBus()
                        for service in bus.list_names():
                            if service.startswith("org.mpris.MediaPlayer2."):
                                name = service.replace("org.mpris.MediaPlayer2.", "")
                                if name not in ["elisa", "strawberry", "jriver"]:
                                    if "MPRIS_SERVICE" in self.dynamic_vars:
                                        self.dynamic_vars["MPRIS_SERVICE"].set(service)
                                    break
                    except:
                        pass
        else:
            messagebox.showinfo(_("Scan Complete"), _("No supported players found."))

    def add_custom_player(self):
        self.player_var.set("mpris")
        self.on_player_change(None)
        if "MPRIS_SERVICE" in self.dynamic_vars:
            self.dynamic_vars["MPRIS_SERVICE"].set("org.mpris.MediaPlayer2.PLAYER_NAME")
        messagebox.showinfo("Custom Player", "Selected 'Generic / Custom Player'.\n\nPlease enter the MPRIS service name of your player (e.g., org.mpris.MediaPlayer2.vlc).")

    def on_player_change(self, event):
        self.update_dynamic_fields()

    def update_dynamic_fields(self):
        # Clear existing widgets in conn_frame
        for widget in self.conn_frame.winfo_children():
            widget.destroy()
            
        self.dynamic_vars = {}
        player = self.player_var.get()
        schema = PLAYER_SCHEMAS.get(player, {})
        fields = schema.get("fields", {})
        
        if not fields:
            ttk.Label(self.conn_frame, text=_("No configuration needed for this player."), font=("Helvetica", 10, "italic")).pack(pady=10)
            return

        row = 0
        self.conn_frame.columnconfigure(1, weight=1)
        
        for key, field_info in fields.items():
            label_text = field_info.get("label", key)
            default_val = field_info.get("default", "")
            
            current_val = self.config.get(key)
            if current_val is None:
                current_val = default_val
                
            ttk.Label(self.conn_frame, text=f"{label_text}:").grid(row=row, column=0, sticky=tk.W, pady=5)
            
            var = tk.StringVar(value=str(current_val))
            self.dynamic_vars[key] = var
            
            # Mask sensitive fields
            show_char = "*" if "key" in key.lower() or "password" in key.lower() else None
            entry = ttk.Entry(self.conn_frame, textvariable=var, show=show_char)
            entry.grid(row=row, column=1, sticky=tk.EW, padx=5)
            
            if key == "LIBRARY_PATH":
                btn_frame = ttk.Frame(self.conn_frame)
                btn_frame.grid(row=row, column=2, padx=5)
                ttk.Button(btn_frame, text=_("Browse"), command=lambda v=var: self.browse_folder(v)).pack(side=tk.LEFT, padx=2)
                ttk.Button(btn_frame, text=_("Scan Now"), command=lambda v=var: self.scan_library(v.get())).pack(side=tk.LEFT, padx=2)
                
            row += 1

    def browse_folder(self, var):
        path = filedialog.askdirectory(initialdir=var.get())
        if path:
            var.set(path)

    def scan_library(self, path):
        if not path:
            messagebox.showerror(_("Error"), _("Please select a library path first."))
            return
            
        db_path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "library.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ask if we should clear existing library
        clear_db = True
        if db_path.exists():
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM tracks")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        # Simple dialog for brevity in mixin, but replicating full dialog logic is best
                        # Using simpler messagebox for now or keeping full logic?
                        # Let's use askyesnocancel: Yes=Replace, No=Update, Cancel=Abort
                        # But that's confusing.
                        # I'll replicate the custom dialog logic here to ensure UX consistency.
                        
                        dialog = tk.Toplevel(self.root)
                        dialog.title("Scan Options")
                        dialog.transient(self.root)
                        dialog.grab_set()
                        dialog.geometry("500x220")
                        
                        result = [None]
                        dialog.protocol("WM_DELETE_WINDOW", lambda: [result.__setitem__(0, None), dialog.destroy()])
                        
                        def on_replace(): result[0] = True; dialog.destroy()
                        def on_update(): result[0] = False; dialog.destroy()
                        def on_cancel(): result[0] = None; dialog.destroy()
                        
                        btn_container = ttk.Frame(dialog, padding="10")
                        btn_container.pack(side=tk.BOTTOM, fill=tk.X)
                        
                        row1 = ttk.Frame(btn_container); row1.pack(fill=tk.X, pady=2)
                        ttk.Button(row1, text=_("Replace"), command=on_replace, width=15).pack(side=tk.LEFT, padx=5)
                        ttk.Label(row1, text=_("Clear all and rescan")).pack(side=tk.LEFT)
                        
                        row2 = ttk.Frame(btn_container); row2.pack(fill=tk.X, pady=2)
                        ttk.Button(row2, text=_("Update"), command=on_update, width=15).pack(side=tk.LEFT, padx=5)
                        ttk.Label(row2, text=_("Keep existing, add new")).pack(side=tk.LEFT)
                        
                        row3 = ttk.Frame(btn_container); row3.pack(fill=tk.X, pady=2)
                        ttk.Button(row3, text=_("Cancel"), command=on_cancel, width=15).pack(side=tk.LEFT, padx=5)
                        
                        msg_frame = ttk.Frame(dialog, padding="20")
                        msg_frame.pack(fill=tk.BOTH, expand=True)
                        ttk.Label(msg_frame, text=f"Existing library has {count} tracks.", font=("", 10, "bold")).pack(pady=10)
                        
                        self.root.wait_window(dialog)
                        if result[0] is None: return
                        clear_db = result[0]
            except Exception as e:
                print(f"Error checking DB: {e}")
        
        def run_scan():
            try:
                lib = LocalLibrary(str(db_path))
                def progress(current, total): print(f"Scanning: {current}/{total}")
                lib.scan_directory(path, callback=progress, clear_db=clear_db)
                action = "replaced" if clear_db else "updated"
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Library {action}! Scan complete."))
            except Exception as e:
                err = str(e) # Capture safely
                self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {err}"))

        threading.Thread(target=run_scan, daemon=True).start()
        messagebox.showinfo(_("Scanning"), _("Scanning library in background..."))
