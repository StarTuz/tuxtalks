# Custom Commands - Detailed Design Specification
## Feature Design for Implementation

**Date:** December 12, 2025  
**Version:** 1.0  
**Status:** ✅ **COMPLETE** - Implementation finished (2025-12-13)  
**Prerequisites:** Phase 1 bugs must be fixed first

---

## 🎯 Feature Overview

### **Problem Statement:**

Users need to add voice commands for keys that aren't in the game's binding file.

**Example Scenarios:**
- Universal keys: `F12` (screenshot), `Escape` (menu), `PrintScreen`
- Custom hotkeys: User bound `F10` to something outside game's control
- Overlay keys: Discord overlay (`Shift+Tab`), Steam overlay

**Current Limitation:**
- Bindings tab only shows what's in game's XML
- Macros tab requires creating a "sequence" for single key

**Solution:**
Add "Custom Commands" section to Bindings tab for user-defined single-key commands.

---

## 🎨 UI Design

### **Bindings Tab Layout (NEW):**

```
┌───────────────────────────────────────────────────────────┐
│ Bindings Tab                                     │
├───────────────────────────────────────────────────────────┤
│                                                           │
│ 📋 Game Bindings (from inputmap.xml)                     │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ Voice Command     │ Game Action   │ Mapped Key     ┃ │
│ ┣━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━┫ │
│ ┃ match speed       │ Match Speed   │ Shift+x        ┃ │
│ ┃ boost             │ Boost Engines │ Tab            ┃ │
│ ┃ travel mode       │ Travel Mode   │ Shift+1        ┃ │
│ ┃ scan mode         │ Scan Mode     │ Shift+1        ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━┛ │
│ [Modify Trigger] [Clear Trigger]                         │
│                                                           │
│─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│                                                           │
│ ➕ Custom Commands (voice → single key)                   │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ Voice Command     │ Description   │ Key            ┃ │
│ ┣━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━┫ │
│ ┃ screenshot        │ Take Photo    │ F12            ┃ │
│ ┃ toggle menu       │ Show/Hide     │ Escape         ┃ │
│ ┃ overlay           │ Show Overlay  │ Shift+Tab      ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━┛ │
│ [Add Custom] [Edit] [Delete]                             │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### **Visual Hierarchy:**

| Section | Height | Expandable |
|---------|--------|------------|
| **Game Bindings** | 60% of tab | Scrollable |
| **Separator** | Thin line | - |
| **Custom Commands** | 40% of tab | Scrollable |

### **Color Coding:**

| Item Type | Text Color | Icon |
|-----------|----------|------|
| Game Binding | White/Default | 🎮 |
| Custom Command | Green (#4CAF50) | ➕ |
| Multi-step Macro | Blue (#2196F3) | 🔧 |

---

## 📊 Data Schema

### **Profile Class Extension:**

```python
class GameProfile:
    # EXISTING FIELDS:
    name: str
    group: str
    action_voice_map: dict  # Game bindings from XML
    macros: dict            # Multi-step sequences
    bindings: dict          # Parsed from game file
    
    # NEW FIELD:
    custom_commands: dict = {}
