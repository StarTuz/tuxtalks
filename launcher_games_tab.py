import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import datetime
import threading

import psutil
from game_manager import GameManager, X4Profile, EliteDangerousProfile, GenericGameProfile
from input_controller import InputController
from i18n import _

class KeyBindDialog(tk.Toplevel):
    def __init__(self, parent, title, initial_value=""):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.geometry("400x250")
        
        # Center
        self.transient(parent)
        self.grab_set()
        
        # UI
        main = ttk.Frame(self, padding=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main, text=_("Press the key combination on your keyboard:"), font=("Helvetica", 10)).pack(pady=(0, 10))
        
        self.display_var = tk.StringVar(value=initial_value if initial_value and initial_value != "NOT BOUND" else "Press keys...")
        self.entry = ttk.Entry(main, textvariable=self.display_var, font=("Helvetica", 12, "bold"), justify="center", state="readonly")
        self.entry.pack(fill=tk.X, pady=10)
        
        ttk.Label(main, text=_("(Example: Ctrl + Alt + H)"), font=("Helvetica", 9, "italic")).pack(pady=5)
        
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=20)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text=_("Cancel"), command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text=_("Clear"), command=self.on_clear).pack(side=tk.LEFT, padx=5)
        
        # Key Binding Logic
        self.current_keys = set() # What is shown/saved
        self.held_keys = set()    # What is physically held
        self.bind("<KeyPress>", self.on_key_press)
        self.bind("<KeyRelease>", self.on_key_release)
        
        # Focus
        self.focus_set()
        self.entry.focus_set()
        
    def on_key_press(self, event):
        k = event.keysym
        
        # TK Mappings to readable
        if "Control_L" in k: k = "LeftControl"
        elif "Control_R" in k: k = "RightControl"
        elif "Shift_L" in k: k = "LeftShift"
        elif "Shift_R" in k: k = "RightShift"
        elif "Alt_L" in k: k = "LeftAlt"
        elif "Alt_R" in k: k = "RightAlt"
        elif "Return" == k: k = "Enter"
        
        # If this is the start of a new sequence (no keys currently held)
        if not self.held_keys:
             self.current_keys.clear()
             
        self.held_keys.add(k)
        self.current_keys.add(k)
        self.update_display()
        
    def on_key_release(self, event):
        k = event.keysym
        if "Control_L" in k: k = "LeftControl"
        elif "Control_R" in k: k = "RightControl"
        elif "Shift_L" in k: k = "LeftShift"
        elif "Shift_R" in k: k = "RightShift"
        elif "Alt_L" in k: k = "LeftAlt"
        elif "Alt_R" in k: k = "RightAlt"
        elif "Return" == k: k = "Enter"

        if k in self.held_keys:
            self.held_keys.remove(k)
            
        # Do NOT remove from current_keys or update display
        # This creates the "Latch" effect where the full combo stays visible
        # until the user presses a new key sequence.

    def update_display(self):
        # Sort: Mods first, then keys
        mods = []
        keys = []
        
        ordered_mods = ["LeftControl", "RightControl", "LeftShift", "RightShift", "LeftAlt", "RightAlt"]
        
        for k in self.current_keys:
            if k in ordered_mods:
                mods.append(k)
            else:
                keys.append(k)
                
        # Sort Mods
        mods.sort(key=lambda x: ordered_mods.index(x) if x in ordered_mods else 99)
        keys.sort()
        
        combo = mods + keys
        display = " + ".join(combo)
        self.display_var.set(display)

    def on_clear(self):
        self.current_keys.clear()
        self.display_var.set("")
        
    def on_ok(self):
        # Return the string in the entry
        self.result = self.display_var.get()
        self.destroy()

