#!/usr/bin/env python3
"""
Automated script to wrap English UI strings with gettext _() function.
This scans launcher Python files and wraps string literals that appear to be UI text.
"""

import re
import os
import sys

# Patterns to identify UI strings (strings that should be translated)
UI_STRING_PATTERNS = [
    # ttk/tk widget text parameters
    r'(text\s*=\s*)"([^"]+)"',
    r"(text\s*=\s*)'([^']+)'",
    
    # messagebox calls
    r'(messagebox\.\w+\s*\([^,]*,\s*)"([^"]+)"',
    r"(messagebox\.\w+\s*\([^,]*,\s*)'([^']+)'",
    
    # Label/Frame titles
    r'(ttk\.(Label|LabelFrame|Button|Checkbutton)\s*\([^)]*text\s*=\s*)"([^"]+)"',
]

# Strings to NEVER translate (technical terms, code)
SKIP_STRINGS = {
    '', 'UTF-8', 'utf-8', 'None', 'True', 'False',
    'http', 'https', 'ftp', '.py', '.json', '.xml',
    '...', '–', '—', '\n', '\t',
}

def should_translate(text):
    """Determine if a string should be marked for translation."""
    if not text or text in SKIP_STRINGS:
        return False
    if text.startswith('http') or text.startswith('ftp'):
        return False
    if text.endswith('.py') or text.endswith('.json'):
        return False
    # Skip very short technical strings
    if len(text) <= 2 and text.isupper():
        return False
    return True

def wrap_launcher_file(filepath):
    """Add gettext wrapping to a launcher file."""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Add import at top if not present
    if 'from i18n import _' not in content:
        # Find the last import line
        import_lines = []
        for i, line in enumerate(content.split('\n')):
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append(i)
        
        if import_lines:
            lines = content.split('\n')
            insert_pos = max(import_lines) + 1
            lines.insert(insert_pos, 'from i18n import _')
            content = '\n'.join(lines)
    
    # Wrap text= parameters in widget constructors
    def wrap_text_param(match):
        prefix = match.group(1)
        text = match.group(2)
        quote = '"' if '"' in match.group(0) else "'"
        
        if should_translate(text) and not text.startswith('_('):
            return f'{prefix}_({quote}{text}{quote})'
        return match.group(0)
    
    content = re.sub(r'(text\s*=\s*)(["\'])([^"\']+)\2', 
                     lambda m: f'{m.group(1)}_({m.group(2)}{m.group(3)}{m.group(2)})'
                     if should_translate(m.group(3)) else m.group(0),
                     content)
    
    #  Wrap messagebox strings
    content = re.sub(r'(messagebox\.\w+\()(["\'])([^"\']+)\2(\s*,\s*)(["\'])([^"\']+)\5',
                     lambda m: f'{m.group(1)}_({m.group(2)}{m.group(3)}{m.group(2)}){m.group(4)}_({m.group(5)}{m.group(6)}{m.group(5)})'
                     if should_translate(m.group(3)) and should_translate(m.group(6)) else m.group(0),
                     content)
    
    # Only write if changed
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {filepath}")
        return True
    else:
        print(f"  - No changes needed")
        return False

def main():
    """Process all launcher files."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    launcher_files = [
        'launcher.py',
        'launcher_speech_tab.py',
        'launcher_player_tab.py',
        'launcher_games_tab.py',
        'launcher_input_tab.py',
        'launcher_corrections_tab.py',
        'launcher_vocabulary_tab.py',
        'launcher_packs_tab.py',
    ]
    
    updated = 0
    for filename in launcher_files:
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            if wrap_launcher_file(filepath):
                updated += 1
        else:
            print(f"Warning: {filepath} not found")
    
    print(f"\n✓ Processed {len(launcher_files)} files, updated {updated}")
    print("\nNext steps:")
    print("1. Review changes: git diff")
    print("2. Extract strings: pybabel extract -F babel.cfg -o locale/messages.pot .")
    print("3. Update Spanish: pybabel update -i locale/messages.pot -d locale")
    print("4. Translate locale/es/LC_MESSAGES/messages.po")
    print("5. Compile: pybabel compile -d locale")

if __name__ == '__main__':
    main()
