#!/usr/bin/env python3
"""
Welsh (Cymraeg) translation for TuxTalks using gaming-specific glossary.
"""

import re
import os
import sys

# Welsh Gaming Glossary (English -> Welsh)
WELSH_GLOSSARY = {
    # UI Elements
    "Settings": "Gosodiadau",
    "General": "Cyffredinol",
    "Voice": "Llais",
    "Games": "Gemau",
    "Speech Engines": "Peiriannau Llais",
    "Input": "Mewnbwn",
    "Vocabulary": "Geirfa",
    "Help": "Cymorth",
    "Content Packs": "Pecynnau Cynnwys",
    "Corrections": "Cywiriadau",
    "Training": "Hyfforddiant",
    "Player": "Chwaraewr",
    
    # Actions
    "Start Assistant": "Cychwyn Cynorthwyydd",
    "Stop": "Stopio",
    "Exit": "Gadael",
    "Save Config": "Cadw Cyfluniad",
    "Cancel": "Canslo",
    "Browse": "Pori",
    "Add": "Ychwanegu",
    "Edit": "Golygu",
    "Delete": "Dileu",
    "Refresh": "Adnewyddu",
    "Clear": "Clirio",
    "New": "Newydd",
    "Create": "Creu",
    "Remove": "Tynnu",
    "Import": "Mewnforio",
    "Export": "Allforio",
    "Backup": "Copi Wrth Gefn",
    "Restore": "Adfer",
    "Test": "Profi",
    "Run": "Rhedeg",
    "Save": "Cadw",
    "Apply": "Cymhwyso",
    "OK": "Iawn",
    "Yes": "Ie",
    "No": "Na",
    "Close": "Cau",
    "Continue": "Parhau",
    
    # Gaming Terms
    "Bindings": "Rhwymiadau",
    "Binds": "Rhwymiadau",
    "Game Action": "Gweithred Gêm",
    "Voice Command": "Gorchymyn Llais",
    "Mapped Key": "Bysell Fapio",
    "Process Name": "Enw Proses",
    "Binding Profile": "Proffil Rhwymo",
    "Macro": "Macro",
    "Macros": "Macros",
    "Profile": "Proffil",
    "Game Integration": "Integreiddio Gêm",
    "Runtime Status": "Statws Amser Rhedeg",
    "Runtime Environment": "Amgylchedd Amser Rhedeg",
    "Custom Commands": "Gorchmynion Personol",
    "Game Bindings": "Rhwymiadau Gêm",
    "Active Profile Bindings": "Rhwymiadau Proffil Gweithredol",
    
    # Speech/Voice
    "Wake Word": "Gair Deffro",
    "Wake Word Settings": "Gosodiadau Gair Deffro",
    "Speech Recognition": "Adnabod Lleferydd",
    "Speech Recognition (Vosk)": "Adnabod Lleferydd (Vosk)",
    "Text-to-Speech": "Testun-i-Lais",
    "Text-to-Speech (Piper)": "Testun-i-Lais (Piper)",
    "Active Model": "Model Gweithredol",
    "Active Voice": "Llais Gweithredol",
    "Voice Triggers": "Sbardunau Llais",
    "Voice Corrections": "Cywiriadau Llais",
    "Voice Fingerprint": "Ôl Bys Llais",
    "Voice Learning": "Dysgu Llais",
    "Voice Training": "Hyfforddiant Llais",
    
    # UI Labels
    "Theme": "Thema",
    "Scale": "Graddfa",
    "Filter": "Hidlo",
    "Search": "Chwilio",
    "Name": "Enw",
    "Description": "Disgrifiad",
    "Path": "Llwybr",
    "File": "Ffeil",
    "Folder": "Ffolder",
    "Directory": "Cyfeiriadur",
    "Configuration": "Cyfluniad",
    "Options": "Opsiynau",
    "Preferences": "Dewisiadau",
    
    # Status messages
    "Saved": "Wedi Cadw",
    "Success": "Llwyddiant",
    "Error": "Gwall",
    "Info": "Gwybodaeth",
    "Warning": "Rhybudd",
    "Complete": "Cyflawn",
    "Failed": "Methiant",
    "Stopped": "Wedi Stopio",
    "Downloaded": "Wedi Lawrlwytho",
    "Downloading": "Wrthi'n lawrlwytho",
    "Importing": "Wrthi'n mewnforio",
    "Loading": "Wrthi'n llwytho",
    "Processing": "Wrthi'n prosesu",
    "Ready": "Barod",
    "Running": "Yn rhedeg",
    
    # Game Integration Specific
    "Game": "Gêm",
    "Game Type": "Math o Gêm",
    "Game Name": "Enw Gêm",
    "Game Group": "Grŵp Gêm",
    "Game Bindings File": "Ffeil Rhwymiadau Gêm",
    "Bindings Path": "Llwybr Rhwymiadau",
    "Bindings File Path": "Llwybr Ffeil Rhwymiadau",
    "Configuration Name": "Enw Cyfluniad",
    "Profile Name": "Enw Proffil",
    "Macro Profile": "Proffil Macro",
    "Defined Macros": "Macros Diffiniedig",
    "Macro Steps": "Camau Macro",
    "Delay": "Oedi",
    "Action": "Gweithred",
    "Key": "Bysell",
    "Source": "Ffynhonnell",
    "Built-in": "Wedi'i gynnwys",
    "Custom": "Personol",
    "Pack": "Pecyn",
    
    # Wizard/Dialog
    "Add Game": "Ychwanegu Gêm",
    "Edit Game": "Golygu Gêm",
    "Remove Game": "Tynnu Gêm",
    "Add Bind": "Ychwanegu Rhwymiad",
    "Edit Bind": "Golygu Rhwymiad",
    "Remove Bind": "Tynnu Rhwymiad",
    "Default Binds": "Rhwymiadau Diofyn",
    "Add Command": "Ychwanegu Gorchymyn",
    "Add Game Profile": "Ychwanegu Proffil Gêm",
    "Create Profile": "Creu Proffil",
    "Save Settings": "Cadw Gosodiadau",
    "Profile Settings": "Gosodiadau Proffil",
    "Profile Configuration": "Cyfluniad Proffil",
    
    # Steps/Process
    "Step 1": "Cam 1",
    "Step 2": "Cam 2",
    "Step 3": "Cam 3",
    "Select Running Game Process": "Dewis Proses Gêm sy'n Rhedeg",
    "Scan Processes": "Sganio Prosesau",
    "Scan Results": "Canlyniadau Sgan",
    "Command Line": "Llinell Orchymyn",
    "Command Line / Path": "Llinell Orchymyn / Llwybr",
    
    # Specific Actions
    "Enable Game Integration": "Galluogi Integreiddio Gêm",
    "Modify Trigger": "Addasu Sbardun",
    "Clear Trigger": "Clirio Sbardun",
    "Delete Selected": "Dileu'r Dewis",
    "Clear All": "Clirio Popeth",
    "Use Selected": "Defnyddio'r Dewis",
    "Restore Defaults": "Adfer Diofyn",
    "Import Defaults": "Mewnforio Diofyn",
    
    # Voice/Audio
    "Wake Word:": "Gair Deffro:",
    "Active Model:": "Model Gweithredol:",
    "Active Voice:": "Llais Gweithredol:",
    "Browse Folder": "Pori Ffolder",
    "Download from URL": "Lawrlwytho o URL",
    "Delete Voice": "Dileu Llais",
    "Import New Voice": "Mewnforio Llais Newydd",
    "Load from File (.onnx)": "Llwytho o Ffeil (.onnx)",
    
    # Correction/Training
    "When I hear...": "Pan fyddaf yn clywed...",
    "I should understand...": "Dylwn i ddeall...",
    "Test & Train": "Profi a Hyfforddi",
    "Record": "Recordio",
    "Dur:": "Hyd:",
    "Add as Correction": "Ychwanegu fel Cywiriad",
    "Targeted Train": "Hyfforddiant Targedig",
    "Basic": "Sylfaenol",
    "Advanced": "Uwch",
    "Recent Ignored/Missed Commands": "Gorchmynion diweddar a anwybyddwyd/methwyd",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Pwyswch y cyfuniad o fysellau ar eich bysellfwrdd:",
    "(Example: Ctrl + Alt + H)": "(Enghraifft: Ctrl + Alt + H)",
    "Clear": "Clirio",
    "Capture": "Cipio",
    "Key to Press:": "Bysell i'w Phwyso:",
    "Modifiers:": "Addaswyr:",
    
    # Game-Specific
    "Game Integration Status": "Statws Integreiddio Gêm",
    "Game:": "Gêm:",
    "Binds:": "Rhwymiadau:",
    "Macro Profile:": "Proffil Macro:",
    "Runtime Status:": "Statws Amser Rhedeg:",
    "Profile Name (Variant):": "Enw Proffil (Amrywiol):",
    "Binding Profile Name:": "Enw Proffil Rhwymo:",
    "Bindings File Path (Optional):": "Llwybr Ffeil Rhwymiadau (Dewisol):",
    "Process Name (e.g. X4.exe):": "Enw Proses (e.g. X4.exe):",
    "Game Type:": "Math o Gêm:",
    "Game Name:": "Enw Gêm:",
    "Process Name:": "Enw Proses:",
    "Runtime Environment:": "Amgylchedd Amser Rhedeg:",
    
    # Advanced Features
    "External Audio Assets": "Asedau Audio Allanol",
    "Audio Directory:": "Cyfeiriadur Audio:",
    "Reference File": "Ffeil Gyfeiriol",
    "Sound Pool": "Pwll Sain",
    "Playback Mode": "Modd Chwarae",
    "Random": "Ar Hap",
    "Simultaneous": "Cydamserol",
    "Sequential": "Dilyniannol",
    "Round-Robin": "Cylch-Robin",
    
    # Common long phrases (abbreviated)
    "Advanced Voice Control for Linux": "Rheolaeth Llais Uwch ar gyfer Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Pwyso i Siarad",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "Iawn",
    "Ctrl": "Ctrl",
    "Alt": "Alt",
    "Shift": "Shift",
    
    # Emojis/Icons (keep as-is)
    "🐧": "🐧",
    "➕": "➕",
    "✏": "✏",
    "🗑": "🗑",
    "↑": "↑",
    "↓": "↓",
    "🔄": "🔄",
    "🔍": "🔍",
    "💾": "💾",
    "🎤": "🎤",
    "⚠️": "⚠️",
}

