#!/usr/bin/env python3
"""
Automated Welsh translation for TuxTalks using gaming-specific glossary.
Enhances all .po files in the Welsh locale.
"""

import re
import os
import sys

# Gaming-specific glossary (English -> Welsh)
GAMING_GLOSSARY = {
    # UI Elements (general terms)
    "Settings": "Gosodiadau",
    "General": "Cyffredinol",
    "Voice": "Llais",
    "Games": "Gemau",
    "Speech Engines": "Peiriannau Lleferydd",
    "Input": "Mewnbwn",
    "Vocabulary": "Geirfa",
    "Help": "Cymorth",
    "Content Packs": "Pecynnau Cynnwys",
    "Corrections": "Cywiriadau",
    "Training": "Hyfforddiant",
    "Player": "Chwaraewr",
    
    # Actions
    "Start Assistant": "Dechrau Cynorthwyydd",
    "Stop": "Stopio",
    "Exit": "Gadael",
    "Save Config": "Cadw Ffurfweddiad",
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
    "Backup": "Copi wrth gefn",
    "Restore": "Adfer",
    "Test": "Profi",
    "Run": "Rhedeg",
    "Save": "Cadw",
    "Apply": "Gweithredu",
    "OK": "Iawn",
    "Yes": "Ie",
    "No": "Na",
    "Close": "Cau",
    "Continue": "Parhau",
    
    # Gaming Terms
    "Bindings": "Rhwymidau",
    "Binds": "Allweddi",
    "Game Action": "Gweithred Gêm",
    "Voice Command": "Gorchymyn Llais",
    "Mapped Key": "Allwedd wedi'i Mapio",
    "Process Name": "Enw Proses",
    "Binding Profile": "Proffil Rhwymo",
    "Macro": "Macro",
    "Macros": "Macros",
    "Profile": "Proffil",
    "Game Integration": "Integreiddio Gêm",
    "Runtime Status": "Statws Rhedeg",
    "Runtime Environment": "Amgylchedd Rhedeg",
    "Custom Commands": "Gorchmynion Personol",
    "Game Bindings": "Rhwymidau Gêm",
    "Active Profile Bindings": "Rhwymidau Proffil Actif",
    
    # Speech/Voice
    "Wake Word": "Gair Deffro",
    "Wake Word Settings": "Gosodiadau Gair Deffro",
    "Speech Recognition": "Adnabod Lleferydd",
    "Speech Recognition (Vosk)": "Adnabod Lleferydd (Vosk)",
    "Text-to-Speech": "Testun-i-Lleferydd",
    "Text-to-Speech (Piper)": "Testun-i-Lleferydd (Piper)",
    "Active Model": "Model Actif",
    "Active Voice": "Llais Actif",
    "Voice Triggers": "Sbardunau Llais",
    "Voice Corrections": "Cywiriadau Llais",
    "Voice Fingerprint": "Olion Bysedd Llais",
    "Voice Learning": "Dysgu Llais",
    "Voice Training": "Hyfforddi Llais",
    
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
    "Configuration": "Ffurfweddiad",
    "Options": "Opsiynau",
    "Preferences": "Dewisiadau",
    
    # Status messages
    "Saved": "Wedi'i gadw",
    "Success": "Llwyddiant",
    "Error": "Gwall",
    "Info": "Gwybodaeth",
    "Warning": "Rhybudd",
    "Complete": "Wedi'i gwblhau",
    "Failed": "Wedi methu",
    "Stopped": "Wedi stopio",
    "Downloaded": "Wedi'i lawrlwytho",
    "Downloading": "Yn lawrlwytho",
    "Importing": "Yn mewnforio",
    "Loading": "Yn llwytho",
    "Processing": "Yn prosesu",
    "Ready": "Yn barod",
    "Running": "Yn rhedeg",
    
    # Game Integration Specific
    "Game": "Gêm",
    "Game Type": "Math o Gêm",
    "Game Name": "Enw Gêm",
    "Game Group": "Grŵp Gêm",
    "Game Bindings File": "Ffeil Rhwymidau Gêm",
    "Bindings Path": "Llwybr Rhwymidau",
    "Bindings File Path": "Llwybr Ffeil Rhwymidau",
    "Configuration Name": "Enw Ffurfweddiad",
    "Profile Name": "Enw Proffil",
    "Macro Profile": "Proffil Macro",
    "Defined Macros": "Macros wedi'u Diffinio",
    "Macro Steps": "Camau Macro",
    "Delay": "Oedi",
    "Action": "Gweithred",
    "Key": "Allwedd",
    "Source": "Ffynhonnell",
    "Built-in": "Adeiladedig",
    "Custom": "Personol",
    "Pack": "Pecyn",
    
    # Wizard/Dialog
    "Add Game": "Ychwanegu Gêm",
    "Edit Game": "Golygu Gêm",
    "Remove Game": "Tynnu Gêm",
    "Add Bind": "Ychwanegu Rhwymyn",
    "Edit Bind": "Golygu Rhwymyn",
    "Remove Bind": "Tynnu Rhwymyn",
    "Default Binds": "Rhwymidau Rhagosodedig",
    "Add Command": "Ychwanegu Gorchymyn",
    "Add Game Profile": "Ychwanegu Proffil Gêm",
    "Create Profile": "Creu Proffil",
    "Save Settings": "Cadw Gosodiadau",
    "Profile Settings": "Gosodiadau Proffil",
    "Profile Configuration": "Ffurfweddiad Proffil",
    
    # Steps/Process
    "Step 1": "Cam 1",
    "Step 2": "Cam 2",
    "Step 3": "Cam 3",
    "Select Running Game Process": "Dewiswch Broses Gêm sy'n Rhedeg",
    "Scan Processes": "Sganio Prosesau",
    "Scan Results": "Canlyniadau Sganio",
    "Command Line": "Llinell Orchymyn",
    "Command Line / Path": "Llinell Orchymyn / Llwybr",
    
    # Specific Actions
    "Enable Game Integration": "Galluogi Integreiddio Gêm",
    "Modify Trigger": "Addasu Sbardun",
    "Clear Trigger": "Clirio Sbardun",
    "Delete Selected": "Dileu Dewis",
    "Clear All": "Clirio Popeth",
    "Use Selected": "Defnyddio Dewis",
    "Restore Defaults": "Adfer Rhagosodiadau",
    "Import Defaults": "Mewnforio Rhagosodiadau",
    
    # Voice/Audio
    "Wake Word:": "Gair Deffro:",
    "Active Model:": "Model Actif:",
    "Active Voice:": "Llais Actif:",
    "Browse Folder": "Pori Ffolder",
    "Download from URL": "Lawrlwytho o URL",
    "Delete Voice": "Dileu Llais",
    "Import New Voice": "Mewnforio Llais Newydd",
    "Load from File (.onnx)": "Llwytho o Ffeil (.onnx)",
    
    # Correction/Training
    "When I hear...": "Pan fyddaf yn clywed...",
    "I should understand...": "Dylwn ddeall...",
    "Test & Train": "Profi a Hyfforddi",
    "Record": "Recordio",
    "Dur:": "Parhad:",
    "Add as Correction": "Ychwanegu fel Cywiriad",
    "Targeted Train": "Hyfforddiant wedi'i Dargedu",
    "Basic": "Sylfaenol",
    "Advanced": "Uwch",
    "Recent Ignored/Missed Commands": "Gorchmynion diweddar wedi'u hanwybyddu/methu",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Pwyswch y cyfuniad allweddi ar eich bysellfwrdd:",
    "(Example: Ctrl + Alt + H)": "(Engraifft: Ctrl + Alt + H)",
    "Clear": "Clirio",
    "Capture": "Cipio",
    "Key to Press:": "Allwedd i'w Gwasgu:",
    "Modifiers:": "Addaswyr:",
    
    # Game-Specific
    "Game Integration Status": "Statws Integreiddio Gêm",
    "Game:": "Gêm:",
    "Binds:": "Rhwymidau:",
    "Macro Profile:": "Proffil Macro:",
    "Runtime Status:": "Statws Rhedeg:",
    "Profile Name (Variant):": "En Enw Proffil (Amrywiad):",
    "Binding Profile Name:": "Enw Proffil Rhwymo:",
    "Bindings File Path (Optional):": "Llwybr Ffeil Rhwymidau (Dewisol):",
    "Process Name (e.g. X4.exe):": "Enw Proses (e.e. X4.exe):",
    "Game Type:": "Math o Gêm:",
    "Game Name:": "Enw Gêm:",
    "Process Name:": "Enw Proses:",
    "Runtime Environment:": "Amgylchedd Rhedeg:",
    
    # Advanced Features
    "External Audio Assets": "Asedau Sain Allanol",
    "Audio Directory:": "Cyfeiriadur Sain:",
    "Reference File": "Ffeil Gyfeirio",
    "Sound Pool": "Pwll Sain",
    "Playback Mode": "Modd Chwarae",
    "Random": "Ar Hap",
    "Simultaneous": "Ar y Cyd",
    "Sequential": "Dilyniannol",
    "Round-Robin": "Cylch-Robin",
    
    # Common long phrases
    "Advanced Voice Control for Linux": "Rheolaeth Llais Uwch ar gyfer Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Gwasgwch i Siarad",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "Iawn",
    "Ctrl": "Ctrl",
    "Alt": "Alt",
    "Shift": "Shift",
    
    # Wizard setup
    "TuxTalks First-Run Setup": "Setup rhediad cyntaf TuxTalks",
    "Welcome to TuxTalks! 🐧": "Croeso i TuxTalks! 🐧",
    "TuxTalks is your powerful, secure, and offline voice command assistant for Linux gaming.\n\nThis wizard will help you set up your core preferences in just a few minutes so you can start talking to your favorite games and media players.": "TuxTalks yw eich cynorthwyydd gorchymyn llais pwerus, diogel ac all-lein ar gyfer hapchwarae Linux.\n\nBydd y dewin hwn yn eich helpu i sefydlu eich dewisiadau craidd mewn ychydig funudau fel y gallwch ddechrau siarad â'ch hoff gemau a chwaraewyr cyfryngau.",
    "Ready to begin?": "Yn barod i ddechrau?",
    "Step 1: Interface Language": "Cam 1: Iaith y Rhyngwyneb",
    "Select the language for the TuxTalks interface:": "Dewiswch yr iaith ar gyfer rhyngwyneb TuxTalks:",
    "Note: RTL support is automatically enabled for Arabic.": "Nodyn: Mae cefnogaeth RTL yn cael ei alluogi'n awtomatig ar gyfer Arabeg.",
    "Step 2: Voice Recognition (ASR)": "Cam 2: Adnabod Llais (ASR)",
    "To process your voice offline, TuxTalks needs a language model.\n\nBased on your language selection, we recommend the following model:": "I brosesu eich llais all-lein, mae angen model iaith ar TuxTalks.\n\nYn seiliedig ar eich dewis iaith, rydym yn argymell y model canlynol:",
    "Download & Install": "Lawrlwytho a Gosod",
    "Step 3: Initial Integration": "Cam 3: Integreiddio Cychwynnol",
    "Choose your primary media player:": "Dewiswch eich prif chwaraewr cyfryngau:",
    "Tip: You can change this and add games later in the main settings.": "Awgrym: Gallwch newid hwn ac ychwanegu gemau yn nes ymlaen yn y prif osodiadau.",
    "All Set! 🎉": "Popeth yn Barod! 🎉",
    "Setup is complete. TuxTalks is now configured with your language and voice preferences.\n\nClick 'Finish' to open the main settings where you can further customize your experience, add games, and calibrate your microphone.": "Mae'r gosodiad wedi'i gwblhau. Mae TuxTalks bellach wedi'i ffurfweddu gyda'ch dewisiadau iaith a llais.\n\nCliciwch 'Gorffen' i agor y prif osodiadau lle gallwch chi barhau i addasu eich profiad, ychwanegu gemau, a graddnodi eich meicroffon.",
    "Skip Setup?": "Hepgor y Gosodiad?",
    "Closing this window will skip the setup wizard. You can still configure everything manually in the settings.\n\nSkip and don't show again?": "Bydd cau'r ffenestr hon yn hepgor y dewin gosod. Gallwch ddal i ffurfweddu popeth â llaw yn y gosodiadau.\n\nHepgor a pheidio â dangos eto?",
}

