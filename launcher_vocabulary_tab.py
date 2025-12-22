import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pathlib
import os
from i18n import _

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources # Fallback for older python

class LauncherVocabularyTab:
    """
    Mixin class for providing Custom Vocabulary management.
    """
    
    def build_vocabulary_tab(self):
        """Builds the Vocabulary Management tab."""
        # Main Frame
        vocab_frame = ttk.Frame(self.vocabulary_tab, padding="15")
        vocab_frame.pack(fill=tk.BOTH, expand=True)
        
        # Explanation
        info_frame = ttk.LabelFrame(vocab_frame, text=_("Info"), padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="Add specific game terms here (e.g., 'Frame Shift', 'Limpets').", wraplength=400).pack(anchor=tk.W)
        ttk.Label(info_frame, text=_("When populated, the Assistant will ONLY listen for these words + unknown sounds."), foreground="gray", wraplength=400).pack(anchor=tk.W)
        
        # Import Section
        import_frame = ttk.LabelFrame(vocab_frame, text=_("Import Game Vocabulary"), padding="10")
        import_frame.pack(fill=tk.X, pady=(0, 10))
        
        hbox = ttk.Frame(import_frame)
        hbox.pack(fill=tk.X)
        
        ttk.Label(hbox, text=_("Select Game:")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.game_vocab_var = tk.StringVar()
        self.game_vocab_combo = ttk.Combobox(hbox, textvariable=self.game_vocab_var, state="readonly", width=25)
        self.game_vocab_combo.pack(side=tk.LEFT, padx=5)
        
        # Refresh Button
        ttk.Button(hbox, text=_("↻"), width=3, command=self.populate_game_dropdown).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(hbox, text=_("Import Selected"), command=self.import_selected_game).pack(side=tk.LEFT, padx=5)
        
        # Path Hint
        user_path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "vocabulary"
        path_lbl = ttk.Label(hbox, text=f"(Look in: {user_path})", foreground="gray", font=("TkDefaultFont", 8))
        path_lbl.pack(side=tk.LEFT, padx=10)
        
        # Populate games
        self.populate_game_dropdown()
        
        # Management Area
        manage_frame = ttk.Frame(vocab_frame)
        manage_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left: Listbox
        list_frame = ttk.Frame(manage_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text=_("Current Vocabulary:")).pack(anchor=tk.W)
        
        self.vocab_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, height=15)
        self.vocab_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.vocab_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.vocab_listbox.config(yscrollcommand=scrollbar.set)
        
        # Right: Buttons
        btn_frame = ttk.Frame(manage_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Label(btn_frame, text=_("New Term:")).pack(anchor=tk.W)
        self.new_term_var = tk.StringVar()
        self.term_entry = ttk.Entry(btn_frame, textvariable=self.new_term_var, width=20)
        self.term_entry.pack(pady=(0, 5))
        self.term_entry.bind('<Return>', lambda e: self.add_term())
        
        ttk.Button(btn_frame, text=_("Add Term"), command=self.add_term).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text=_("Delete Selected"), command=self.delete_term).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text=_("Clear All"), command=self.clear_vocab).pack(fill=tk.X, pady=(20, 2))
        
        # Load initial data
        self.refresh_vocab_list()

    def refresh_vocab_list(self):
        self.vocab_listbox.delete(0, tk.END)
        current_vocab = self.config.get("CUSTOM_VOCABULARY", [])
        if not isinstance(current_vocab, list):
            current_vocab = []
        
        for term in sorted(current_vocab):
            self.vocab_listbox.insert(tk.END, term)

    def add_term(self):
        term = self.new_term_var.get().strip()
        if not term: return
        
        current_vocab = self.config.get("CUSTOM_VOCABULARY", [])
        if not isinstance(current_vocab, list): current_vocab = []
        
        # Check duplicate (case-insensitive?) - preserving case for display, but checking lower
        if any(t.lower() == term.lower() for t in current_vocab):
            messagebox.showwarning("Duplicate", f"'{term}' is already in the list.")
            return

        current_vocab.append(term)
        self.config.set("CUSTOM_VOCABULARY", current_vocab)
        self.config.save() # Auto-save
        
        self.new_term_var.set("")
        self.refresh_vocab_list()
        self.term_entry.focus()

    def delete_term(self):
        selection = self.vocab_listbox.curselection()
        if not selection: return
        
        term = self.vocab_listbox.get(selection[0])
        current_vocab = self.config.get("CUSTOM_VOCABULARY", [])
        
        if term in current_vocab:
            current_vocab.remove(term)
            self.config.set("CUSTOM_VOCABULARY", current_vocab)
            self.config.save() # Auto-save
            self.refresh_vocab_list()

    def clear_vocab(self):
        if messagebox.askyesno(_("Confirm Clear"), _("Are you sure you want to clear the entire vocabulary list?")):
            self.config.set("CUSTOM_VOCABULARY", [])
            self.config.save() # Auto-save
            self.refresh_vocab_list()

    def populate_game_dropdown(self):
        """Scans for vocabulary .txt files."""
        self.vocab_files = {} # Name -> Path
        
        candidates = []
        
        # 1. User Data Path (Preferred for editability)
        user_path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "vocabulary"
        try:
            user_path.mkdir(parents=True, exist_ok=True)
            candidates.append(user_path)
            # Update UI info if possible, but simpler to just search it
        except: pass
        
        # 2. Local dev path
        dev_path = pathlib.Path(__file__).parent / "data" / "vocabulary"
        if dev_path.exists():
            candidates.append(dev_path)
            
        # 3. Installed Package path
        site_path = pathlib.Path(__file__).parent / "tuxtalks" / "data" / "vocabulary"
        if site_path.exists():
            candidates.append(site_path)
            
        # 4. CWD
        cwd_path = pathlib.Path("data/vocabulary")
        if cwd_path.exists():
            candidates.append(cwd_path)
            
        found_games = []
        
        for p in candidates:
            if not p.exists(): continue
            for f in p.glob("*.txt"):
                name = f.stem.replace("_", " ").title()
                # User path overrides others if same name
                if name not in self.vocab_files: 
                    self.vocab_files[name] = f
                
                if name not in found_games:
                    found_games.append(name)
                    
        self.game_vocab_combo['values'] = sorted(found_games)
        if found_games:
            self.game_vocab_combo.current(0)

    def import_selected_game(self):
        name = self.game_vocab_var.get()
        if not name or name not in self.vocab_files:
            return
            
        path = self.vocab_files[name]
        try:
            with open(path, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
                
            current_vocab = self.config.get("CUSTOM_VOCABULARY", [])
            if not isinstance(current_vocab, list): current_vocab = []
            
            added_count = 0
            for term in lines:
                # Case-insensitive duplicate check
                if not any(t.lower() == term.lower() for t in current_vocab):
                    current_vocab.append(term)
                    added_count += 1
                    
            if added_count > 0:
                self.config.set("CUSTOM_VOCABULARY", current_vocab)
                self.config.save() # Auto-save
                self.refresh_vocab_list()
                messagebox.showinfo("Import Successful", f"Imported {added_count} new terms from {name}.\n(Configuration Saved)")
            else:
                messagebox.showinfo(_("Import Info"), _("All terms from this file are already in your vocabulary."))
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to read file: {e}")