```

### **Custom Commands Structure:**

```python
custom_commands = {
    "screenshot": {
        "id": "screenshot",  # Unique identifier
        "name": "Screenshot",  # Display name
        "description": "Take a screenshot",  # User-friendly description
        "triggers": ["screenshot", "take screenshot", "photo"],  # Voice phrases
        "key": "F12",  # Primary key
        "modifiers": [],  # ["ctrl", "shift", "alt"]
        "created": "2025-12-12T23:00:00Z",  # Timestamp
        "enabled": True  # Can be disabled without deleting
    },
    "toggle_menu": {
        "id": "toggle_menu",
        "name": "Toggle Menu",
        "description": "Show/hide game menu",
        "triggers": ["toggle menu", "show menu", "menu"],
        "key": "Escape",
        "modifiers": [],
        "created": "2025-12-12T23:05:00Z",
        "enabled": True
    },
    "discord_overlay": {
        "id": "discord_overlay",
        "name": "Discord Overlay",
        "description": "Show Discord",
        "triggers": ["overlay", "discord", "show discord"],
        "key": "Tab",
        "modifiers": ["shift"],
        "created": "2025-12-12T23:10:00Z",
        "enabled": True
    }
}
```

### **Validation Rules:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | str | Yes | Unique, lowercase, no spaces |
| `name` | str | Yes | 1-50 chars, display name |
| `description` | str | No | 0-200 chars |
| `triggers` | list[str] | Yes | 1+ items, each 1-100 chars |
| `key` | str | Yes | Valid key name (e.g., "F12", "Escape") |
| `modifiers` | list[str] | No | 0-3 items: "ctrl", "shift", "alt" |
| `enabled` | bool | Yes | Default True |

---

## 🖼️ Dialog Design

### **Add Custom Command Dialog:**

```
┌─────────────────────────────────────────────────────┐
│ ➕ Add Custom Command                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Name:                                               │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Screenshot                                      │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ Description (optional):                             │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Takes a screenshot using F12                    │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ Voice Triggers (comma separated):                   │
│ ┌─────────────────────────────────────────────────┐ │
│ │ screenshot, take screenshot, photo              │ │
│ └─────────────────────────────────────────────────┘ │
│  💡 Say any of these phrases to trigger           │
│                                                     │
│ Key to Press:                                       │
│ ┌─────────────────────┐                            │
│ │ F12                 │ [Capture]                  │
│ └─────────────────────┘                            │
│  Press [Capture] then press the key you want       │
│                                                     │
│ Modifiers:                                          │
│ ☐ Ctrl    ☐ Shift    ☐ Alt                         │
│                                                     │
│        [Add Command]  [Cancel]                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### **Field Details:**

**Name Field:**
- Auto-filled with first voice trigger (capitalized)
- Editable
- Max 50 chars

**Description Field:**
- Optional
- Placeholder: "What does this command do?"
- Max 200 chars

**Voice Triggers:**
- Comma-separated list
- Trimmed, lowercased on save
- Minimum 1 trigger
- Duplicate detection

**Key Capture:**
- Button opens capture mode
- Listens for single keypress
- Shows pressed key in field
- ESC cancels capture

**Modifiers:**
- Checkboxes for Ctrl/Shift/Alt
- Multiple can be selected
- Combined with main key

---

## 🔧 Implementation Details

### **New Methods to Add:**

```python
class LauncherGamesTab:
    
    # ─────────────────────────────────────
    # UI Building
    # ─────────────────────────────────────
    
    def build_custom_commands_section(self):
        """Builds the Custom Commands section in Bindings tab"""
        # Creates LabelFrame
        # Adds Treeview
        # Adds button row
        # Binds events
        pass
    
    # ─────────────────────────────────────
    # Data Loading
    # ─────────────────────────────────────
    
    def load_custom_commands(self):
        """Loads custom commands into tree widget"""
        profile = self.get_active_profile()
        if not profile:
            return
        
        # Clear tree
        for item in self.custom_tree.get_children():
            self.custom_tree.delete(item)
        
        # Populate from profile.custom_commands
        for cmd_id, cmd_data in profile.custom_commands.items():
            if cmd_data.get('enabled', True):
                triggers = ', '.join(cmd_data['triggers'])
                key_display = self._format_key_display(
                    cmd_data['key'],
                    cmd_data.get('modifiers', [])
                )
                self.custom_tree.insert(
                    "", tk.END,
                    values=(triggers, cmd_data['name'], key_display),
                    tags=('custom',)
                )
    
    def _format_key_display(self, key, modifiers):
        """Formats key + modifiers for display"""
        parts = []
        if 'ctrl' in modifiers:
            parts.append('Ctrl')
        if 'shift' in modifiers:
            parts.append('Shift')
        if 'alt' in modifiers:
            parts.append('Alt')
        parts.append(key)
        return ' + '.join(parts)
    
    # ─────────────────────────────────────
    # Dialog Handlers
    # ─────────────────────────────────────
    
    def add_custom_command(self):
        """Opens dialog to add custom command"""
        AddCustomCommandDialog(
            parent=self.games_tab,
            profile=self.get_active_profile(),
            callback=self.on_custom_command_added
        )
    
    def edit_custom_command(self):
        """Edits selected custom command"""
        selected = self.custom_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a custom command to edit")
            return
        
        # Get command ID from selection
        # Open EditCustomCommandDialog
        # Pass existing data
        pass
    
    def delete_custom_command(self):
        """Deletes selected custom command"""
        selected = self.custom_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a custom command to delete")
            return
        
        if messagebox.askyesno(
            "Delete Custom Command",
            "Are you sure you want to delete this custom command?"
        ):
            # Get command ID
            # Remove from profile.custom_commands
            # Save profile
            # Refresh UI
            pass
    
    # ─────────────────────────────────────
    # Callbacks
    # ─────────────────────────────────────
    
    def on_custom_command_added(self, cmd_data):
        """Called when custom command added/edited"""
        profile = self.get_active_profile()
        if not profile:
            return
        
        # Add to profile.custom_commands
        cmd_id = cmd_data['id']
        profile.custom_commands[cmd_id] = cmd_data
        
        # Save
        self.gm.save_profiles()
        
        # Refresh UI
        self.load_custom_commands()
```

