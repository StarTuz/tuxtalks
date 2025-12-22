#!/usr/bin/env python3
"""
Welsh (Cymraeg) translation for TuxTalks using gaming-specific glossary.
"""

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
    
    # Speech/Voice
    "Wake Word": "Gair Deffro",
    "Speech Recognition": "Adnabod Lleferydd",
    "Text-to-Speech": "Testun-i-Lais",
    "Active Model": "Model Gweithredol",
    "Active Voice": "Llais Gweithredol",
    "Voice Triggers": "Sbardunau Llais",
    "Voice Corrections": "Cywiriadau Llais",
    
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
    "Downloading": "Lawrlwytho",
    "Importing": "Mewnforio",
    
    # Common UI
    "Theme": "Thema",
    "Scale": "Graddfa",
    "Filter": "Hidlo",
    "Search": "Chwilio",
    "Advanced Voice Control for Linux": "Rheolaeth Llais Uwch ar gyfer Linux",
}

def translate_to_welsh(po_file):
    """Apply Welsh translations to .po file."""
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('msgid "'):
            msgid = line.split('msgid "')[1].rstrip('"\n')
            msgstr_line = lines[i + 1] if i + 1 < len(lines) else 'msgstr ""\n'
            
            if msgid and msgid in WELSH_GLOSSARY:
                welsh = WELSH_GLOSSARY[msgid]
                msgstr_line = f'msgstr "{welsh}"\n'
            
            output.append(line)
            output.append(msgstr_line)
            i += 2
        else:
            output.append(line)
            i += 1
    
    with open(po_file, 'w', encoding='utf-8') as f:
        f.writelines(output)
    
    print(f"✓ Welsh translations applied to {po_file}")

if __name__ == '__main__':
    import sys
    po_file = sys.argv[1] if len(sys.argv) > 1 else 'locale/cy/LC_MESSAGES/tuxtalks.po'
    translate_to_welsh(po_file)
    print(f"Translated {len(WELSH_GLOSSARY)} terms")