class AddGameDialog(tk.Toplevel):
    def __init__(self, parent, game_manager, callback, existing_profile=None):
        super().__init__(parent)
        self.title("Add Game Wizard 🪄" if not existing_profile else f"Edit Game: {existing_profile.name}")
        self.geometry("700x850")
        self.game_manager = game_manager
        self.callback = callback
        self.existing_profile = existing_profile
        
        # UI Layout
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Step 1: Scan
        step1_frame = ttk.LabelFrame(main_frame, text=_("Step 1: Select Running Game Process"), padding="5")
        step1_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Process Tree
        columns = ("pid", "name", "cmdline")
        self.proc_tree = ttk.Treeview(step1_frame, columns=columns, show="headings", height=8)
        self.proc_tree.heading("pid", text=_("PID"))
        self.proc_tree.heading("name", text=_("Process Name"))
        self.proc_tree.heading("cmdline", text=_("Command Line / Path"))
        self.proc_tree.column("pid", width=60)
        self.proc_tree.column("name", width=150)
        self.proc_tree.column("cmdline", width=300)

        # Sorting Bindings
        for col in columns:
            self.proc_tree.heading(col, text=self.proc_tree.heading(col, "text"), 
                                 command=lambda c=col: self._sort_tree(c, False))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(step1_frame, orient=tk.VERTICAL, command=self.proc_tree.yview)
        self.proc_tree.configure(yscroll=scrollbar.set)
        self.proc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.proc_tree.bind("<<TreeviewSelect>>", self.on_process_select)
        
        # Scan Button
        ttk.Button(step1_frame, text=_("🔄 Scan Processes"), command=self.scan_processes).pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Step 2: Configure
        step2_frame = ttk.LabelFrame(main_frame, text=_("Step 2: Configuration"), padding="5")
        step2_frame.pack(fill=tk.X, pady=5)
        
        # Grid
        step2_frame.columnconfigure(1, weight=1)
        
        # Game Type
        ttk.Label(step2_frame, text=_("Game Type:")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(step2_frame, textvariable=self.type_var, values=["X4 Foundations (Steam Proton)", "X4 Foundations (Steam Native)", "X4 Foundations (GOG)", "Elite Dangerous (Steam)", "Generic / Other"], state="readonly")
        self.type_combo.grid(row=0, column=1, sticky=tk.EW, pady=2)
        self.type_combo.current(0)
        
        # Game Group (Renamed for parity)
        # Game Name (Group)
        ttk.Label(step2_frame, text=_("Game Name:")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.group_var = tk.StringVar()
        ttk.Entry(step2_frame, textvariable=self.group_var).grid(row=1, column=1, sticky=tk.EW, pady=2)

        # Process Name (Auto-filled)
        ttk.Label(step2_frame, text=_("Process Name:")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.proc_name_var = tk.StringVar()
        ttk.Entry(step2_frame, textvariable=self.proc_name_var).grid(row=2, column=1, sticky=tk.EW, pady=2)
        
        # Display Name (Profile Variant)
        ttk.Label(step2_frame, text=_("Binding Profile Name:")).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.disp_name_var = tk.StringVar()
        ttk.Entry(step2_frame, textvariable=self.disp_name_var).grid(row=3, column=1, sticky=tk.EW, pady=2)
        ttk.Label(step2_frame, text="(defaults to binding file name, e.g. 'inputmap.xml')", font=("Helvetica", 8, "italic")).grid(row=4, column=1, sticky=tk.W)
        
        # Runtime Environment (New Phase 16 Fix)
        ttk.Label(step2_frame, text=_("Runtime Environment:")).grid(row=5, column=0, sticky=tk.W, pady=2)
        self.wizard_runtime_var = tk.StringVar(value="Native Linux")
        self.wizard_runtime_combo = ttk.Combobox(step2_frame, textvariable=self.wizard_runtime_var, values=["Native Linux", "Proton/Wine"], state="readonly")
        self.wizard_runtime_combo.grid(row=5, column=1, sticky=tk.EW, pady=2)
        
        # Process Path Filter (Hidden/Internal)
        self.disc_var = tk.StringVar() 
        
        # Bindings Path
        ttk.Label(step2_frame, text=_("Bindings Path:")).grid(row=6, column=0, sticky=tk.W, pady=2)
        self.bind_path_var = tk.StringVar()
        ttk.Entry(step2_frame, textvariable=self.bind_path_var).grid(row=6, column=1, sticky=tk.EW, pady=2)
        
        # Buttons Frame
        btn_frame = ttk.Frame(step2_frame)
        btn_frame.grid(row=6, column=2, padx=2)
        ttk.Button(btn_frame, text=_("Browse"), command=self.browse_path).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text=_("🔍 Scan"), command=self.scan_bindings).pack(side=tk.LEFT, padx=1)
        
        # Bind Type Change
        self.type_combo.bind("<<ComboboxSelected>>", self.on_type_change)
        
        # Save
        btn_text = _("💾 Add Game Profile") if not getattr(self, 'existing_profile', None) else "💾 Update Game Profile"
        self.save_btn = ttk.Button(main_frame, text=btn_text, command=self.save_game)
        self.save_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Validation Triggers
        self.type_var.trace_add("write", lambda *args: self.validate_form())
        self.proc_name_var.trace_add("write", lambda *args: self.validate_form())
        self.bind_path_var.trace_add("write", lambda *args: self.validate_form())
        
        # Run initial scan
        self.scan_processes()
        
        # Pre-fill if editing
        if self.existing_profile:
            p = self.existing_profile
            # Process Name
            if isinstance(p.process_name, list):
                self.proc_name_var.set(p.process_name[0] if p.process_name else "")
            else:
                self.proc_name_var.set(p.process_name)
            
            # Group
            self.group_var.set(p.group)
            
            # Profile Name (Variant)
            # Try to extract variant from "Group (Variant)" format
            if "(" in p.name and p.name.endswith(")"):
                variant = p.name.split("(", 1)[1].rsplit(")", 1)[0]
                self.disp_name_var.set(variant)
            elif p.name == p.group:
                self.disp_name_var.set("Default")
            else:
                self.disp_name_var.set(p.name) # Fallback
                
            # Discriminator
            self.disc_var.set(p.path_discriminator if p.path_discriminator else "")
            
            # Binding Path
            if hasattr(p, 'custom_bindings_path') and p.custom_bindings_path:
                 self.bind_path_var.set(p.custom_bindings_path)
            elif hasattr(p, 'reference_path') and p.reference_path:
                 self.bind_path_var.set(p.reference_path)
                 
            # Game Type
            if isinstance(p, X4Profile):
                self.type_combo.current(0)
            elif isinstance(p, EliteDangerousProfile):
                self.type_combo.current(1)
            else:
                self.type_combo.current(2)
        
        # Initial Validation
        self.validate_form()
        
    def scan_bindings(self, silent=False):
        """Intelligently looks for binding files based on selected Game Type."""
        g_type = self.type_var.get()
        path_found = None
        
        if "X4" in g_type:
            # Import logic from X4Profile? Or reuse?
            dummy = X4Profile()
            if "Proton" in g_type:
                path_found = dummy._detect_x4_folder() # Internal proton path
                if path_found:
                     path_found = os.path.join(path_found, "inputmap.xml")
            else:
                 # Native check: ~/.config/Egosoft/X4 or EgosSoft
                 home = os.path.expanduser("~")
                 
                 # Check 'EgoSoft' (Case sensitive check)
                 bases = [f"{home}/.config/Egosoft/X4", f"{home}/.config/EgoSoft/X4"]
                 
                 for base in bases:
                     if os.path.exists(base):
                         # Logic split based on specific detected Game Type
                         if "Steam Native" in g_type:
                             # STEAM NATIVE: Expect User ID folder
                             subdirs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and d.isdigit()]
                             if subdirs:
                                 subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(base, x)), reverse=True)
                                 latest = subdirs[0]
                                 candidate = os.path.join(base, latest, "inputmap.xml") 
                                 if os.path.exists(candidate):
                                     path_found = candidate
                                     break
                         
                         # GOG (or fallback): Check root inputmap.xml
                         # GOG typically uses the root. checking this ONLY if Steam Native check didn't return (or if it's GOG)
                         if not path_found:
                             root_map = os.path.join(base, "inputmap.xml")
                             if os.path.exists(root_map):
                                 path_found = root_map
                                 break
        
        elif "Elite" in g_type:
             dummy = EliteDangerousProfile()
             dummy._resolve_active_binds_path()
             path_found = dummy.active_binds_path
             
        if path_found and os.path.exists(path_found):
            self.bind_path_var.set(path_found)
            if not silent:
                 messagebox.showinfo("Scan Results", f"Found bindings:\n{path_found}", parent=self)
            return path_found
        else:
            if not silent:
                 messagebox.showinfo(_("Scan Results"), _("No standard binding files found for this game type."), parent=self)
            return None

    def on_type_change(self, event=None):
        val = self.type_var.get()
        
        # Reset Disc
        self.disc_var.set("")
        
        if "X4 Foundations" in val:
            self.group_var.set(val) # Default to exact Game Type string as requested
            
            if "Steam Proton" in val:
                self.disp_name_var.set("Steam Proton")
                self.proc_name_var.set("Main()") # User confirmed for Proton/Steam
                self.wizard_runtime_var.set("Proton/Wine")
            elif "Steam Native" in val:
                self.disp_name_var.set("Steam Native")
                self.proc_name_var.set("Main()") # Confirmed for Native too
                self.wizard_runtime_var.set("Native Linux")
            elif "GOG" in val:
                self.disp_name_var.set("GOG")
                self.proc_name_var.set("Main()") # Suspected for GOG too
                self.wizard_runtime_var.set("Native Linux")
                
        elif "Elite Dangerous" in val:
            # Set Group to match Type name (e.g. Elite Dangerous (Steam))
            self.group_var.set(val) 
            self.proc_name_var.set("EliteDangerous64.exe")
            # Default Profile Name?
            self.disp_name_var.set("Custom") # Or "Default" or "Steam"
            self.wizard_runtime_var.set("Proton/Wine")
            
        elif "Generic" in val:
             self.group_var.set("")
             self.proc_name_var.set("")
             self.disp_name_var.set("")
             self.bind_path_var.set("")
             self.wizard_runtime_var.set("Native Linux")
        
        # Auto-Scan bindings & Update Variant Name
        if val and "Generic" not in val:
             found = self.scan_bindings(silent=True)
             if found:
                  # Strict Binding Naming: Use exact filename
                  # e.g. "inputmap.xml"
                  basename = os.path.basename(found)
                  self.disp_name_var.set(basename)
                  
        self.validate_form()

    def validate_form(self):
        """Enable/Disable Save button based on Game Type rules."""
        g_type = self.type_var.get()
        p_name = self.proc_name_var.get().strip()
        bind_path = self.bind_path_var.get().strip()
        
        valid = True
        
        if "Generic" in g_type:
             # Strict Rules for Generic
             if not p_name or not bind_path:
                  valid = False
        else:
             # Care Packages (Elite/X4)
             # We trust the defaults or user override, as long as it's not totally empty?
             # Actually, even for X4, we should probably require a Process Name (which is auto-filled)
             if not p_name:
                  valid = False
                  
        if valid:
             self.save_btn.config(state="normal")
        else:
             self.save_btn.config(state="disabled")
             
    def scan_processes(self):
        # Clear
        for item in self.proc_tree.get_children():
            self.proc_tree.delete(item)
            
        # Scan
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
            try:
                name = proc.info['name']
                cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else str(proc.info.get('exe') or "")
                
                # Filter noise
                # Blocklist of system/kernel processes requiring filtering
                blocklist_prefixes = (
                    "kworker", "systemd", "rcu_", "migration", "idle", "ksoftirqd", 
                    "jbd2", "loop", "cpuhp", "khugepaged", "kcompactd", "kthread",
                    "kdevtmpfs", "kauditd", "dbus-", "rtkit-", "polkit", "pipewire",
                    "wireplumber", "gnome-", "xfce", "kde", "swapper", "init", "zsh", "bash"
                )
                
                if not name or name.startswith(blocklist_prefixes) or name.startswith("["):
                    continue
                    
                # Highlight X4/Elite
                if "x4" in name.lower() or "elite" in name.lower() or "proton" in name.lower():
                     self.proc_tree.insert("", 0, values=(proc.info['pid'], name, cmdline)) # Insert at top
                else:
                     self.proc_tree.insert("", tk.END, values=(proc.info['pid'], name, cmdline))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
    def on_process_select(self, event):
        selected = self.proc_tree.selection()
        if not selected: return
        item = self.proc_tree.item(selected[0])
        pid, name, cmdline = item['values']
        
        self.proc_name_var.set(name)
        self.proc_name_var.set(name)
        # Do NOT overwrite Game Name or Variant - user set those via Dropdown
        # if not self.existing_profile:
        #      self.group_var.set(name) # Default Group = Process Name
        #      self.disp_name_var.set("Default") # Default Profile = Default
        
        # intelligent guess discriminator
        # e.g. /games2/X4/X4 -> games2
        if "/games/" in str(cmdline):
             self.disc_var.set("games")
        elif "steamapps" in str(cmdline):
             self.disc_var.set("steamapps")
        elif "gog" in str(cmdline).lower():
             self.disc_var.set("gog")
        else:
             # Just guess common folder
             self.disc_var.set("")
             
    def browse_path(self):
        current_path = self.bind_path_var.get().strip()
        initial_dir = "/"
        if current_path:
            # If it's a file, get dirname. If dir, use it.
            if os.path.isfile(current_path):
                 initial_dir = os.path.dirname(current_path)
            elif os.path.isdir(current_path):
                 initial_dir = current_path
            elif os.path.exists(os.path.dirname(current_path)):
                 initial_dir = os.path.dirname(current_path)
                 
        f = filedialog.askopenfilename(parent=self, initialdir=initial_dir, title="Select Bindings File (XML/Binds)", filetypes=[("XML files", "*.xml"), ("Binds files", "*.binds"), ("All files", "*.*")])
        if f:
             self.bind_path_var.set(f)
             # Auto-populate Binding Profile Name with filename
             if not self.disp_name_var.get().strip():
                 filename = os.path.basename(f)
                 self.disp_name_var.set(filename)
             
    def _sort_tree(self, col, reverse):
        """Sorts the process list by column."""
        l = [(self.proc_tree.set(k, col), k) for k in self.proc_tree.get_children('')]
        
        # Sort logic
        try:
            # Try numeric sort for PID
            l.sort(key=lambda t: int(t[0]) if t[0].isdigit() else t[0].lower(), reverse=reverse)
        except ValueError:
            l.sort(key=lambda t: t[0].lower(), reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.proc_tree.move(k, '', index)
        self.proc_tree.heading(col, command=lambda: self._sort_tree(col, not reverse))

    def save_game(self):
        print("DEBUG: save_game() called")
        p_name = self.proc_name_var.get()
        d_name = self.disp_name_var.get()
        group = self.group_var.get()
        g_type = self.type_var.get()
        disc = self.disc_var.get()
        binds = self.bind_path_var.get()
        
        print(f"DEBUG: save_game values - p_name='{p_name}', d_name='{d_name}', group='{group}', g_type='{g_type}'")
        
        if not p_name:
            messagebox.showerror(_("Error"), _("Process Name required."), parent=self)
            return
            
        if not d_name: d_name = "Default"
        if not group: group = p_name
        
        # Determine Runtime Environment from Wizard Selection
        runtime_env = self.wizard_runtime_var.get()
        if not runtime_env: runtime_env = "Native Linux"
             
        # Construct Unique Name
        if "X4" in g_type:
             # Name: "X4 Foundations (Steam Proton)"
             # User wants "X4 Foundations (Steam Proton)"
             # If d_name is just "Steam Proton", we want "X4... (Steam Proton)"
             # If d_name is "X4 Foundations (Steam Proton)", we want that.
             if d_name.startswith(group):
                  final_name = d_name
             elif d_name == "Default":
                  final_name = group
             else:
                  final_name = f"{group} ({d_name})"
        elif "Elite" in g_type:
             final_name = f"Elite Dangerous ({d_name})"
             if d_name == "Default" or d_name == "Live": final_name = "Elite Dangerous"
        else:
             final_name = f"{group} ({d_name})"
             if d_name == "Default": final_name = group

        # Conflict Check
        existing_names = {p.name: p for p in self.game_manager.profiles}
        target_profile = None
        
        if final_name in existing_names:
            # Conflict detected
            conflict = existing_names[final_name]
            
            # If we are editing, and the name matches our own profile, it's fine.
            if self.existing_profile and self.existing_profile == conflict:
                target_profile = self.existing_profile # Update self
            else:
                # Genuine conflict
                if not messagebox.askyesno("Profile Exists", f"Profile '{final_name}' already exists.\nOverwrite?", parent=self):
                    return
                target_profile = conflict # Overwrite target
        else:
            # New Name
            if self.existing_profile:
                # Rename case
                target_profile = self.existing_profile
                target_profile.name = final_name
            else:
                target_profile = None # Will create new
            
        # Create or Update Logic
        try:
            if target_profile:
                # Update existing
                target_profile.group = group
                target_profile.process_name = [p_name] if "X4" in g_type else p_name # X4 uses list?
                if "X4" in g_type and not isinstance(target_profile.process_name, list): target_profile.process_name = [p_name]

                target_profile.path_discriminator = disc if disc else None
                target_profile.runtime_env = runtime_env
                
                if isinstance(target_profile, GenericGameProfile):
                     target_profile.reference_path = binds if binds else None
                elif hasattr(target_profile, 'custom_bindings_path'):
                     target_profile.custom_bindings_path = binds if binds else None
                
                # Check for class change? (e.g. Generic -> X4)
                # Not supporting dynamic class casting easily. 
                # If they changed type significantly, might be safer to remove and add?
                # But ID persistence isn't an issue.
                
                self.game_manager.save_profiles()
                messagebox.showinfo("Success", f"Updated profile '{target_profile.name}'!", parent=self)
                self.callback(target_profile.name)
            else:
                # Create New
                print(f"DEBUG: Creating new profile - final_name='{final_name}', group='{group}'")
                if "X4" in g_type:
                    p = X4Profile(name=final_name, discriminator=disc if disc else None, default_path_override=binds if binds else None, group=group)
                    p.process_name = [p_name]
                elif "Elite" in g_type:
                    p = EliteDangerousProfile(name=final_name, discriminator=disc if disc else None, default_path_override=binds if binds else None, group=group)
                else:
                    p = GenericGameProfile(name=final_name, process_name=[p_name], discriminator=disc if disc else None, reference_path=binds if binds else None, group=group)
                
                p.runtime_env = runtime_env
                print(f"DEBUG: About to call add_profile for '{p.name}'")
                self.game_manager.add_profile(p)
                print(f"DEBUG: add_profile returned successfully")
                messagebox.showinfo("Success", f"Added profile '{p.name}'!", parent=self)
                print(f"DEBUG: About to call callback with name='{p.name}'")
                self.callback(p.name)
                print(f"DEBUG: callback returned")

            self.destroy()
            
        except Exception as e:
             messagebox.showerror("Save Error", f"Failed to save profile:\n{e}", parent=self)
             import traceback
             traceback.print_exc()


class CaptureKeyDialog(tk.Toplevel):
    """Simple dialog to capture a key press"""
    
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        
        self.title("Capture Key")
        self.geometry("300x150")
        self.transient(parent)
        self.grab_set()
        
        ttk.Label(
            self,
            text="Press any key...",
            font=("Helvetica", 14, "bold")
        ).pack(pady=40)
        
        ttk.Button(self, text="Cancel", command=self.destroy).pack()
        
        # Bind key capture
        self.bind("<KeyPress>", self.on_key_press)
        self.focus_set()
        
        # Bring to front
        self.lift()
    
    def on_key_press(self, event):
        """Captures the key"""
        key = event.keysym
        
        # Ignore modifiers alone
        if key in ['Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R']:
            return
        
        # Return key
        self.callback(key)
        self.destroy()

class AddCustomCommandDialog(tk.Toplevel):
    """Dialog for adding/editing custom commands"""
    
    def __init__(self, parent, profile, callback, existing_cmd=None):
        super().__init__(parent)
        
        self.profile = profile
        self.callback = callback
        self.existing_cmd = existing_cmd
        
        self.title("➕ Add Custom Command" if not existing_cmd 
                   else f"✏ Edit {existing_cmd['name']}")
        self.geometry("500x550")
        self.transient(parent)
        self.grab_set()
        
        self.build_ui()
        
        # Pre-fill if editing
        if existing_cmd:
            self.load_existing_data()
            
    def build_ui(self):
        """Builds dialog UI"""
        main = ttk.Frame(self, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(main, text="Name:").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.name_var).pack(fill=tk.X, pady=(0,10))
        
        # Description
        ttk.Label(main, text="Description (optional):").pack(anchor=tk.W)
        self.desc_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.desc_var).pack(fill=tk.X, pady=(0,10))
        
        # Voice Triggers
        ttk.Label(main, text="Voice Triggers (comma separated):").pack(anchor=tk.W)
        self.triggers_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.triggers_var).pack(fill=tk.X, pady=(0,5))
        ttk.Label(main, text="💡 Say any of these phrases to trigger", font=("Helvetica", 9), foreground="gray").pack(anchor=tk.W, pady=(0,10))
        
        # Key Capture
        ttk.Label(main, text="Key to Press:").pack(anchor=tk.W)
        key_frame = ttk.Frame(main)
        key_frame.pack(fill=tk.X, pady=(0,5))
        
        self.key_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.key_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(key_frame, text="Capture", command=self.capture_key).pack(side=tk.LEFT, padx=(5,0))
        
        ttk.Label(main, text="Press [Capture] then press the key you want", font=("Helvetica", 9), foreground="gray").pack(anchor=tk.W, pady=(0,10))
        
        # Modifiers
        ttk.Label(main, text="Modifiers:").pack(anchor=tk.W)
        mod_frame = ttk.Frame(main)
        mod_frame.pack(fill=tk.X, pady=(0,10))
        
        self.ctrl_var = tk.BooleanVar()
        self.shift_var = tk.BooleanVar()
        self.alt_var = tk.BooleanVar()
        
        ttk.Checkbutton(mod_frame, text="Ctrl", variable=self.ctrl_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(mod_frame, text="Shift", variable=self.shift_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(mod_frame, text="Alt", variable=self.alt_var).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(side=tk.BOTTOM, pady=20)
        
        ttk.Button(btn_frame, text="Add Command" if not self.existing_cmd else "Save Changes", command=self.save_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
    def capture_key(self):
        CaptureKeyDialog(self, callback=self.on_key_captured)
    
    def on_key_captured(self, key):
        self.key_var.set(key)
        
    def load_existing_data(self):
        cmd = self.existing_cmd
        self.name_var.set(cmd.get('name', ''))
        self.desc_var.set(cmd.get('description', ''))
        self.triggers_var.set(", ".join(cmd.get('triggers', [])))
        self.key_var.set(cmd.get('key', ''))
        
        mods = cmd.get('modifiers', [])
        self.ctrl_var.set('ctrl' in mods)
        self.shift_var.set('shift' in mods)
        self.alt_var.set('alt' in mods)
        
    def save_command(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
            
        triggers_str = self.triggers_var.get().strip()
        if not triggers_str:
            messagebox.showerror("Error", "At least one voice trigger is required")
            return
            
        key = self.key_var.get()
        if not key:
            messagebox.showerror("Error", "Key is required.")
            return
            
        triggers = [t.strip().lower() for t in triggers_str.split(',') if t.strip()]
        
        modifiers = []
        if self.ctrl_var.get(): modifiers.append('ctrl')
        if self.shift_var.get(): modifiers.append('shift')
        if self.alt_var.get(): modifiers.append('alt')
        
        cmd_id = name.lower().replace(' ', '_')
        if self.existing_cmd:
            cmd_id = self.existing_cmd['id']
            
        cmd_data = {
            'id': cmd_id,
            'name': name,
            'description': self.desc_var.get().strip(),
            'triggers': triggers,
            'key': key,
            'modifiers': modifiers,
            'created': self.existing_cmd['created'] if self.existing_cmd else datetime.datetime.now().isoformat(),
            'enabled': True
        }
        
        self.callback(cmd_data)
        self.destroy()

class LauncherGamesTab:
    def build_games_tab(self):
        """Builds the Game Integration UI (Bindings & Macros)."""
        # Game Status Frame
        game_status_frame = ttk.LabelFrame(self.games_tab, text=_("Game Integration Status"), padding="10")
        game_status_frame.pack(fill=tk.X, pady=5)
        
        # Row 0: Target Profile Selector (Two Tier)
        profile_row = ttk.Frame(game_status_frame)
        profile_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(profile_row, text=_("Game:")).pack(side=tk.LEFT)
        self.game_var = tk.StringVar()
        self.game_combo = ttk.Combobox(profile_row, textvariable=self.game_var, state="readonly", width=25)
        self.game_combo.pack(side=tk.LEFT, padx=5)
        self.game_combo.bind("<<ComboboxSelected>>", self.on_game_select)

        ttk.Label(profile_row, text=_("Game Bindings:")).pack(side=tk.LEFT, padx=(10, 0))
        # Phase 17: Restore last selected profile
        # Legacy config retrieval removed - trusting GameManager active_profile logic
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profile_row, textvariable=self.profile_var, state="readonly", width=30)
        self.profile_combo.pack(side=tk.LEFT, padx=5)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_select)
        
        # Phase 1c: Macro Profile - separate row
        macro_profile_row = ttk.Frame(game_status_frame)
        macro_profile_row.pack(fill=tk.X, pady=(5, 2))
        ttk.Label(macro_profile_row, text=_("Macro Profile:")).pack(side=tk.LEFT)
        self.macro_profile_var = tk.StringVar(value="Built-in")
        self.macro_profile_combo = ttk.Combobox(macro_profile_row, textvariable=self.macro_profile_var, state="readonly", width=30)
        self.macro_profile_combo.pack(side=tk.LEFT, padx=5)
        self.macro_profile_combo.bind("<<ComboboxSelected>>", self.on_macro_profile_select)
        
        # Explanatory text for Macro Profile
        ttk.Label(macro_profile_row, text="→ Custom voice macros (separate from Game Bindings)", 
                  font=("Helvetica", 9), foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons row - BELOW Macro Profile
        macro_buttons_row = ttk.Frame(game_status_frame)
        macro_buttons_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(macro_buttons_row, text="", width=14).pack(side=tk.LEFT)  # Indent
        
        # Use tk.Button for color support
        new_btn = tk.Button(macro_buttons_row, text=_("➕"), width=2, fg="#00ff00", bg="#2d2d2d", 
                            activebackground="#3d3d3d", relief="raised", bd=1,
                            command=self.new_macro_profile, cursor="hand2")
        new_btn.pack(side=tk.LEFT, padx=2)
        new_btn.bind("<Enter>", lambda e: self.show_tooltip(e, "New macro profile"))
        new_btn.bind("<Leave>", self.hide_tooltip)
        
        rename_btn = tk.Button(macro_buttons_row, text=_("✏"), width=2, fg="white", bg="#2d2d2d",
                               activebackground="#3d3d3d", relief="raised", bd=1,
                               command=self.rename_macro_profile, cursor="hand2")
        rename_btn.pack(side=tk.LEFT, padx=2)
        rename_btn.bind("<Enter>", lambda e: self.show_tooltip(e, "Rename selected profile"))
        rename_btn.bind("<Leave>", self.hide_tooltip)
        
        delete_btn = tk.Button(macro_buttons_row, text=_("🗑"), width=2, fg="red", bg="#2d2d2d",
                               activebackground="#3d3d3d", relief="raised", bd=1,
                               command=self.delete_macro_profile, cursor="hand2")
        delete_btn.pack(side=tk.LEFT, padx=2)
        delete_btn.bind("<Enter>", lambda e: self.show_tooltip(e, "Delete selected profile"))
        delete_btn.bind("<Leave>", self.hide_tooltip)
        
        ttk.Label(macro_buttons_row, text="→ Create/edit macros in 'Macros (Beta)' tab", 
                  font=("Helvetica", 9), foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        
        # Row 1: Status Text
        status_row = ttk.Frame(game_status_frame)
        status_row.pack(fill=tk.X, pady=5)
        ttk.Label(status_row, text=_("Runtime Status:")).pack(side=tk.LEFT)
        self.game_mode_status = tk.StringVar(value="Inactive (Say 'Enable Game Mode')")
        ttk.Label(status_row, textvariable=self.game_mode_status, font=("Helvetica", 10, "bold"), foreground="gray").pack(side=tk.LEFT, padx=5)

        # Toggle Switch
        self.game_mode_enabled_var = tk.BooleanVar(value=self.config.get("GAME_MODE_ENABLED"))
        ttk.Checkbutton(status_row, text=_("Enable Game Integration"), variable=self.game_mode_enabled_var, command=self.save_game_mode_toggle).pack(side=tk.RIGHT, padx=5)
        
        # Row 2: Buttons + Filter
        # Control Rows
        # Row 1: Filter (Left) | Data/Refresh (Right)
        row1 = ttk.Frame(self.games_tab)
        row1.pack(fill=tk.X, pady=(5, 2))
        
        ttk.Label(row1, text=_("Filter:")).pack(side=tk.LEFT, padx=(5,2))
        self.cat_var = tk.StringVar(value="All")
        self.cat_combo = ttk.Combobox(row1, textvariable=self.cat_var, values=["All", "General", "Ship", "SRV", "On Foot"], state="readonly", width=12)
        self.cat_combo.pack(side=tk.LEFT, padx=2)
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_game_bindings())
        
        ttk.Button(row1, text=_("Refresh"), width=8, command=self.full_refresh_command).pack(side=tk.RIGHT, padx=2)
        ttk.Button(row1, text=_("Restore"), width=8, command=self.restore_game_bindings).pack(side=tk.RIGHT, padx=2)
        ttk.Button(row1, text=_("Backup"), width=8, command=self.backup_game_bindings).pack(side=tk.RIGHT, padx=2)

        # Row 2: Management Operations (Left)
        row2 = ttk.Frame(self.games_tab)
        row2.pack(fill=tk.X, pady=(2, 5))
        
        ttk.Button(row2, text=_("Add Game"), width=11, command=self.add_game_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text=_("Edit Game"), width=11, command=self.edit_game_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text=_("Remove Game"), width=13, command=self.remove_game_command).pack(side=tk.LEFT, padx=2)
        ttk.Frame(row2, width=10).pack(side=tk.LEFT) # Spacer
        ttk.Button(row2, text=_("Sync Bindings"), width=13, command=self.import_defaults_command).pack(side=tk.LEFT, padx=2)
        # Edit/Delete Triggers - Optional, confusing if mixed with Profile buttons. 
        # Ideally move to context menu. For now, omit to cleaner UI or add if requested.
        # User asked for "Delete method" for Profile. Profile delete is handled.


        # --- Game Notebook (Bindings | Macros | Settings) ---
        self.game_notebook = ttk.Notebook(self.games_tab)
        self.game_notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 1. Bindings Tab
        self.bindings_tab = ttk.Frame(self.game_notebook)
        self.game_notebook.add(self.bindings_tab, text=_("Bindings"))
        
        # 2. Macros Tab (Placeholder, defined below)
        self.macros_tab = ttk.Frame(self.game_notebook)
        
        # 3. Settings Tab (New Phase 14 Fix)
        self.settings_tab = ttk.Frame(self.game_notebook)
        self.game_notebook.add(self.settings_tab, text=_("Profile Settings"))
        
        # --- Populate Settings Tab ---
        
        # Profile Configuration Frame
        config_frame = ttk.LabelFrame(self.settings_tab, text=_("Profile Configuration"), padding="10")
        config_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Grid layout for inputs
        config_frame.columnconfigure(1, weight=1)
        
        # Process Name
        ttk.Label(config_frame, text=_("Process Name (e.g. X4.exe):")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.proc_name_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.proc_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Bindings Path
        ttk.Label(config_frame, text=_("Bindings File Path:")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.bind_path_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.bind_path_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(config_frame, text=_(" Browse "), command=self.browse_bindings_path).grid(row=1, column=2, padx=2)
        
        # Runtime Environment
        ttk.Label(config_frame, text=_("Runtime Environment:")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.runtime_env_var = tk.StringVar()
        self.runtime_combo = ttk.Combobox(config_frame, textvariable=self.runtime_env_var, values=["Native Linux", "Proton/Wine"], state="readonly")
        self.runtime_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Save Config Button
        ttk.Button(config_frame, text=_("Save Settings"), command=self.save_profile_settings).grid(row=0, column=2, rowspan=3, padx=2, sticky=tk.EW)
        
        # Multimedia Compliance Section
        media_group = ttk.LabelFrame(self.settings_tab, text=_("External Audio Assets"), padding="10")
        media_group.pack(fill=tk.X, pady=10, padx=10)
        
        # Row 1: Consent
        self.consent_var = tk.BooleanVar(value=False)
        self.consent_chk = ttk.Checkbutton(media_group, text=_("I confirm I own the audio files in this folder and will not redistribute them without permission."), variable=self.consent_var, command=self.toggle_audio_path_state)
        self.consent_chk.pack(anchor=tk.W)
        
        # Row 2: Path Selector
        path_frame = ttk.Frame(media_group)
        path_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(path_frame, text=_("Audio Directory:")).pack(side=tk.LEFT)
        self.audio_dir_var = tk.StringVar(value=self.config.get("CUSTOM_AUDIO_DIR", ""))
        self.audio_entry = ttk.Entry(path_frame, textvariable=self.audio_dir_var)
        self.audio_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.browse_audio_btn = ttk.Button(path_frame, text=_("Browse"), command=self.browse_audio_dir)
        self.browse_audio_btn.pack(side=tk.LEFT)
        
        # Initial State
        self.toggle_audio_path_state()

        # X4 Controller Sync Section (Hidden by default, shown via on_profile_select)
        self.x4_sync_frame = ttk.LabelFrame(self.settings_tab, text=_("X4 Foundations Controller Sync"), padding="10")
        
        ttk.Label(self.x4_sync_frame, text=_("Sync Controller Profiles (inputmap.xml) between Proton and Native Linux versions.")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(self.x4_sync_frame, text=_("Note: GOG versions are not supported for sync."), font=("Helvetica", 8, "italic")).pack(anchor=tk.W, pady=(0, 5))
        
        x4_btn_frame = ttk.Frame(self.x4_sync_frame)
        x4_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(x4_btn_frame, text=_("Sync: Proton ➜ Native"), command=lambda: self.sync_x4_command("proton_to_native")).pack(side=tk.LEFT, padx=5)
        ttk.Button(x4_btn_frame, text=_("Sync: Native ➜ Proton"), command=lambda: self.sync_x4_command("native_to_proton")).pack(side=tk.LEFT, padx=5)

        # Active Profile Bindings (Back to Bindings Tab)
        profile_frame = ttk.LabelFrame(self.bindings_tab, text=_("Active Profile Bindings"), padding="10")
        profile_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        
        # Treeview for Bindings
        game_cols = ("voice", "action", "key")
        self.game_tree = ttk.Treeview(profile_frame, columns=game_cols, show="headings")
        self.game_tree.heading("voice", text=_("Voice Command"))
        self.game_tree.heading("action", text=_("Game Action"))
        self.game_tree.heading("key", text=_("Mapped Key"))
        
        # Scrollbar for Bindings
        game_scroll = ttk.Scrollbar(profile_frame, orient=tk.VERTICAL, command=self.game_tree.yview)
        self.game_tree.configure(yscrollcommand=game_scroll.set)
        self.game_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        game_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Modify/Clear Buttons for Bindings
        bind_btn_frame = ttk.Frame(profile_frame)
        bind_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Button(bind_btn_frame, text=_("Modify Trigger"), width=15, command=self.edit_voice_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(bind_btn_frame, text=_("Clear Trigger"), width=15, command=self.delete_trigger_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(bind_btn_frame, text=_("Edit Key"), width=12, command=self.edit_key_binding_command).pack(side=tk.LEFT, padx=5)
        
        # Context Menu for Bindings
        self.game_tree.bind("<Button-3>", self.show_bindings_context_menu)
        game_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.game_tree.column("voice", width=200)
        self.game_tree.column("action", width=200)
        self.game_tree.column("key", width=100)
        
        # Phase 7: Custom Commands Section
        self.build_custom_commands_section()

        # 2. Macros Tab
        self.macros_tab = ttk.Frame(self.game_notebook)
        self.game_notebook.add(self.macros_tab, text=_("Macros (Beta)"))
        
        # Macro Layout: Left List (Macros), Right Editor (Steps)
        self.macro_paned = ttk.PanedWindow(self.macros_tab, orient=tk.HORIZONTAL)
        self.macro_paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left: Macro List
        macro_list_frame = ttk.LabelFrame(self.macro_paned, text=_("Defined Macros"), padding="5")
        self.macro_paned.add(macro_list_frame, weight=1)
        
        # Buttons for Macro List
        macro_btn_frame = ttk.Frame(macro_list_frame)
        macro_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Button(macro_btn_frame, text=_("New"), width=5, command=self.new_macro).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        ttk.Button(macro_btn_frame, text=_("Edit"), width=5, command=self.edit_macro).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        ttk.Button(macro_btn_frame, text=_("Del"), width=5, command=self.delete_macro).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        
        # Phase 1c: Added "source" column to show macro origin
        self.macro_tree = ttk.Treeview(macro_list_frame, columns=("triggers", "source"), show="headings")
        self.macro_tree.heading("triggers", text=_("Voice Triggers"))
        self.macro_tree.heading("source", text=_("Source"))
        self.macro_tree.column("triggers", width=200, stretch=True)
        self.macro_tree.column("source", width=120, stretch=False)
        self.macro_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure tag colors for different sources
        self.macro_tree.tag_configure("pack", foreground="blue")
        self.macro_tree.tag_configure("custom", foreground="green")
        self.macro_tree.tag_configure("builtin", foreground="gray")
        
        # Right: Step Editor
        macro_edit_frame = ttk.LabelFrame(self.macro_paned, text=_("Macro Steps"), padding="5")
        self.macro_paned.add(macro_edit_frame, weight=3)
        
        # Step Buttons
        step_btn_frame = ttk.Frame(macro_edit_frame)
        step_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Button(step_btn_frame, text=_("Add"), width=4, command=self.add_macro_step).pack(side=tk.LEFT, padx=1)
        ttk.Button(step_btn_frame, text=_("Edit"), width=4, command=self.edit_macro_step).pack(side=tk.LEFT, padx=1)
        ttk.Button(step_btn_frame, text=_("Del"), width=4, command=self.remove_macro_step).pack(side=tk.LEFT, padx=1)
        ttk.Button(step_btn_frame, text=_("↑"), width=2, command=self.move_step_up).pack(side=tk.LEFT, padx=1)
        ttk.Button(step_btn_frame, text=_("↓"), width=2, command=self.move_step_down).pack(side=tk.LEFT, padx=1)
        ttk.Button(step_btn_frame, text=_("Run"), width=4, command=self.test_macro).pack(side=tk.RIGHT, padx=1)
        
        # Step List
        self.step_tree = ttk.Treeview(macro_edit_frame, columns=("action", "bind", "delay"), show="headings")
        self.step_tree.heading("action", text=_("Action"))
        self.step_tree.heading("bind", text=_("Key"))
        self.step_tree.heading("delay", text=_("Delay"))
        self.step_tree.column("action", stretch=True)
        self.step_tree.column("bind", width=100, minwidth=100, anchor="center", stretch=False)
        self.step_tree.column("delay", width=90, minwidth=90, anchor="center", stretch=False)
        self.step_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind Selection Event
        self.macro_tree.bind("<<TreeviewSelect>>", self.on_macro_select)
        
        # 3. Reference Tab (For Generic Profiles)
        self.reference_tab = ttk.Frame(self.game_notebook)
        self.game_notebook.add(self.reference_tab, text=_("Reference File"))
        
        # Text Area for Reference
        self.reference_text = tk.Text(self.reference_tab, font=("Consolas", 10), wrap=tk.NONE) # No wrap for code/logs
        self.reference_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        ref_scroll_y = ttk.Scrollbar(self.reference_tab, orient=tk.VERTICAL, command=self.reference_text.yview)
        ref_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.reference_text.configure(yscrollcommand=ref_scroll_y.set)
        
        ref_scroll_x = ttk.Scrollbar(self.reference_tab, orient=tk.HORIZONTAL, command=self.reference_text.xview)
        ref_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.reference_text.configure(xscrollcommand=ref_scroll_x.set)
        
        self.reference_text.insert("1.0", "Select a Generic Profile with a Reference File to view it here.")
        self.reference_text.configure(state=tk.DISABLED)
        
        # Reference Label (For Info)
        self.ref_lbl = ttk.Label(self.reference_tab, text="...", font=("Arial", 10))
        self.ref_lbl.pack(side=tk.TOP, fill=tk.X, pady=5, padx=5)

        # Initial Populate
        self.refresh_game_bindings()
        self.refresh_profile_list()
        self.populate_macro_profiles()  # Phase 1c: Load macro profile options

    def save_game_mode_toggle(self):
        self.config.set("GAME_MODE_ENABLED", self.game_mode_enabled_var.get())
        self.config.save()
    
    def show_tooltip(self, event, text):
        """Show tooltip at cursor position."""
        if hasattr(self, 'tooltip_window'):
            return
        x, y = event.x_root + 10, event.y_root + 10
        self.tooltip_window = tk.Toplevel()
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=text, background="#ffffe0", 
                        relief="solid", borderwidth=1, font=("Helvetica", 9), padx=5, pady=2)
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide tooltip."""
        if hasattr(self, 'tooltip_window'):
            self.tooltip_window.destroy()
            del self.tooltip_window


    def refresh_game_bindings(self):
        if not hasattr(self, 'gm'):
            print("DEBUG: Initializing GameManager in Launcher...")
            self.gm = GameManager()
            self.gm.initialize()
            
        # Update Profiles List - REMOVED duplicative logic (handled by refresh_profile_list)
        # profile_names = [p.name for p in self.gm.profiles]
        # self.profile_combo['values'] = profile_names
        # if profile_names and not self.profile_var.get():
        #    self.profile_var.set(profile_names[0]) 
            
        # Detect Game
            
        # Detect Game
        game_name = self.gm.detect_game()
        
        # Update Status
        if game_name:
            self.game_mode_status.set(f"Detected: {game_name}")
        else:
            self.game_mode_status.set("Inactive (Say 'Enable Game Mode')")
            
        # Determine Active Profile for EDITOR
        # Prioritize Existing Active -> Manual Selection (Mapped) -> Detected Game -> Default
        active_profile = self.gm.active_profile
        print(f"DEBUG: refresh_game_bindings START | gm.active_profile: {active_profile} | Name: {getattr(active_profile, 'name', 'None')}")
        
        current_sel = self.profile_var.get()

        
        # 1. Validate Active Profile
        if active_profile:
             # Ensure it matches current selection if selection exists
             # But selection might be a display name, so be careful.
             pass 
        
        # 2. Manual Selection (if active_profile is None, e.g. startup)
        if not active_profile and current_sel:
             # Check Display Map first!
             real_name = current_sel
             if hasattr(self, 'profile_display_map') and current_sel in self.profile_display_map:
                  real_name = self.profile_display_map[current_sel]
                  
             for p in self.gm.profiles:
                 if p.name == real_name:
                     active_profile = p
                     break
        
        # 3. Detected Game (if no manual selection or match fail)
        if not active_profile and game_name:
            for p in self.gm.profiles:
                if p.name == game_name:
                    active_profile = p
                    # Sync UI - find display name?
                    # This is tricky without reverse map easily available globally
                    # But typically this runs when binding active so UI might not matter as much
                    self.profile_var.set(active_profile.name) # Sync UI
                    break

        # 4. Default Fallback
        if not active_profile and self.gm.profiles:
             # Only fallback if we REALLY have nothing
             # But be careful not to overwrite if we just deleted everything (empty list handled by implicit check)
             active_profile = self.gm.profiles[0]
             self.profile_var.set(active_profile.name) # Sync UI

        # Clear Tree
        for item in self.game_tree.get_children():
            self.game_tree.delete(item)
            
        # The user's instruction seems to imply active_profile should be fetched from gm.active_profile
        # However, active_profile is already determined above.
        # Assuming the intent is to add debug prints and an early exit if active_profile is still None
        # after the determination logic.
        if not active_profile:
             return
             
        print(f"DEBUG: Refreshing bindings for {active_profile.name}. Action count: {len(active_profile.actions)}")
        
        # Lazy Load Bindings if missing
        if not active_profile.bindings and hasattr(active_profile, 'load_bindings'):
             print(f"DEBUG: Bindings empty for {active_profile.name}, forcing load...")
             active_profile.load_bindings()

        # Sync Logic for other methods
        self.current_editing_profile = active_profile
        self.gm.active_profile = active_profile
        
        # Dynamic Filter Update
        if hasattr(active_profile, 'categories'):
            self.cat_combo['values'] = active_profile.categories
        else:
            self.cat_combo['values'] = ["All"]
            
        target_cat = self.cat_var.get()
        if target_cat not in self.cat_combo['values']:
             # Reset if invalid (e.g. switched from Elite to X4 while "SRV" was selected)
             target_cat = "All"
             self.cat_var.set("All")
        
        # Iterate through defined voice commands
        # First pass: Group actions by friendly name and check which are bound
        friendly_name_groups = {}
        action_order = []  # Track original order
        

        for action in active_profile.action_voice_map.keys():
            if target_cat != "All":
                cat = active_profile.get_category(action)
                if cat != target_cat:
                    continue
            
            friendly = active_profile.get_friendly_name(action)
            if friendly not in friendly_name_groups:
                friendly_name_groups[friendly] = []
                action_order.append(friendly)  # Track first occurrence
            
            # Get binding to check if bound
            binding = self._get_binding_display(active_profile, action)
            is_bound = binding != "NOT BOUND"
            

            friendly_name_groups[friendly].append((action, is_bound, binding))
        
        # Sort each group: bound keys first, then unbound
        # ONLY sort if there are multiple items (duplicates)
        for friendly, actions in friendly_name_groups.items():
            if len(actions) > 1:  # Only sort if there are duplicates!
                if "Weapon Group" in friendly:
                    print(f"BEFORE SORT {friendly}: {actions}")
                actions.sort(key=lambda x: (not x[1], x[0]))  # Sort by: bound first, then by action name
                if "Weapon Group" in friendly:
                    print(f"AFTER SORT {friendly}: {actions}")
        
        # Second pass: populate tree with slot indicators IN ORIGINAL ORDER
        friendly_name_tracker = {}
        
        for friendly in action_order:  # Use original order!
            action_list = friendly_name_groups[friendly]
            for action, is_bound, final_key_str in action_list:
                phrases = active_profile.action_voice_map.get(action, [])
                phrases_str = ", ".join(phrases)
                
                friendly_action = friendly
                
                # Add slot indicator if multiple bindings for this friendly name
                if len(action_list) > 1:
                    occurrence = friendly_name_tracker.get(friendly, 0) + 1
                    friendly_name_tracker[friendly] = occurrence
                    
                    slot_names = ["Primary", "Secondary", "Tertiary", "Quaternary"]
                    if occurrence <= len(slot_names):
                        friendly_action = f"{friendly} [{slot_names[occurrence-1]}]"
                    else:
                        friendly_action = f"{friendly} [Slot {occurrence}]"
                

                # Store REAL action name as tag for editing!
                item_id = self.game_tree.insert("", tk.END, values=(phrases_str, friendly_action, final_key_str), tags=(action,))
            
        self.gm.reload_macros()
        self.refresh_macros(active_profile)
        self.load_custom_commands() # Phase 7 Load
            
        # Phase 14: Load fields
        # Process Name Fallback
        p_name = active_profile.process_name
        if not p_name and hasattr(active_profile, 'default_process_name'):
            p_name = active_profile.default_process_name
        self.proc_name_var.set(p_name if p_name else "")
        
        # Show active binding path (Custom -> Reference -> Default -> None)
        display_path = active_profile.custom_bindings_path
        if not display_path and hasattr(active_profile, 'reference_path'):
             display_path = active_profile.reference_path
        if not display_path and hasattr(active_profile, 'default_path'):
             display_path = active_profile.default_path
        self.bind_path_var.set(display_path if display_path else "")
        
        # Runtime Env
        rt = getattr(active_profile, 'runtime_env', "Native Linux")
        self.runtime_env_var.set(rt)

        # Show/Hide X4 Sync Frame (Dynamic UI)
        if hasattr(self, 'x4_sync_frame'):
            if isinstance(active_profile, X4Profile):
                self.x4_sync_frame.pack(fill=tk.X, pady=10, padx=10, side=tk.BOTTOM)
            else:
                self.x4_sync_frame.pack_forget()
        
        # Reference File info
        active_path = getattr(active_profile, 'active_binds_path', "None")
        if active_path and len(active_path) > 60: active_path = "..." + active_path[-60:]
        
        info_text = f"Bindings File: {active_path}\nTotal Commands: {len(active_profile.bindings)}"
        
        # ED Note (Phase 16)
        if isinstance(active_profile, EliteDangerousProfile):
            info_text += "\n\n⚠️ NOTE: In-game key changes are saved to a separate 'Custom' file.\nIf you change keys in Elite, you may need to update the Binding Path (or import the Custom file)."
            
            # Warning for Standard Profiles (ControlSchemes)
            # Check actual path used
            path_to_check = getattr(active_profile, 'active_binds_path', "") or getattr(active_profile, 'custom_bindings_path', "") or getattr(active_profile, 'default_path', "")
            
            if path_to_check and "ControlSchemes" in path_to_check:
                 info_text += "\n\n⛔ CAUTION: You are viewing a Standard Profile (built-in).\nDo NOT edit this file directly. Updates or Verification will overwrite it.\nAlways use a 'Custom' profile for your own keybindings to ensure stability.\n💡 TIP: Use the 'Backup' button to save a safe copy of your configuration!"
            
        self.ref_lbl.config(text=info_text)
        
        # Update Reference Tab
        self.reference_text.config(state=tk.NORMAL)
        self.reference_text.delete("1.0", tk.END)
        
        if isinstance(active_profile, GenericGameProfile) and hasattr(active_profile, 'reference_path') and active_profile.reference_path:
             try:
                 with open(active_profile.reference_path, 'r', errors='replace') as f:
                     content = f.read(10000)
                     if len(content) == 10000: content += "\n... (Truncated)"
                     self.reference_text.insert("1.0", content)
             except Exception as e:
                 self.reference_text.insert("1.0", f"Error reading reference file: {e}")
        elif isinstance(active_profile, GenericGameProfile):
             self.reference_text.insert("1.0", "No reference file associated with this Generic Profile.")
        else:
             self.reference_text.insert("1.0", "Reference View is only for Generic Profiles.")
             
        self.reference_text.config(state=tk.DISABLED)

    def browse_bindings_path(self):
        current_path = self.bind_path_var.get().strip()
        initial_dir = "/"
        if current_path:
            if os.path.isfile(current_path):
                 initial_dir = os.path.dirname(current_path)
            elif os.path.isdir(current_path):
                 initial_dir = current_path
            elif os.path.exists(os.path.dirname(current_path)):
                 initial_dir = os.path.dirname(current_path)
                 
        filename = filedialog.askopenfilename(initialdir=initial_dir, title="Select Bindings File", filetypes=[("XML Files", "*.xml"), ("Binds Files", "*.binds"), ("All Files", "*.*")])
        if filename: self.bind_path_var.set(filename)

    def save_profile_settings(self):
        profile = self.get_active_profile()
        if not profile: return
        
        new_proc_name = self.proc_name_var.get().strip()
        profile.process_name = new_proc_name
        
        # Sync process_name to all profiles in the same group (Phase 15 request)
        synced_count = 0
        if hasattr(self, 'gm'):
             for p in self.gm.profiles:
                 if p.group == profile.group:
                     p.process_name = new_proc_name
                     p.save_config() # Save modular config for each
                     synced_count += 1
        
        # Save path to appropriate attribute (Profile specific)
        new_path = self.bind_path_var.get().strip()
        if isinstance(profile, GenericGameProfile):
             profile.reference_path = new_path
        else:
             profile.custom_bindings_path = new_path
             
        # Save Runtime Env
        profile.runtime_env = self.runtime_env_var.get()
        
        profile.save_config() # Save config for active profile again (redundant but safe)
        
        # Persist to global user_games.json (so new defaults stick on restart)
        self.gm.save_profiles()
        
        self.refresh_game_bindings() # Reload to apply changes
        msg = "Profile settings saved successfully."
        if synced_count > 1:
             msg += f"\n\nProcess Name updated for all {synced_count} profiles in '{profile.group}'."
        messagebox.showinfo("Saved", msg)
        
    def _build_display_name(self, profile):
        """Convert full profile name to display name.
        
        Centralizes display name logic to ensure consistency across UI.
        
        Example:
            "X4 Foundations (GOG) (inputmap.xml)" → "inputmap.xml"
            "Elite Dangerous (Keyboard)" → "Keyboard"
        
        Args:
            profile: GameProfile object
            
        Returns:
            str: Display-friendly name (variant only, without group prefix)
        """
        d_name = profile.name
        
        # Only strip if name follows pattern: "Group (variant)"
        if profile.group and profile.name.startswith(profile.group):
            remainder = profile.name[len(profile.group):].strip()
            if remainder.startswith("(") and remainder.endswith(")"):
                d_name = remainder[1:-1]  # Strip parentheses
        
        return d_name
        
    def get_active_profile(self):
        """Helper to get currently selected profile."""
        if not hasattr(self, 'gm'):
             return None
        
        # 1. Trust the UI Dropdown Selection First
        selected_name = self.profile_var.get()
        if selected_name:
            # Check if this is a display name that needs reverse mapping
            real_name = selected_name
            if hasattr(self, 'profile_display_map') and selected_name in self.profile_display_map:
                real_name = self.profile_display_map[selected_name]
            
            # Search by real name
            for p in self.gm.profiles:
                if p.name == real_name:
                    return p
                    
        # 2. Fallback to Detected Game
        game_name = self.gm.detect_game()
        if game_name:
             for p in self.gm.profiles:
                if p.name == game_name:
                    return p
                    
        # 3. Fallback to First Profile
        elif self.gm.profiles:
            return self.gm.profiles[0]
            
        return None

    def add_voice_command(self):
        profile = self.get_active_profile()
        if not profile: return
        
        all_actions = sorted(list(profile.actions.keys()))
        known_actions = set(profile.action_voice_map.keys())
        available = [a for a in all_actions if a not in known_actions]
        
        if not available:
            messagebox.showinfo(_("Complete"), _("All detected game actions typically have voice commands assigned!\nYou can still edit existing ones."))
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Voice Command")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text=_("Select Game Action:")).pack(pady=5)
        
        selected_action = tk.StringVar()
        combo = ttk.Combobox(dialog, textvariable=selected_action, values=available, state="readonly", height=15)
        combo.pack(fill=tk.X, padx=20, pady=5)
        if available: combo.current(0)
        
        ttk.Label(dialog, text=_("Voice Triggers (comma separated):")).pack(pady=5)
        trigger_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=trigger_var).pack(fill=tk.X, padx=20, pady=5)
        
        def on_add():
            action = selected_action.get()
            triggers_str = trigger_var.get()
            if not action or not triggers_str: return
            triggers = [t.strip().lower() for t in triggers_str.split(",") if t.strip()]
            if not triggers: return
            profile.action_voice_map[action] = triggers
            profile.save_commands()
            self.refresh_game_bindings()
            dialog.destroy()
            
        ttk.Button(dialog, text=_("Add Command"), command=on_add).pack(pady=10)
        combo.focus_set()

    def edit_key_binding_command(self):
        """Allows editing the game key binding for a selected action."""
        profile = self.get_active_profile()
        if not profile: return
        
        selected = self.game_tree.selection()
        if not selected: return
        
        item = self.game_tree.item(selected[0])
        # Get REAL action name from tags (not the friendly name from values!)
        item_tags = item.get('tags', [])
        action = item_tags[0] if item_tags else item['values'][1]  # Fallback to friendly name if no tag
        friendly_name = item['values'][1]  # For display in dialog
        current_key_display = item['values'][2] # "Ctrl + F1"
        
        # Simple Prompt for now
        # TODO: A dedicated KeyBindDialog that captures KeyPress events would be better
        # allowing for pressing the actual keycombo.
        
        # Custom KeyBind Dialog - use friendly name for title
        dialog = KeyBindDialog(self.root, f"Edit Binding: {friendly_name}", initial_value=current_key_display)
        self.root.wait_window(dialog)
        new_bind_str = dialog.result
        
        if new_bind_str is None or not new_bind_str.strip(): return
        
        # Parse Input "LeftControl + LeftAlt + H"
        
        parts = [p.strip() for p in new_bind_str.split("+") if p.strip()]
        if not parts: return

        base_key_raw = parts[-1]
        raw_mods = parts[:-1]
        
        # Robust Mapping based on Elite Dangerous XML names
        TK_ED_LOOKUP = {
            "enter": "Key_Enter", "return": "Key_Enter",
            "UI_Back": ["menu back", "back", "cancel"],
            "CycleNextPanel": ["next panel", "tab next"],
            "CyclePreviousPanel": ["previous panel", "tab previous"],
            "CycleNextPage": ["next page", "cycle next page"],
            "CyclePreviousPage": ["previous page", "cycle previous page"],
            "UIFocus": ["ui focus", "focus"],
            "space": "Key_Space", "backspace": "Key_Backspace", "tab": "Key_Tab",
            "escape": "Key_Escape", "delete": "Key_Delete", "insert": "Key_Insert",
            "home": "Key_Home", "end": "Key_End",
            "pageup": "Key_PageUp", "pagedown": "Key_PageDown", "prior": "Key_PageUp", "next": "Key_PageDown",
            "up": "Key_UpArrow", "down": "Key_DownArrow", "left": "Key_LeftArrow", "right": "Key_RightArrow",
            "capslock": "Key_CapsLock", "numlock": "Key_NumLock", "scrolllock": "Key_ScrollLock",
            "printscreen": "Key_PrintScreen", "pause": "Key_Pause",
            "numpad0": "Key_Numpad_0", "numpad1": "Key_Numpad_1", "numpad2": "Key_Numpad_2",
            "numpad3": "Key_Numpad_3", "numpad4": "Key_Numpad_4", "numpad5": "Key_Numpad_5",
            "numpad6": "Key_Numpad_6", "numpad7": "Key_Numpad_7", "numpad8": "Key_Numpad_8", "numpad9": "Key_Numpad_9",
            "numpadenter": "Key_Numpad_Enter", "numpadadd": "Key_Numpad_Add", "numpadsubtract": "Key_Numpad_Subtract",
            "numpadmultiply": "Key_Numpad_Multiply", "numpaddivide": "Key_Numpad_Divide", "numpaddecimal": "Key_Numpad_Decimal",
            "minus": "Key_Minus", "equal": "Key_Equals", "equals": "Key_Equals",
            "bracketleft": "Key_LeftBracket", "bracketright": "Key_RightBracket",
            "semicolon": "Key_Semicolon", "apostrophe": "Key_Apostrophe",
            "comma": "Key_Comma", "period": "Key_Period", "slash": "Key_Slash",
            "backslash": "Key_BackSlash", "grave": "Key_Grave",
            "shift": "Key_LeftShift", "leftshift": "Key_LeftShift", "rightshift": "Key_RightShift",
            "ctrl": "Key_LeftControl", "control": "Key_LeftControl", "leftcontrol": "Key_LeftControl", "rightcontrol": "Key_RightControl",
            "alt": "Key_LeftAlt", "leftalt": "Key_LeftAlt", "rightalt": "Key_RightAlt",
        }
        
        def map_key_to_ed(k):
            k_lower = k.lower().replace(" ", "")
            # Direct lookup
            if k_lower in TK_ED_LOOKUP: return TK_ED_LOOKUP[k_lower]
            
            # Single alphanumeric
            if len(k) == 1 and k.isalnum(): return f"Key_{k.upper()}"
            
            # F-keys
            if k_lower.startswith("f") and k_lower[1:].isdigit():
                 return f"Key_{k.upper()}"
                 
            # Fallback: Capitalize
            return f"Key_{k.capitalize()}"
            
        def map_mod_to_ed(m):
            m = m.lower().replace(" ", "")
            if "ctrl" in m or "control" in m: 
                return "Key_RightControl" if "right" in m else "Key_LeftControl"
            if "shift" in m: 
                return "Key_RightShift" if "right" in m else "Key_LeftShift"
            if "alt" in m: 
                return "Key_RightAlt" if "right" in m else "Key_LeftAlt"
            return None
            
        final_key = map_key_to_ed(base_key_raw)
        
        # Special check: If base_key is physically "Shift" (e.g. user mapped 'Shift' to an action?), 
        # it should be treated as a key, not a modifier? 
        # Actually ED allows mapping modifiers as primary keys.
        # But usually user inputs "Shift+A".
        
        final_mods = [map_mod_to_ed(m) for m in raw_mods]
        final_mods = [m for m in final_mods if m] # filter None
        
        key_data = {'key': final_key, 'mods': final_mods}
        
        success, err = profile.update_binding(action, key_data)
        if success:
             self.refresh_game_bindings()
             messagebox.showinfo("Success", f"Updated binding for {action}.", parent=self.root)
        else:
             messagebox.showerror("Error", f"Failed to update:\n{err}", parent=self.root)

    def remove_game_command(self):
        """Deletes all profiles for the currently active game group."""
        group = self.game_combo.get()
        if not group:
             messagebox.showinfo(_("Info"), _("No game group selected."))
             return
             
        # Count profiles in group
        print(f"DEBUG: remove_game_command | Target Group: '{group}'")
        print(f"DEBUG: Internal Profile Groups: {[p.group for p in self.gm.profiles]}")
        profiles_in_group = [p for p in self.gm.profiles if p.group == group]
        
        if not profiles_in_group:
             print(f"DEBUG: Match failed using ==. checking repr: {repr(group)}")
             # Fallback check?
             messagebox.showinfo(_("Info"), _("No profiles found in this group."))
             # Force refresh anyway just in case
             self.refresh_profile_list()
             return

        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove the ENTIRE game group '{group}'?\nThis will delete {len(profiles_in_group)} profiles and cannot be undone."):
            
            # Use batch removal
            removed_count = self.gm.remove_group(group)
            
            if removed_count > 0:
                messagebox.showinfo("Success", f"Removed {removed_count} profiles for '{group}'.")
                self.game_var.set("") 
                self.profile_var.set("") # Clear selection
                self.full_refresh_command() # Full Refresh to clean lists
            else:
                messagebox.showerror(_("Error"), _("Failed to remove profiles."))

    def delete_trigger_command(self):
        profile = self.get_active_profile()
        if not profile: return
        
        selected = self.game_tree.selection()
        if not selected:
             messagebox.showinfo(_("Info"), _("Select a row to delete."))
             return
             
        item = self.game_tree.item(selected[0])
        action = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete voice triggers for '{action}'?"):
             del profile.action_voice_map[action]
             profile.save_commands()
             self.refresh_game_bindings()

    def add_game_command(self):
        """Opens the Add Game Wizard."""
        # Use simple attribute check or fallback
        gm = getattr(self, 'gm', None) 
        if not gm: return
        AddGameDialog(self.games_tab, gm, self.refresh_profile_list)
        
    def edit_game_command(self):
        """Opens the Wizard in Edit Mode."""
        profile = self.get_active_profile()
        if not profile:
             messagebox.showinfo(_("Edit Game"), _("No profile selected."))
             return
        AddGameDialog(self.games_tab, self.gm, self.refresh_profile_list, existing_profile=profile)

    def sync_x4_command(self, direction):
        """Syncs X4 controller profiles."""
        profile = self.get_active_profile()
        if not profile or not isinstance(profile, X4Profile): return
        
        target = "Native Linux (~/.config)" if direction == "proton_to_native" else "Steam Proton (compatdata)"
        
        if messagebox.askyesno("Sync Controllers", f"Overwrite {target} controller profiles?\n\nThis will copy 'inputmap.xml' and custom profiles.\nExisting files will be backed up."):
             success, msg = profile.sync_profiles(direction)
             if success:
                 messagebox.showinfo("Sync Complete", msg)
             else:
                 messagebox.showerror("Sync Failed", msg)

    def import_defaults_command(self):
        """Imports standard profiles for the active game group."""
        profile = self.get_active_profile()
        # Get UI Selection first as the "Intent"
        selected_group = self.game_combo.get()
        print(f"DEBUG: import_defaults_command | Profile: {profile} | Combo Group: {selected_group}")
        
        # Determine Game Type
        is_ed = False
        is_x4 = False
        
        # Only trust profile if it MATCHES the selected group
        # Otherwise we might have fallen back to a default profile (like X-Plane) because the group is empty.
        valid_profile = None
        if profile and getattr(profile, 'group', None) == selected_group:
             valid_profile = profile
        
        group_to_use = selected_group # Default to UI selection
        
        if valid_profile:
             print(f"DEBUG: Valid Profile found: {valid_profile.name} | Type: {type(valid_profile)}")
             is_ed = isinstance(valid_profile, EliteDangerousProfile)
             is_x4 = isinstance(valid_profile, X4Profile)
             group_to_use = valid_profile.group
             
             # Fallback: If profile is Generic but group matches
             if not is_ed and not is_x4:
                  if group_to_use and "Elite Dangerous" in group_to_use: 
                      is_ed = True
                  elif group_to_use and "X4 Foundations" in group_to_use: 
                      is_x4 = True
                  
        elif selected_group:
             # Fallback to string matching on UI selection
             if "Elite Dangerous" in selected_group:
                 is_ed = True
             elif "X4 Foundations" in selected_group:
                 is_x4 = True
        
        print(f"DEBUG: Decision -> is_ed={is_ed}, is_x4={is_x4}, group_to_use='{group_to_use}'")
                 
        if is_ed:
            if messagebox.askyesno(_("Import Defaults"), _("Scan and import standard Elite Dangerous ControlSchemes?\nThis may double up profiles if you already have them, but skips duplicate names.")):
                count, names = self.gm.import_ed_standard_profiles(target_group=group_to_use)
                if count > 0:
                    messagebox.showinfo("Import Complete", f"Imported {count} profiles:\n" + ", ".join(names[:5]) + "...")
                    self.full_refresh_command()
                else:
                    messagebox.showinfo(_("Import Complete"), _("No profiles found. (Check console for path/parsing errors)"))
        elif is_x4:
            if messagebox.askyesno("Sync Bindings", f"Sync profiles for '{group_to_use}'?\n\nThis will:\n- Import new binding files\n- Remove orphaned profiles"):
                # Pass explicit target group from UI if profile is None
                added, removed, names = self.gm.import_x4_profiles(target_group=group_to_use)
                
                # Build message
                msg_parts = []
                if added > 0:
                    msg_parts.append(f"✅ Added {added} profile(s)")
                if removed > 0:
                    msg_parts.append(f"♻️ Removed {removed} orphaned profile(s)")
                if not msg_parts:
                    msg_parts.append("No changes needed - already in sync!")
                
                message = "\n".join(msg_parts)
                if added > 0 and names:
                    message += f"\n\nNew profiles:\n" + "\n".join(f"  • {n}" for n in names[:5])
                    if len(names) > 5:
                        message += f"\n  ... and {len(names) - 5} more"
                
                messagebox.showinfo("Sync Complete", message)
                self.full_refresh_command()

        else:
             messagebox.showinfo("Import", f"Please select a supported Game Group (Elite or X4) to import defaults.\nCurrent Group: '{group_to_use}'")
    def refresh_profile_list(self, new_selection=None):
        """Reloads profile list and populates Two-Tier combos."""
        print(f"DEBUG: LauncherGamesTab.refresh_profile_list called with new_selection='{new_selection}'")
        if not hasattr(self, 'gm'): 
            print("DEBUG: No gm attribute, returning")
            return
        
        print(f"DEBUG: Total profiles in gm: {len(self.gm.profiles)}")
        print(f"DEBUG: Profile names: {[p.name for p in self.gm.profiles]}")
        
        # 1. Populate Game Groups
        # Ensure groups are unique strings
        raw_groups = [p.group for p in self.gm.profiles if p.group]
        groups = sorted(list(set(raw_groups)))
        print(f"DEBUG: Groups found: {groups}")
        self.game_combo['values'] = groups
        
        target_profile = None
        
        # Determine Target Profile
        if new_selection and new_selection != 'None':
             print(f"DEBUG: Looking for new_selection profile: '{new_selection}'")
             target_profile = next((p for p in self.gm.profiles if p.name == new_selection), None)
             print(f"DEBUG: Found target_profile: {target_profile}")
        elif self.gm.active_profile:
             print(f"DEBUG: Using active_profile: {self.gm.active_profile.name}")
             target_profile = self.gm.active_profile
             
        print(f"DEBUG: target_profile final: {target_profile.name if target_profile else 'None'}")
             
        # Set Selection
        if target_profile and target_profile.group in groups:
            print(f"DEBUG: Setting game combo to group: {target_profile.group}")
            idx = groups.index(target_profile.group)
            if self.game_combo.current() != idx:
                self.game_combo.current(idx)
                
            # Always populate profile list for this group, even if selection didn't change
            # DISPLAY LOGIC: Use simplified names for UI, map back to real names
            # Clear stale mappings first!
            self.profile_display_map = {}
            display_names = []
            group_p_objs = [p for p in self.gm.profiles if p.group == target_profile.group]
            print(f"DEBUG: Profiles in group '{target_profile.group}': {[p.name for p in group_p_objs]}")
            
            # Build display names using centralized method
            for p in group_p_objs:
                d_name = self._build_display_name(p)  # ← Consistent logic!
                self.profile_display_map[d_name] = p.name
                display_names.append(d_name)

                 
            self.profile_combo['values'] = display_names
            print(f"DEBUG: Set profile_combo values to: {display_names}")
            
            # Reverse lookup for current selection
            current_disp = next((k for k, v in self.profile_display_map.items() if v == target_profile.name), target_profile.name)
            self.profile_var.set(current_disp)
            print(f"DEBUG: Set profile_var to: {current_disp}")
            # self.profile_combo.set(current_disp) # Force?
                 
            # Note: We do NOT need to set self.gm.active_profile here, it's already set or we are just refreshing list.
            
        elif groups:
             # Default to first group
             self.game_combo.current(0)
             self.on_game_select(None)

    def on_game_select(self, event):
        group = self.game_combo.get()
        print(f"DEBUG: Game selected: {group}")
        
        # Filter profiles for this group
        group_p_objs = [p for p in self.gm.profiles if p.group == group]
        
        # DISPLAY LOGIC - Clear and rebuild with centralized method
        self.profile_display_map = {}
        display_names = []
        for p in group_p_objs:
            d_name = self._build_display_name(p)  # ← Same logic as refresh!
            self.profile_display_map[d_name] = p.name
            display_names.append(d_name)
             
        self.profile_combo['values'] = display_names
        
        if display_names:
             self.profile_combo.current(0)
             # Force variable update just in case
             self.profile_var.set(display_names[0])
             self.on_profile_select(None)
             # Note: on_profile_select already calls save_profiles, so we're good
        else:
             print("DEBUG: No profiles found for group!")
             self.profile_var.set("")
             self.profile_combo.set("")
             # CLEAR active profile to prevent ghosting
             self.gm.active_profile = None
             # Save the cleared state
             self.gm.save_profiles()
             # Also clear UI fields?
             # self.refresh_game_bindings() might be needed to clear the form
             self.refresh_game_bindings()

    def on_profile_select(self, event):
        disp_name = self.profile_combo.get()
        if not disp_name: return
        
        # Resolve real name
        real_name = disp_name
        if hasattr(self, 'profile_display_map') and disp_name in self.profile_display_map:
             real_name = self.profile_display_map[disp_name]
             
        profile = next((p for p in self.gm.profiles if p.name == real_name), None)
        
        if profile:
             if profile != self.gm.active_profile:
                 self.gm.active_profile = profile
                 self.refresh_game_bindings()
                 
             # Save Selection (New Persistence)
             self.gm.save_profiles()
             
             # Legacy backup (optional, but let's stick to one source of truth)
             # self.config.set("LAST_GAME_PROFILE", real_name)
             # self.config.save()
             

    def on_macro_profile_select(self, event):
        """Handle macro profile selection (Built-in, Custom, or Pack)."""
        macro_profile = self.macro_profile_combo.get()
        if not macro_profile:
            return
        
        # Update GameManager's active macro profile
        if hasattr(self, 'gm') and self.gm:
            self.gm.active_macro_profile = macro_profile
            
            # PHASE 13 FIX: Persist Selection to Profile
            if self.gm.active_profile:
                self.gm.active_profile.selected_macro_profile = macro_profile
                self.gm.save_profiles()
            
            # Reload macros from new source
            self.gm.reload_macros()
            self.refresh_game_bindings()
            
            print(f"✅ Macro Profile switched to: {macro_profile}")
    
    def populate_macro_profiles(self):
        """Populate Macro Profile dropdown with Built-in, Custom profiles, and installed packs."""
        options = ["Built-in"]
        
        # Add custom macro profiles for current game
        if hasattr(self, 'gm') and self.gm:
            custom_profiles = self.gm.get_custom_macro_profiles()
            if custom_profiles:
                options.extend(sorted(custom_profiles))
            else:
                # Default custom profile if none exist
                options.append("Custom")
        
        # Add separator and LAL packs
        if hasattr(self, 'gm') and self.gm and hasattr(self.gm, 'lal_manager'):
            pack_names = list(self.gm.lal_manager.packs.keys())
            if pack_names:
                options.append("───────")  # Visual separator
                options.extend(sorted(pack_names))
        
        self.macro_profile_combo['values'] = options
        
        # Set current selection if active_macro_profile is set
        if hasattr(self, 'gm') and self.gm and hasattr(self.gm, 'active_macro_profile'):
            current = self.gm.active_macro_profile
            if current in options:
                self.macro_profile_var.set(current)
    
    def new_macro_profile(self):
        """Create a new custom macro profile."""
        if not hasattr(self, 'gm') or not self.gm or not self.gm.active_profile:
            messagebox.showinfo(_("No Game Selected"), _("Please select a game first."), parent=self.games_tab)
            return
        
        name = simpledialog.askstring(
            "New Macro Profile",
            "Enter a name for the new macro profile:\n(e.g., 'Combat Macros', 'Trading Macros')",
            parent=self.games_tab
        )
        
        if not name:
            return
        
        # Validate name
        name = name.strip()
        if not name:
            messagebox.showwarning(_("Invalid Name"), _("Profile name cannot be empty."), parent=self.games_tab)
            return
        
        # Check if already exists
        existing = self.gm.get_custom_macro_profiles()
        if name in existing:
            messagebox.showwarning("Duplicate Name", f"A profile named '{name}' already exists.", parent=self.games_tab)
            return
        
        # Create the profile
        success = self.gm.create_custom_macro_profile(name)
        if success:
            # Refresh dropdown and select new profile
            self.populate_macro_profiles()
            self.macro_profile_var.set(name)
            self.gm.active_macro_profile = name
            self.refresh_game_bindings()
            messagebox.showinfo("Success", f"Created macro profile: {name}", parent=self.games_tab)
        else:
            messagebox.showerror(_("Error"), _("Failed to create macro profile."), parent=self.games_tab)
    
    def rename_macro_profile(self):
        """Rename the currently selected custom macro profile."""
        if not hasattr(self, 'gm') or not self.gm:
            return
        
        current = self.macro_profile_var.get()
        
        # Can only rename custom profiles
        if current == "Built-in" or current == "───────":
            messagebox.showinfo(
                "Cannot Rename",
                "Built-in profiles and separators cannot be renamed.",
                parent=self.games_tab
            )
            return
        
        # Check if it's a pack
        if hasattr(self.gm, 'lal_manager') and current in self.gm.lal_manager.packs:
            messagebox.showinfo(
                "Cannot Rename Pack",
                f"'{current}' is a content pack and cannot be renamed.\n\nOnly custom macro profiles can be renamed.",
                parent=self.games_tab
            )
            return
        
        new_name = simpledialog.askstring(
            "Rename Macro Profile",
            f"Enter new name for '{current}':",
            initialvalue=current,
            parent=self.games_tab
        )
        
        if not new_name or new_name == current:
            return
        
        new_name = new_name.strip()
        if not new_name:
            messagebox.showwarning(_("Invalid Name"), _("Profile name cannot be empty."), parent=self.games_tab)
            return
        
        # Check if new name already exists
        existing = self.gm.get_custom_macro_profiles()
        if new_name in existing:
            messagebox.showwarning("Duplicate Name", f"A profile named '{new_name}' already exists.", parent=self.games_tab)
            return
        
        # Rename the profile
        success = self.gm.rename_custom_macro_profile(current, new_name)
        if success:
            self.populate_macro_profiles()
            self.macro_profile_var.set(new_name)
            self.gm.active_macro_profile = new_name
            messagebox.showinfo("Success", f"Renamed to: {new_name}", parent=self.games_tab)
        else:
            messagebox.showerror(_("Error"), _("Failed to rename macro profile."), parent=self.games_tab)
    
    def delete_macro_profile(self):
        """Delete the currently selected custom macro profile."""
        if not hasattr(self, 'gm') or not self.gm:
            return
        
        current = self.macro_profile_var.get()
        
        # Can only delete custom profiles
        if current == "Built-in" or current == "───────":
            messagebox.showinfo(
                "Cannot Delete",
                "Built-in profiles cannot be deleted.",
                parent=self.games_tab
            )
            return
        
        # Check if it's a pack
        if hasattr(self.gm, 'lal_manager') and current in self.gm.lal_manager.packs:
            messagebox.showinfo(
                "Cannot Delete Pack",
                f"'{current}' is a content pack.\n\nTo remove packs, use the Content Packs tab.",
                parent=self.games_tab
            )
            return
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete macro profile '{current}'?\n\nThis will permanently remove all macros in this profile.",
            parent=self.games_tab
        ):
            return
        
        # Delete the profile
        success = self.gm.delete_custom_macro_profile(current)
        if success:
            # Switch to Built-in
            self.gm.active_macro_profile = "Built-in"
            self.populate_macro_profiles()
            self.macro_profile_var.set("Built-in")
            self.refresh_game_bindings()
            messagebox.showinfo("Success", f"Deleted macro profile: {current}", parent=self.games_tab)
        else:
            messagebox.showerror(_("Error"), _("Failed to delete macro profile."), parent=self.games_tab)

    def backup_game_bindings(self):
        profile = self.get_active_profile()
        if not profile:
             return
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        suggested_name = f"{profile.name.replace(' ', '_')}_Backup_{timestamp}.binds"
        last_dir = self.config.get("LAST_BACKUP_DIR") or os.path.expanduser("~")

        dest_path = filedialog.asksaveasfilename(title="Backup Bindings As...", initialdir=last_dir, initialfile=suggested_name, filetypes=[("Bindings Files", "*.binds"), ("All Files", "*.*")])
        if not dest_path: return 
        
        self.config.set("LAST_BACKUP_DIR", os.path.dirname(dest_path))
        self.config.save()
        
        success, msg = profile.backup_bindings(dest_path)
        if success: messagebox.showinfo("Success", msg)
        else: messagebox.showerror("Backup Failed", msg)

    def restore_game_bindings(self):
        profile = self.get_active_profile()
        if not profile:
             messagebox.showerror(_("Error"), _("No game profile loaded."))
             return
        last_dir = self.config.get("LAST_BACKUP_DIR") or os.path.expanduser("~")
            
        source_path = filedialog.askopenfilename(title="Select Bindings to Restore", initialdir=last_dir, filetypes=[("Bindings Files", "*.binds"), ("All Files", "*.*")])
        if not source_path: return
        
        self.config.set("LAST_BACKUP_DIR", os.path.dirname(source_path))
        self.config.save()
        
        target = profile.active_binds_path
        if not target:
             messagebox.showerror(_("Error"), _("Internal Error: Active bindings path is unknown."))
             return
        confirm = messagebox.askyesno("⚠️ OVERWRITE WARNING", f"This will OVERWRITE your current bindings file:\n\n{target}\n\nAre you sure you want to replace it with the selected file?", icon='warning')
        if not confirm: return
        
        success, msg = profile.restore_bindings(source_path)
        if success:
             messagebox.showinfo("Restore Successful", msg)
             self.refresh_game_bindings()
        else:
             messagebox.showerror("Restore Failed", msg)

    def rebind_game_command(self):
        profile = self.get_active_profile()
        if not profile: return
        selected = self.game_tree.selection()
        if not selected:
             messagebox.showinfo(_("Info"), _("Select an action to rebind."))
             return
        if profile.is_running():
            confirm = messagebox.askokcancel(_("⚠️ Game is Running"), _("Elite Dangerous appears to be running.\n\nChanges made now may NOT take effect immediately or could be overwritten by the game.\n\nContinue anyway?"))
            if not confirm: return

        item = self.game_tree.item(selected[0])
        action = item['values'][1]
        self.show_binding_dialog(profile, action)

    def show_binding_dialog(self, profile, action):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Rebind: {action}")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text=f"Press intended key combination for:\n{action}", font=("Arial", 12), justify=tk.CENTER).pack(pady=20)
        lbl_detected = ttk.Label(dialog, text=_("Waiting..."), font=("Arial", 14, "bold"), foreground="blue")
        lbl_detected.pack(pady=10)
        
        captured_data = {"key": None, "mods": []}
        
        def on_key(event):
            keysym = event.keysym.lower()
            mods = []
            if event.state & 0x0001: mods.append("shift_l")
            if event.state & 0x0004: mods.append("control_l")
            if event.state & 0x0008 or event.state & 0x0080: mods.append("alt_l")
            
            ed_key = profile.TK_TO_ED_MAP.get(keysym, f"Key_{keysym.upper()}")
            ed_mods = []
            for m in mods:
                if m != keysym: 
                     ed_mods.append(profile.TK_TO_ED_MAP.get(m, "Key_" + m.capitalize()))
            
            display_str = " + ".join(ed_mods + [ed_key])
            lbl_detected.config(text=display_str)
            captured_data["key"] = ed_key
            captured_data["mods"] = ed_mods
            return "break"
            
        dialog.bind("<Key>", on_key)
        dialog.focus_set()
        
        def on_apply():
            if not captured_data["key"]:
                messagebox.showwarning(_("Warning"), _("No key detected."))
                return
            collisions = profile.check_collisions(captured_data, proposed_action=action)
            # Remove self is now handled in game_manager, but harmless to keep if logic changes
            if action in collisions: collisions.remove(action)
            
            if collisions:
                conflict_list = ", ".join(collisions)
                confirm = messagebox.askyesno("Conflict Warning", f"Connection Warning!\n\nThe key combination is already bound to:\n\n{conflict_list}\n\nDo you want to overwrite it?")
                if not confirm: return
                for conflict in collisions:
                    # Strip Category suffix "ActionName (Category)" -> "ActionName"
                    if " (" in conflict and conflict.endswith(")"):
                         raw_action = conflict.rsplit(" (", 1)[0]
                    else:
                         raw_action = conflict
                    profile.unbind_action(raw_action)
            success, msg = profile.update_binding(action, captured_data)
            if success:
                messagebox.showinfo("Success", msg)
                self.refresh_game_bindings()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)
                
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(side=tk.BOTTOM, pady=20)
        ttk.Button(btn_frame, text=_("Apply"), command=on_apply).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text=_("Cancel"), command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def full_refresh_command(self):
        """Refreshes both the Profile List and the Bindings UI."""
        self.refresh_profile_list()
        self.refresh_game_bindings()
        
    def refresh_macros(self, profile):
        for item in self.macro_tree.get_children():
            self.macro_tree.delete(item)
        if not profile: return
        
        # Phase 1c: Include source information
        for name, data in profile.macros.items():
            triggers = ", ".join(data.get("triggers", []))
            
            # Get macro source
            source = self.gm.get_macro_source(name) if hasattr(self, 'gm') else "Unknown"
            
            # Determine tag for color coding
            if "Pack:" in source:
                tag = "pack"
            elif source == "Custom":
                tag = "custom"
            else:  # Built-in or Unknown
                tag = "builtin"
            
            self.macro_tree.insert("", tk.END, values=(triggers, source), iid=name, tags=(tag,))

    def new_macro(self):
        profile = self.get_active_profile()
        if not profile: return
        name = simpledialog.askstring("New Macro", "Enter a unique internal name for this macro (e.g. 'DockRequest'):")
        if not name or name in profile.macros:
             messagebox.showwarning(_("Invalid"), _("Name empty or already exists."))
             return
        triggers_str = simpledialog.askstring("Voice Triggers", "Enter voice triggers (comma separated):")
        if not triggers_str: return
        triggers = [t.strip().lower() for t in triggers_str.split(",") if t.strip()]
        profile.macros[name] = {"triggers": triggers, "steps": []}
        profile.save_macros()
        self.refresh_macros(profile)
        self.macro_tree.selection_set(name)

    def delete_macro(self):
        profile = self.get_active_profile()
        if not profile: return
        selected = self.macro_tree.selection()
        if not selected: return
        name = selected[0]
        
        # Phase 1c: Check if macro is deletable
        source = self.gm.get_macro_source(name) if hasattr(self, 'gm') else "Unknown"
        if source != "Custom":
            messagebox.showinfo(
                "Read-Only",
                f"Cannot delete {source} macros.\n\nThis macro is from: {source}\n\nOnly Custom macros can be deleted.",
                parent=self.games_tab
            )
            return
        
        if messagebox.askyesno("Confirm", f"Delete macro '{name}'?"):
            del profile.macros[name]
            profile.save_macros()
            self.refresh_macros(profile)
            for item in self.step_tree.get_children():
                self.step_tree.delete(item)

    def edit_macro(self):
        profile = self.get_active_profile()
        if not profile: return
        selected = self.macro_tree.selection()
        if not selected:
             messagebox.showinfo(_("Select"), _("Please select a macro."))
             return
        name = selected[0]
        if name not in profile.macros: return
        
        # Phase 1c: Check if macro is editable
        source = self.gm.get_macro_source(name) if hasattr(self, 'gm') else "Unknown"
        if source != "Custom":
            messagebox.showinfo(
                "Read-Only",
                f"Cannot edit {source} macros.\n\nThis macro is from: {source}\n\nOnly Custom macros can be edited.",
                parent=self.games_tab
            )
            return
        
        current_triggers = ", ".join(profile.macros[name].get("triggers", []))
        triggers_str = simpledialog.askstring("Edit Triggers", "Enter voice triggers (comma separated):", initialvalue=current_triggers)
        if triggers_str is None: return 
        triggers = [t.strip().lower() for t in triggers_str.split(",") if t.strip()]
        if not triggers:
             messagebox.showwarning(_("Warning"), _("Triggers cannot be empty."))
             return
        profile.macros[name]["triggers"] = triggers
        profile.save_macros()
        self.refresh_macros(profile)
        self.macro_tree.selection_set(name)

    def on_macro_select(self, event):
        profile = self.get_active_profile()
        if not profile: return
        for item in self.step_tree.get_children():
            self.step_tree.delete(item)
        selected = self.macro_tree.selection()
        if not selected: return
        name = selected[0]
        if name not in profile.macros: return
        steps = profile.macros[name].get("steps", [])
        for i, step in enumerate(steps):
            if "key" in step:
                 bind_str = f"{step['key']} (Custom)"
            else:
                 bind_str = self._get_binding_display(profile, step['action'])
            self.step_tree.insert("", tk.END, values=(step['action'], bind_str, step.get('delay', 100)), iid=f"{name}_step_{i}")

    def _get_binding_display(self, profile, action):
        # Resolve potentially aliased Action ID to actual XML Tag(s)
        tags_to_check = [action]
        if hasattr(profile, 'virtual_tag_map') and action in profile.virtual_tag_map:
            tags_to_check.extend(profile.virtual_tag_map[action])
            
        binding_data = None
        for tag in tags_to_check:
            if tag in profile.actions:
                binding_data = profile.actions[tag]
                break
                

        
        if not binding_data: return "NOT BOUND"
        key_code, mods = binding_data
        
        # Helper to format a single key
        def fmt_key(k):
             k = str(k)
             # X4 specific
             if k == "None": return ""
             
             if k.startswith("Key_"):
                 # Handle "Key_LeftShift" -> "LeftShift"
                 k = k.replace("Key_", "")
                 # Common simplifications
                 if "LeftControl" in k or "RightControl" in k: return "Ctrl"
                 if "LeftShift" in k or "RightShift" in k: return "Shift"
                 if "LeftAlt" in k or "RightAlt" in k: return "Alt"
                 # Space, Enter, F1, etc are fine as-is or Capitalized
                 return k
             return k

        mod_names = []
        for m in mods:
            m_str = str(m)
            # Check for pynput keys (X4 Parser)
            if "Key.shift" in m_str: mod_names.append("Shift")
            elif "Key.ctrl" in m_str: mod_names.append("Ctrl")
            elif "Key.alt" in m_str: mod_names.append("Alt")
            
            # Check for legacy Int codes
            elif m_str in ["29", "97"]: mod_names.append("Ctrl")
            elif m_str in ["42", "54"]: mod_names.append("Shift")
            elif m_str in ["56", "100"]: mod_names.append("Alt")
            
            # Check for ED strings
            elif m_str.startswith("Key_"):
                 mod_names.append(fmt_key(m_str))
            else:
                 # Clean up generic Key.foo
                 if m_str.startswith("Key."):
                     mod_names.append(m_str.replace("Key.", "").capitalize())
                 else:
                     mod_names.append(m_str)

        key_name = key_code
        # Try Int Logic (Legacy)
        try:
            kc_int = int(key_code)
            # ... (Map removed for brevity in snippet, assuming integer logic is mostly legacy/ED specific if simple ints used)
            # Actually, X4 uses strings now. So we mostly skip this.
            pass
        except:
            # String Logic
            key_name = fmt_key(key_name)
                 
        start_codes = {
            2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9", 11: "0",
            16: "Q", 17: "W", 18: "E", 19: "R", 20: "T", 21: "Y", 22: "U", 23: "I", 24: "O", 25: "P",
            26: "[", 27: "]", 28: "Enter",
            30: "A", 31: "S", 32: "D", 33: "F", 34: "G", 35: "H", 36: "J", 37: "K", 38: "L",
            39: ";", 40: "'", 41: "`", 43: "\\",
            44: "Z", 45: "X", 46: "C", 47: "V", 48: "B", 49: "N", 50: "M",
            51: ",", 52: ".", 53: "/", 57: "Space",
            56: "Alt", 100: "AltGr" # Fix for scan code 56
        }
        
        # If Key is an INT (Elite Dangerous uses scancodes)
        if isinstance(key_code, int):
             if key_code in start_codes: key_name = start_codes[key_code]
        # X4 returns strings like "1", "2" - DON'T convert these via scancode map!
        # The scancode for "1" is 2, for "2" is 3, etc. - wrong!

        # Combine
        parts = mod_names + [str(key_name)]
        # Filter empty strings
        parts = [p for p in parts if p]
        
        return " + ".join(parts)

    def add_macro_step(self):
        self._show_step_dialog(mode="add")

    def edit_macro_step(self):
        self._show_step_dialog(mode="edit")

    def _show_step_dialog(self, mode="add"):
        profile = self.get_active_profile()
        if not profile: return
        macro_sel = self.macro_tree.selection()
        if not macro_sel: 
             messagebox.showinfo(_("Select Macro"), _("Please select a macro first."))
             return
        macro_name = macro_sel[0]
        
        edit_idx = -1
        current_step = None
        if mode == "edit":
             step_sel = self.step_tree.selection()
             if not step_sel:
                  messagebox.showinfo(_("Select Step"), _("Please select a step to edit."))
                  return
             edit_idx = self.step_tree.index(step_sel[0])
             current_step = profile.macros[macro_name]["steps"][edit_idx]

        dialog = tk.Toplevel(self.root)
        dialog.title("Macro Step")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text=_("Action:")).pack(pady=5)
        
        custom_cache = {}
        for s in profile.macros[macro_name]["steps"]:
            if "key" in s:
                custom_cache[s["action"]] = s["key"]
        
        all_actions = sorted(list(profile.actions.keys()))
        custom_names = sorted(list(custom_cache.keys()))
        combo_values = ["-- Custom Action --"] + custom_names + all_actions
        
        sel_action = tk.StringVar()
        combo = ttk.Combobox(dialog, textvariable=sel_action, values=combo_values, state="readonly")
        combo.pack(fill=tk.X, padx=20)
        
        if mode == "edit" and current_step:
            sel_action.set(current_step['action'])
        else:
            combo.current(0)
            
        ttk.Label(dialog, text=_("Delay after (ms):")).pack(pady=5)
        delay_var = tk.StringVar(value="100")
        if mode == "edit" and current_step:
             delay_var.set(str(current_step.get('delay', 100)))
        ttk.Entry(dialog, textvariable=delay_var).pack(fill=tk.X, padx=20)
        
        # Audio Feedback Selector (Sound Pool - Option A)
        ttk.Label(dialog, text=_("Audio Feedback / Sound Pool:")).pack(pady=5)
        
        # Frame for List and Right-side buttons
        pool_frame = ttk.Frame(dialog)
        pool_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Listbox for files
        pool_list = tk.Listbox(pool_frame, height=4, selectmode=tk.EXTENDED)
        pool_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        pool_scroll = ttk.Scrollbar(pool_frame, orient=tk.VERTICAL, command=pool_list.yview)
        pool_list.config(yscrollcommand=pool_scroll.set)
        pool_scroll.pack(side=tk.LEFT, fill=tk.Y)
        
        # Button column
        btn_col = ttk.Frame(pool_frame)
        btn_col.pack(side=tk.LEFT, fill=tk.Y, padx=(5,0))
        
        def add_audio_files():
            # Allow multi-select
            files = filedialog.askopenfilenames(
                title="Add Audio Files",
                filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac"), ("All Files", "*.*")],
                parent=dialog
            )
            for f in files:
                pool_list.insert(tk.END, f)
                
        def remove_audio_files():
            selection = pool_list.curselection()
            if not selection: return
            # Remove in reverse order
            for i in reversed(selection):
                pool_list.delete(i)
                
        ttk.Button(btn_col, text="➕", width=3, command=add_audio_files).pack(pady=(0, 5))
        ttk.Button(btn_col, text="➖", width=3, command=remove_audio_files).pack()
        
        # Playback Mode
        mode_frame = ttk.Frame(dialog)
        mode_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        
        mode_var = tk.StringVar(value="Random")
        modes = ["Random", "Simultaneous", "Sequential (Round-Robin)"]
        mode_combo = ttk.Combobox(mode_frame, textvariable=mode_var, values=modes, state="readonly", width=25)
        mode_combo.pack(side=tk.LEFT, padx=5)
        
        # Populate if editing
        if mode == "edit" and current_step:
            # Check for new pool format
            pool = current_step.get("audio_pool", [])
            existing_mode = current_step.get("playback_mode", "Random")
            
            # Fallback to legacy single file if pool is empty
            if not pool:
                legacy_file = current_step.get("audio_feedback_file")
                if legacy_file:
                    pool = [legacy_file]
            
            for p in pool:
                pool_list.insert(tk.END, p)
            
            # Map mode string if needed (simple for now)
            if existing_mode in modes:
                mode_var.set(existing_mode)
        
        def on_save():
            act = sel_action.get()
            try: d = int(delay_var.get())
            except: d = 100
            
            step_data = {"action": act, "delay": d}
            
            # Save Sound Pool
            pool_items = list(pool_list.get(0, tk.END))
            if pool_items:
                step_data["audio_pool"] = pool_items
                step_data["playback_mode"] = mode_var.get()
                # For backward compatibility / display summary, set legacy field to first item or "Mixture"
                step_data["audio_feedback_file"] = pool_items[0] if len(pool_items) == 1 else "(Sound Pool)"
            else:
                # Clear
                step_data["audio_feedback_file"] = ""

            
            if act == "-- Custom Action --":
                init_name = ""
                init_key = ""
                if mode == "edit" and current_step and "key" in current_step:
                     init_name = current_step['action']
                     init_key = current_step['key']
                
                custom_name = simpledialog.askstring("Custom Action", "Enter a Name for this action (e.g. 'Toggle TrackIR'):", parent=dialog, initialvalue=init_name)
                if custom_name is None: return # Cancelled
                
                custom_key = simpledialog.askstring("Custom Action", "Enter the Key to press (leave empty for Audio Only):", parent=dialog, initialvalue=init_key)
                if custom_key is None: return # Cancelled
                
                custom_key = custom_key.strip()
                custom_name = custom_name.strip()
                
                # Validation: Must have either Key OR Audio
                if not custom_key and not pool_items:
                     messagebox.showwarning("Invalid Step", "Please specify either a Key or Audio files.", parent=dialog)
                     return

                if not custom_name:
                    if not custom_key and pool_items:
                        custom_name = "Audio Feedback"
                    else:
                        messagebox.showwarning("Invalid Name", "Please enter a name for this action.", parent=dialog)
                        return

                step_data["action"] = custom_name
                step_data["key"] = custom_key
            elif act in custom_cache:
                step_data["action"] = act
                step_data["key"] = custom_cache[act]
            
            if mode == "add": profile.macros[macro_name]["steps"].append(step_data)
            else: profile.macros[macro_name]["steps"][edit_idx] = step_data
            profile.save_macros()
            self.on_macro_select(None)
            dialog.destroy()
            
        btn_text = _("Add Step") if mode == "add" else "Save Changes"
        ttk.Button(dialog, text=btn_text, command=on_save).pack(pady=20)

    def remove_macro_step(self):
        profile = self.get_active_profile()
        if not profile: return
        macro_sel = self.macro_tree.selection()
        if not macro_sel: return
        name = macro_sel[0]
        step_sel = self.step_tree.selection()
        if not step_sel: return
        idx = self.step_tree.index(step_sel[0])
        del profile.macros[name]["steps"][idx]
        profile.save_macros()
        self.on_macro_select(None)

    def move_step_up(self): self._move_step(-1)
    def move_step_down(self): self._move_step(1)
        
    def _move_step(self, direction):
        profile = self.get_active_profile()
        if not profile: return
        macro_sel = self.macro_tree.selection()
        if not macro_sel: return
        name = macro_sel[0]
        step_sel = self.step_tree.selection()
        if not step_sel: return
        idx = self.step_tree.index(step_sel[0])
        steps = profile.macros[name]["steps"]
        new_idx = idx + direction
        if 0 <= new_idx < len(steps):
             steps[idx], steps[new_idx] = steps[new_idx], steps[idx]
             profile.save_macros()
             self.on_macro_select(None)
             new_item = self.step_tree.get_children()[new_idx]
             self.step_tree.selection_set(new_item)

    def test_macro(self):
        profile = self.get_active_profile()
        if not profile: return
        selected = self.macro_tree.selection()
        if not selected: return
        name = selected[0]
        if not name: return
        print(f"Testing macro: {name}")
        ic = InputController()
        if not ic.available:
            messagebox.showwarning(_("Input Error"), _("ydotool is not available. Cannot execute macro."))
            return
        def run_thread():
            try:
                success = profile.execute_macro(name, ic)
                if not success:
                    self.root.after(0, lambda: messagebox.showerror(_("Error"), _("Macro execution failed (see console).")))
            except Exception as e:
                print(f"Macro Execution Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Macro error: {e}"))
        threading.Thread(target=run_thread, daemon=True).start()

    def toggle_audio_path_state(self):
        """Enable/disable audio directory controls based on consent."""
        consented = self.consent_var.get()
        
        if consented:
            # Enable directory controls
            self.audio_entry.config(state="normal")
            self.browse_audio_btn.config(state="normal")
            # If path exists, scan it
            if self.audio_dir_var.get():
                 self.scan_audio_files()
        else:
            # Disable controls AND clear the directory path
            self.audio_entry.config(state="disabled")
            self.browse_audio_btn.config(state="disabled")
            self.audio_dir_var.set("")  # Clear the path when unchecked
            self.scan_audio_files() # Scan after clearing, which will effectively clear the audio_files list

    def browse_audio_dir(self):
        path = filedialog.askdirectory(title="Select Audio Assets Directory")
        if path:
            self.audio_dir_var.set(path)
            self.config.set("CUSTOM_AUDIO_DIR", path)
            self.config.save()
            self.scan_audio_files()

    def scan_audio_files(self):
        """Scans the configured directory for audio files."""
        path = self.audio_dir_var.get()
        self.audio_files = [] # For Combobox
        if not path or not os.path.exists(path): return
        
        valid_exts = {".wav", ".ogg", ".flac", ".mp3"} # simpleaudio works best with wav, soundfile handles others
        try:
             files = [f for f in os.listdir(path) if os.path.splitext(f)[1].lower() in valid_exts]
             self.audio_files = sorted(files)
             print(f"Scanned {len(self.audio_files)} audio files.")
        except Exception as e:
             print(f"Audio Scan Error: {e}")

    def show_bindings_context_menu(self, event):
        item = self.game_tree.identify_row(event.y)
        if item:
            self.game_tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="✏️ Edit Voice Command", command=self.edit_voice_command)
            menu.add_command(label="🎹 Edit Mapped Key", command=self.edit_key_binding_command)
            menu.add_command(label="❌ Remove Voice Command", command=self.delete_trigger_command)
            menu.add_separator()
            menu.add_command(label="➕ Add New Command...", command=self.add_voice_command)
            menu.add_command(label="➕ Add New Command...", command=self.add_voice_command)
            # Use tk_popup for better behavior (closes on click outside)
            menu.tk_popup(event.x_root, event.y_root)

    def edit_voice_command(self):
        """Allows editing the voice triggers for a selected action."""
        profile = self.get_active_profile()
        if not profile: return
        
        selected = self.game_tree.selection()
        if not selected: return
        
        item = self.game_tree.item(selected[0])
        action = item['values'][1] # Action Name
        current_triggers = item['values'][0] # "trigger1, trigger2"
        
        new_triggers = simpledialog.askstring("Edit Voice Command", f"Edit triggers for '{action}':", initialvalue=current_triggers, parent=self.root)
        
        if new_triggers is not None: # Check for cancellation (None) vs empty string
             triggers_list = [t.strip().lower() for t in new_triggers.split(",") if t.strip()]
             if not triggers_list:
                 # If emptied, remove? Or just warn?
                 if messagebox.askyesno(_("Confirm"), _("Remove all voice triggers for this action?")):
                     if action in profile.action_voice_map:
                         del profile.action_voice_map[action]
                 else:
                     return
             else:
                 profile.action_voice_map[action] = triggers_list
                 
             profile.save_commands()
             self.refresh_game_bindings()

    def build_custom_commands_section(self):
        """Builds the Custom Commands section in Bindings tab"""
        # Separator
        ttk.Separator(self.bindings_tab, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # LabelFrame
        frame = ttk.LabelFrame(self.bindings_tab, text="➕ Custom Commands (voice → single key)", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview
        cols = ("triggers", "desc", "key")
        self.custom_tree = ttk.Treeview(frame, columns=cols, show="headings", height=6)
        
        self.custom_tree.heading("triggers", text="Voice Triggers")
        self.custom_tree.heading("desc", text="Description")
        self.custom_tree.heading("key", text="Mapped Key")
        
        self.custom_tree.column("triggers", width=200)
        self.custom_tree.column("desc", width=200)
        self.custom_tree.column("key", width=100)
        
        # Scrollbar
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.custom_tree.yview)
        self.custom_tree.configure(yscrollcommand=scroll.set)
        
        self.custom_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Add Custom", width=15, command=self.add_custom_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", width=10, command=self.edit_custom_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", width=10, command=self.delete_custom_command).pack(side=tk.LEFT, padx=5)
        
        # Context Menu
        self.custom_tree.bind("<Button-3>", self.show_custom_context_menu)

    def load_custom_commands(self):
        """Loads custom commands into tree widget"""
        if not hasattr(self, 'custom_tree'): return
            
        profile = self.get_active_profile()
        if not profile: return
        
        # Clear tree
        for item in self.custom_tree.get_children():
            self.custom_tree.delete(item)
        
        # Populate from profile.custom_commands (if exists)
        if hasattr(profile, 'custom_commands'):
            for cmd_id, cmd_data in profile.custom_commands.items():
                if cmd_data.get('enabled', True):
                    triggers = ', '.join(cmd_data['triggers'])
                    key_display = self._format_key_display(
                        cmd_data['key'],
                        cmd_data.get('modifiers', [])
                    )
                    
                    # Store ID in tags
                    self.custom_tree.insert(
                        "", tk.END,
                        values=(triggers, cmd_data.get('name', cmd_id), key_display),
                        tags=(cmd_id,)
                    )

    def _format_key_display(self, key, modifiers):
        """Formats key + modifiers for display"""
        parts = []
        # Title case modifiers
        parts.extend([m.title() for m in modifiers])
        parts.append(key)
        return ' + '.join(parts)

    def add_custom_command(self):
        """Opens dialog to add custom command"""
        profile = self.get_active_profile()
        if not profile: return
        
        AddCustomCommandDialog(
            parent=self.games_tab, # Using root tab as parent
            profile=profile,
            callback=self.on_custom_command_added
        )

    def edit_custom_command(self):
        """Edits selected custom command"""
        profile = self.get_active_profile()
        if not profile: return
        
        selected = self.custom_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a custom command to edit")
            return
            
        # Get ID from tags
        item = self.custom_tree.item(selected[0])
        tags = item.get('tags', [])
        if not tags: return
        cmd_id = tags[0]
        
        if hasattr(profile, 'custom_commands') and cmd_id in profile.custom_commands:
            cmd_data = profile.custom_commands[cmd_id]
            AddCustomCommandDialog(
                parent=self.games_tab,
                profile=profile,
                callback=self.on_custom_command_added,
                existing_cmd=cmd_data
            )

    def delete_custom_command(self):
        """Deletes selected custom command"""
        profile = self.get_active_profile()
        if not profile: return
        
        selected = self.custom_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a custom command to delete")
            return
            
        item = self.custom_tree.item(selected[0])
        tags = item.get('tags', [])
        if not tags: return
        cmd_id = tags[0]
        
        name = item['values'][1]
        
        if messagebox.askyesno(
            "Delete Custom Command",
            f"Are you sure you want to delete '{name}'?"
        ):
            if hasattr(profile, 'custom_commands') and cmd_id in profile.custom_commands:
                del profile.custom_commands[cmd_id]
                self.gm.save_profiles()
                self.load_custom_commands()

    def on_custom_command_added(self, cmd_data):
        """Called when custom command added/edited"""
        profile = self.get_active_profile()
        if not profile: return
        
        # Initialize dict if missing
        if not hasattr(profile, 'custom_commands'):
            profile.custom_commands = {}
            
        # Add/Update
        cmd_id = cmd_data['id']
        profile.custom_commands[cmd_id] = cmd_data
        
        # Save
        self.gm.save_profiles()
        
        # Refresh UI
        self.load_custom_commands()
        
    def show_custom_context_menu(self, event):
        item = self.custom_tree.identify_row(event.y)
        if item:
            self.custom_tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="✏️ Edit", command=self.edit_custom_command)
            menu.add_command(label="❌ Delete", command=self.delete_custom_command)
            menu.tk_popup(event.x_root, event.y_root)