### **Dialog Class:**

```python
class AddCustomCommandDialog(tk.Toplevel):
    """Dialog for adding/editing custom commands"""
    
    def __init__(self, parent, profile, callback, existing_cmd=None):
        super().__init__(parent)
        
        self.profile = profile
        self.callback = callback
        self.existing_cmd = existing_cmd
        self.captured_key = None
        
        self.title("➕ Add Custom Command" if not existing_cmd 
                   else f"✏ Edit {existing_cmd['name']}")
        self.geometry("500x450")
        
        self.build_ui()
        
        # Pre-fill if editing
        if existing_cmd:
            self.load_existing_data()
    
    def build_ui(self):
        """Builds dialog UI"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(main_frame, text="Name:").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var).pack(
            fill=tk.X, pady=(0,10)
        )
        
        # Description
        ttk.Label(main_frame, text="Description (optional):").pack(anchor=tk.W)
        self.desc_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.desc_var).pack(
            fill=tk.X, pady=(0,10)
        )
        
        # Voice Triggers
        ttk.Label(main_frame, text="Voice Triggers (comma separated):").pack(anchor=tk.W)
        self.triggers_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.triggers_var).pack(
            fill=tk.X, pady=(0,5)
        )
        ttk.Label(
            main_frame,
            text="💡 Say any of these phrases to trigger",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(0,10))
        
        # Key Capture
        ttk.Label(main_frame, text="Key to Press:").pack(anchor=tk.W)
        key_frame = ttk.Frame(main_frame)
        key_frame.pack(fill=tk.X, pady=(0,5))
        
        self.key_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.key_var, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(key_frame, text="Capture", command=self.capture_key).pack(
            side=tk.LEFT, padx=(5,0)
        )
        
        ttk.Label(
            main_frame,
            text="Press [Capture] then press the key you want",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(0,10))
        
        # Modifiers
        ttk.Label(main_frame, text="Modifiers:").pack(anchor=tk.W)
        mod_frame = ttk.Frame(main_frame)
        mod_frame.pack(fill=tk.X, pady=(0,10))
        
        self.ctrl_var = tk.BooleanVar()
        self.shift_var = tk.BooleanVar()
        self.alt_var = tk.BooleanVar()
        
        ttk.Checkbutton(mod_frame, text="Ctrl", variable=self.ctrl_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(mod_frame, text="Shift", variable=self.shift_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(mod_frame, text="Alt", variable=self.alt_var).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="Add Command" if not self.existing_cmd else "Save Changes",
            command=self.save_command
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def capture_key(self):
        """Captures a key press"""
        CaptureKeyDialog(self, callback=self.on_key_captured)
    
    def on_key_captured(self, key):
        """Called when key captured"""
        self.captured_key = key
        self.key_var.set(key)
    
    def save_command(self):
        """Validates and saves command"""
        # Validation
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
            messagebox.showerror("Error", "Key is required. Click [Capture] to set a key.")
            return
        
        # Parse triggers
        triggers = [t.strip().lower() for t in triggers_str.split(',') if t.strip()]
        
        # Build modifiers list
        modifiers = []
        if self.ctrl_var.get():
            modifiers.append('ctrl')
        if self.shift_var.get():
            modifiers.append('shift')
        if self.alt_var.get():
            modifiers.append('alt')
        
        # Generate ID
        cmd_id = name.lower().replace(' ', '_')
        if self.existing_cmd:
            cmd_id = self.existing_cmd['id']
        
        # Build command data
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
        
        # Callback
        self.callback(cmd_data)
        self.destroy()
```