# Sentence fragments/phrases
PHRASES = {
    "Configuration saved.": "Ffurfweddiad wedi'i gadw.",
    "TuxTalks is already running.": "Mae TuxTalks eisoes yn rhedeg.",
    "Unsaved Changes": "Newidiadau Heb eu Cadw",
    "You have unsaved changes. Save before starting?": "Mae gennych newidiadau heb eu cadw. Cadw cyn dechrau?",
    "Assistant stopped.": "Cynorthwyydd wedi stopio.",
    "Please select a game first.": "Dewiswch gêm yn gyntaf.",
    "No game selected.": "Dim gêm wedi'i dewis.",
    "Profile name cannot be empty.": "Ni all enw proffil fod yn wag.",
    "Failed to create macro profile.": "Methwyd â chreu proffil macro.",
    "Failed to delete macro profile.": "Methwyd â dileu proffil macro.",
    "Failed to rename macro profile.": "Methwyd ag ailenwi proffil macro.",
    "No profile selected.": "Dim proffil wedi'i ddewis.",
    "Process Name required.": "Enw Proses yn ofynnol.",
    "Select a row to delete.": "Dewiswch res i'w dileu.",
    "Delete selected correction?": "Dileu cywiriad dewisol?",
    "Perfect match! No training needed.": "Gêm berffaith! Dim angen hyfforddiant.",
    "Correction added.": "Cywiriad wedi'i ychwanegu.",
    "Test a phrase first.": "Profi ymadrodd yn gyntaf.",
    "Scaling saved. Restart required for full effect.": "Graddfa wedi'i chadw. Angen ailgychwyn am effaith lawn.",
    "All detected game actions typically have voice commands assigned!\nYou can still edit existing ones.": "Fel arfer mae gan bob gweithred gêm a ganfyddir orchmynion llais wedi'u neilltuo!\nGallwch barhau i olygu rhai presennol.",
    "Please select a Game grouping first.": "Dewiswch grŵp Gêm yn gyntaf.",
    "Internal Error: Active bindings path is unknown.": "Gwall Mewnol: Mae llwybr rhwymidau actif yn anhysbys.",
    "Select an action to rebind.": "Dewiswch weithred i'w hail-rwymo.",
    "No profiles found in this group.": "Ni chafwyd proffiliau yn y grŵp hwn.",
    "No standard binding files found for this game type.": "Ni chafwyd ffeiliau rhwymo safonol ar gyfer y math hwn o gêm.",
    "Failed to remove profiles.": "Methwyd â thynnu proffiliau.",
    "Name already taken.": "Enw eisoes wedi'i gymryd.",
    "No profiles found. (Check console for path/parsing errors)": "Ni chafwyd proffiliau. (Gwiriwch y consol am wallau llwybr/dosrannu)",
    "Import Complete": "Mewnforio wedi'i Gwblhau",
    "No profiles found.": "Ni chafwyd proffiliau.",
    "Elite Dangerous appears to be running.\n\nChanges made now may NOT take effect immediately or could be overwritten by the game.\n\nContinue anyway?": "Ymddengys bod Elite Dangerous yn rhedeg.\n\nEfallai NA fydd newidiadau a wneir nawr yn dod i rym ar unwaith neu gallent gael eu trosysgrifo gan y gêm.\n\nParhau deall?",
    "Scan and import standard Elite Dangerous ControlSchemes?\nThis may double up profiles if you already have them, but skips duplicate names.": "Sganio a mewnforio ControlSchemes safonol Elite Dangerous?\nGall hyn ddyblu proffiliau os oes gennych chi nhw eisoes, ond mae'n hepgor enwau dyblyg.",
    "Importing voice in background...": "Yn mewnforio llais yn y cefndir...",
    "Downloading voice in background...": "Yn lawrlwytho llais yn y cefndir...",
    "Failed to install voice.": "Methwyd â gosod llais.",
    "Failed to import voice.": "Methwyd â mewnforio llais.",
}