PHRASES = {
    "Configuration saved.": "Wedi cadw'r cyfluniad.",
    "TuxTalks is already running.": "Mae TuxTalks eisoes yn rhedeg.",
    "Unsaved Changes": "Newidiadau Heb eu Cadw",
    "You have unsaved changes. Save before starting?": "Mae gennych newidiadau heb eu cadw. Cadw cyn cychwyn?",
    "Assistant stopped.": "Cynorthwyydd wedi stopio.",
    "Please select a game first.": "Dewiswch gêm yn gyntaf.",
    "No game selected.": "Dim gêm wedi'i dewis.",
    "Profile name cannot be empty.": "Ni all enw proffil fod yn wag.",
    "Failed to create macro profile.": "Methwyd â chreu proffil macro.",
    "Failed to delete macro profile.": "Methwyd â dileu proffil macro.",
    "Failed to rename macro profile.": "Methwyd ag ail-enwi proffil macro.",
    "No profile selected.": "Dim proffil wedi'i ddewis.",
    "Process Name required.": "Angen enw proses.",
    "Select a row to delete.": "Dewiswch res i'w dileu.",
    "Delete selected correction?": "Dileu'r cywiriad a ddewiswyd?",
    "Perfect match! No training needed.": "Gêm berffaith! Dim angen hyfforddiant.",
    "Correction added.": "Cywiriad wedi'i ychwanegu.",
    "Test a phrase first.": "Profi ymadrodd yn gyntaf.",
}