### **Key Capture Dialog:**

```python
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
    
    def on_key_press(self, event):
        """Captures the key"""
        key = event.keysym
        
        # Ignore modifiers alone
        if key in ['Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R']:
            return
        
        # Return key
        self.callback(key)
        self.destroy()
```

---

## 🔄 Integration Points

### **1. Voice Recognition Integration**

**File:** `core/command_processor.py` (or wherever voice routing happens)

**New Logic:**

```python
def process_voice_command(recognized_text):
    profile = gm.get_active_profile()
    
    # Priority 1: Custom Commands
    for cmd_id, cmd_data in profile.custom_commands.items():
        if cmd_data.get('enabled', True):
            for trigger in cmd_data['triggers']:
                if trigger in recognized_text.lower():
                    execute_custom_command(cmd_data)
                    return True
    
    # Priority 2: Game Bindings
    for action, triggers in profile.action_voice_map.items():
        for trigger in triggers:
            if trigger in recognized_text.lower():
                execute_game_binding(action)
                return True
    
    # Priority 3: Macros
    for macro_name, macro_data in profile.macros.items():
        for trigger in macro_data['triggers']:
            if trigger in recognized_text.lower():
                execute_macro(macro_data)
                return True
    
    # No match found
    return False

def execute_custom_command(cmd_data):
    """Executes a custom command"""
    key = cmd_data['key']
    modifiers = cmd_data.get('modifiers', [])
    
    # Use input controller to press key
    input_controller.press_key(key, modifiers)
```

**Priority Rationale:**
1. **Custom Commands first** - User explicitly created these
2. **Game Bindings second** - Authoritative from game file
3. **Macros last** - More complex, broader matching

---

### **2. Input Controller Integration**

**File:** `input_controller.py`

**Verify Method Exists:**

```python
def press_key(self, key, modifiers=[]):
    """
    Presses a key with optional modifiers
    
    Args:
        key: Key name (e.g., "F12", "Escape", "a")
        modifiers: List of modifiers ["ctrl", "shift", "alt"]
    """
    # Implementation should already exist
    pass
```

**If not exists, add it:**
- Convert key name to key code
- Press modifiers (if any)
- Press main key
- Release main key
- Release modifiers

---

### **3. Profile Save/Load Integration**

**File:** `game_manager.py` (or wherever profiles are saved)

**Add to Profile Class:**

```python
class GameProfile:
    def __init__(self, ...):
        # ... existing fields ...
        self.custom_commands = {}
    
    def save(self):
        """Saves profile to JSON"""
        data = {
            'name': self.name,
            'group': self.group,
            # ... existing fields ...
            'custom_commands': self.custom_commands  # ADD THIS
        }
        # ... save logic ...
    
    def load(self, data):
        """Loads profile from JSON"""
        self.name = data['name']
        self.group = data['group']
        # ... existing fields ...
        self.custom_commands = data.get('custom_commands', {})  # ADD THIS
```

---

## 🧪 Testing Strategy

### **Unit Tests:**

```python
def test_custom_command_creation():
    """Test creating a custom command"""
    cmd_data = {
        'id': 'test_cmd',
        'name': 'Test Command',
        'description': 'Test',
        'triggers': ['test', 'trigger'],
        'key': 'F12',
        'modifiers': [],
        'enabled': True
    }
    
    profile = GameProfile()
    profile.custom_commands['test_cmd'] = cmd_data
    
    assert 'test_cmd' in profile.custom_commands
    assert profile.custom_commands['test_cmd']['key'] == 'F12'

def test_custom_command_execution():
    """Test executing a custom command"""
    cmd_data = {
        'key': 'F12',
        'modifiers': ['ctrl']
    }
    
    # Mock input controller
    input_controller = Mock()
    execute_custom_command(cmd_data)
    
    input_controller.press_key.assert_called_with('F12', ['ctrl'])

def test_voice_trigger_matching():
    """Test voice trigger matching"""
    cmd_data = {
        'triggers': ['screenshot', 'take photo', 'capture']
    }
    
    assert matches_command("take a screenshot", cmd_data) == True
    assert matches_command("show menu", cmd_data) == False
```