def translate_string(english):
    """Translate an English string to Welsh."""
    # Direct match
    if english in GAMING_GLOSSARY:
        return GAMING_GLOSSARY[english]
    if english in PHRASES:
        return PHRASES[english]
    
    # Check for close matches (trim spaces)
    trimmed = english.strip()
    if trimmed != english and trimmed in GAMING_GLOSSARY:
        return GAMING_GLOSSARY[trimmed]
    if trimmed != english and trimmed in PHRASES:
        return PHRASES[trimmed]
    
    # Handle colons at the end
    if english.endswith(':'):
        base = english[:-1].strip()
        if base in GAMING_GLOSSARY:
            return f"{GAMING_GLOSSARY[base]}:"
        
    # Handle ellipses at the end
    if english.endswith('...'):
        base = english[:-3].strip()
        if base in GAMING_GLOSSARY:
            return f"{GAMING_GLOSSARY[base]}..."

    # Don't translate emojis, symbols, technical terms
    if not any(c.isalpha() for c in english):
        return english
    
    if english in ["PID", "UTF-8", "PTT", "X4", "TuxTalks", "Vosk", "Piper", "JRiver", "Strawberry", "Elisa", "MPRIS"]:
        return english
    
    # Return None for now - manual translation needed or keep English
    return None

def auto_translate_po(filepath):
    """Automatically translate a .po file with our glossary."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match msgid and msgstr pairs, handling potential multi-line msgids
    pattern = re.compile(r'(msgid\s+"(.*?)")\s+(msgstr\s+"(.*?)")', re.DOTALL)
    
    def replace_func(match):
        full_msgid_part = match.group(1)
        english_text = match.group(2)
        full_msgstr_part = match.group(3)
        existing_translation = match.group(4)
        
        # Don't overwrite existing non-empty translations unless they are just placeholders
        if existing_translation and existing_translation != english_text:
             return match.group(0)
             
        welsh = translate_string(english_text)
        if welsh:
            return f'{full_msgid_part}\nmsgstr "{welsh}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    # Write back
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