def translate_string(english):
    """Translate an English string to Welsh."""
    if english in WELSH_GLOSSARY:
        return WELSH_GLOSSARY[english]
    if english in PHRASES:
        return PHRASES[english]
    
    trimmed = english.strip()
    if trimmed != english and trimmed in WELSH_GLOSSARY:
        return WELSH_GLOSSARY[trimmed]
    if trimmed != english and trimmed in PHRASES:
        return PHRASES[trimmed]
    
    if english.endswith(':'):
        base = english[:-1].strip()
        if base in WELSH_GLOSSARY:
            return f"{WELSH_GLOSSARY[base]}:"
        
    if english.endswith('...'):
        base = english[:-3].strip()
        if base in WELSH_GLOSSARY:
            return f"{WELSH_GLOSSARY[base]}..."

    if not any(c.isalpha() for c in english):
        return english
    
    if english in ["PID", "UTF-8", "PTT", "X4", "TuxTalks", "Vosk", "Piper"]:
        return english
    
    return None

def auto_translate_po(filepath):
    """Automatically translate a .po file with our glossary."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = re.compile(r'(msgid\s+"(.*?)")\s+(msgstr\s+"(.*?)")', re.DOTALL)
    
    def replace_func(match):
        full_msgid_part = match.group(1)
        english_text = match.group(2)
        existing_translation = match.group(4)
        
        if existing_translation and existing_translation != english_text:
             return match.group(0)
             
        welsh = translate_string(english_text)
        if welsh:
            return f'{full_msgid_part}\nmsgstr "{welsh}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Auto-translated {filepath}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cy_dir = os.path.join(script_dir, 'locale/cy/LC_MESSAGES/')
    
    if os.path.exists(cy_dir):
        for filename in os.listdir(cy_dir):
            if filename.endswith('.po'):
                auto_translate_po(os.path.join(cy_dir, filename))
        
        print("\nNext steps:")
        print("1. Review translations in locale/cy/LC_MESSAGES/")
        print("2. Compile: pybabel compile -d locale")
    else:
        print(f"Error: {cy_dir} not found")
        sys.exit(1)