### **Integration Tests:**

```python
def test_end_to_end_custom_command():
    """Full workflow test"""
    # 1. Create custom command via UI
    # 2. Save profile
    # 3. Reload profile
    # 4. Verify command exists
    # 5. Trigger via voice
    # 6. Verify key pressed
    pass
```

### **Manual Tests:**

1. **Add Custom Command**
   - Open dialog
   - Fill all fields
   - Capture key
   - Save
   - Verify appears in tree

2. **Trigger via Voice**
   - Say trigger phrase
   - Verify key pressed in game
   - Check game responds

3. **Edit Custom Command**
   - Select existing
   - Edit triggers
   - Save
   - Verify updated

4. **Delete Custom Command**
   - Select custom command
   - Click Delete
   - Confirm
   - Verify removed

---

## 📝 UI Text & Messages

### **Labels:**

| Element | Text |
|---------|------|
| Section Header | "➕ Custom Commands (voice → single key)" |
| Add Button | "Add Custom" |
| Edit Button | "Edit" |
| Delete Button | "Delete" |
| Dialog Title (Add) | "➕ Add Custom Command" |
| Dialog Title (Edit) | "✏ Edit {name}" |
| Save Button | "Add Command" / "Save Changes" |

### **Help Text:**

| Location | Text |
|----------|------|
| Section Note | "For keys not in game's binding file (e.g., F12 screenshot, Escape menu)" |
| Triggers Field | "💡 Say any of these phrases to trigger" |
| Key Capture | "Press [Capture] then press the key you want" |

### **Error Messages:**

| Scenario | Message |
|----------|---------|
| No name | "Name is required" |
| No triggers | "At least one voice trigger is required" |
| No key | "Key is required. Click [Capture] to set a key." |
| Duplicate trigger | "Trigger '{trigger}' already used in another command" |
| No selection (edit) | "Select a custom command to edit" |
| No selection (delete) | "Select a custom command to delete" |

### **Confirmation Dialogs:**

```
Delete:
  Title: "Delete Custom Command"
  Message: "Are you sure you want to delete this custom command?"
  Buttons: [Yes] [No]

Duplicate Trigger Warning:
  Title: "Duplicate Trigger"
  Message: "The trigger '{trigger}' is already used by:
            - Game Binding: {action}
            - Custom Command: {name}
            
            This may cause conflicts. Continue anyway?"
  Buttons: [Yes] [No]
```

---

## 🎨 Polish & UX Enhancements

### **Visual Indicators:**

- **Green text** for custom commands in tree
- **Icon column** showing ➕ for custom, 🎮 for game
- **Hover tooltip** showing full description

### **Keyboard Shortcuts:**

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Add Custom Command |
| `Ctrl+E` | Edit Selected |
| `Delete` | Delete Selected |
| `F5` | Refresh |

### **Context Menu (Right-click):**

```
Right-click on custom command:
  ✏ Edit
  📋 Duplicate
  ❌ Disable
  🗑 Delete
  ─────────
  📤 Export
```

---

## 🚀 Migration Strategy

### **For Users with Single-Step Macros:**

**On First Launch After Update:**

```
┌──────────────────────────────────────────────┐
│ 🔄 Macro Migration Available                 │
├──────────────────────────────────────────────┤
│                                              │
│ We found 3 single-step macros that could    │
│ be converted to Custom Commands:            │
│                                              │
│ ✓ "screenshot" (F12)                         │
│ ✓ "toggle_menu" (Escape)                     │
│ ✓ "overlay" (Shift+Tab)                      │
│                                              │
│ Custom Commands are clearer and easier       │
│ to manage for single-key actions.           │
│                                              │
│ Would you like to migrate these now?         │
│                                              │
│   [Migrate All] [Review Manually] [Skip]    │
│                                              │
└──────────────────────────────────────────────┘
```

**Migration Logic:**

```python
def detect_single_step_macros(profile):
    """Finds macros with only 1 step"""
    candidates = []
    
    for macro_name, macro_data in profile.macros.items():
        if len(macro_data.get('steps', [])) == 1:
            step = macro_data['steps'][0]
            # Check if it's a simple key press
            if 'key' in step:
                candidates.append({
                    'macro_name': macro_name,
                    'triggers': macro_data['triggers'],
                    'key': step['key'],
                    'description': f"Migrated from macro '{macro_name}'"
                })
    
    return candidates

def migrate_macro_to_custom_command(profile, macro_name):
    """Migrates a single-step macro to custom command"""
    macro_data = profile.macros[macro_name]
    step = macro_data['steps'][0]
    
    # Create custom command
    cmd_id = macro_name
    cmd_data = {
        'id': cmd_id,
        'name': macro_name.replace('_', ' ').title(),
        'description': f"Migrated from macro",
        'triggers': macro_data['triggers'],
        'key': step['key'],
        'modifiers': step.get('modifiers', []),
        'enabled': True,
        'created': datetime.datetime.now().isoformat()
    }
    
    # Add to custom commands
    profile.custom_commands[cmd_id] = cmd_data
    
    # Remove from macros
    del profile.macros[macro_name]
    
    # Save
    profile.save()
```

---

## 📚 Documentation Updates

### **README.md:**

Add section:

```markdown
### Custom Commands

In addition to game bindings and macros, you can define custom voice commands for any key:

**Example:**
- Voice: "screenshot"
- Key: F12

Perfect for:
- Universal keys (Escape, F12, PrintScreen)
- Custom hotkeys outside game's control
- Overlay triggers (Discord, Steam)

**To add:**
1. Go to Game tab → Bindings
2. Scroll to "Custom Commands" section
3. Click [Add Custom]
4. Enter name, voice triggers, and capture key
5. Done! Say the trigger phrase to press the key
```

### **Help Tab:**

Add entry:

```
Q: What's the difference between Custom Commands and Macros?
A: Custom Commands are for SINGLE keypresses (e.g., F12 for screenshot).
   Macros are for SEQUENCES of actions (e.g., dock request: Tab → Wait → Enter).
   
   Use Custom Commands when possible - they're simpler and faster.
```

---

## ✅ Acceptance Criteria

### **Must Have:**
- [ ] Can add custom command with voice triggers and key
- [ ] Can edit existing custom command
- [ ] Can delete custom command
- [ ] Voice triggers execute the key press
- [ ] Data persists across restarts
- [ ] Visual distinction from game bindings

### **Should Have:**
- [ ] Migration wizard for single-step macros
- [ ] Duplicate trigger detection
- [ ] Modifier key support (Ctrl/Shift/Alt)
- [ ] Description field for documentation

### **Nice to Have:**
- [ ] Keyboard shortcuts (Ctrl+N, etc.)
- [ ] Context menu (right-click)
- [ ] Export/import custom commands
- [ ] Disable without deleting

---

## 🏁 Implementation Checklist

### **Phase 3 (Custom Commands Implementation):**

#### **3.1: Data Layer**
- [ ] Add `custom_commands` field to Profile class
- [ ] Add save/load methods
- [ ] Add validation
- [ ] Write unit tests

#### **3.2: UI Layer**
- [ ] Add second LabelFrame to Bindings tab
- [ ] Create `custom_tree` Treeview widget
- [ ] Add button row (Add, Edit, Delete)
- [ ] Create `AddCustomCommandDialog` class
- [ ] Create `CaptureKeyDialog` class
- [ ] Add `load_custom_commands()` method
- [ ] Style with green text/icons

#### **3.3: Integration**
- [ ] Update voice routing to check custom commands first
- [ ] Connect to `input_controller.press_key()`
- [ ] Update `refresh_game_bindings()` to load custom commands
- [ ] Add conflict detection (duplicate triggers)

#### **3.4: Migration**
- [ ] Add `detect_single_step_macros()` function
- [ ] Create migration wizard dialog
- [ ] Add "Skip" option with preference save
- [ ] Test migration path

#### **3.5: Testing**
- [ ] Unit tests for data layer
- [ ] Integration tests for voice → key
- [ ] Manual UI testing
- [ ] Migration testing

#### **3.6: Documentation**
- [ ] Update README.md
- [ ] Add Help tab entry
- [ ] Update tooltips
- [ ] Create user guide section

---

**Design Complete!** ✅

**Ready for Implementation After Phase 1 & 2 Complete**

**Estimated Implementation Time:** 4-6 hours
