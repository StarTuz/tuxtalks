#!/usr/bin/env python3
"""
German translation for TuxTalks using gaming-specific glossary.
Focused on HCS VoicePacks terminology where applicable.
"""

# German Gaming Glossary (English -> German)
GERMAN_GLOSSARY = {
    # UI Elements
    "Settings": "Einstellungen",
    "General": "Allgemein",
    "Voice": "Stimme",
    "Games": "Spiele",
    "Speech Engines": "Sprachmaschinen",
    "Input": "Eingabe",
    "Vocabulary": "Vokabular",
    "Help": "Hilfe",
    "Content Packs": "Inhaltspakete",
    "Corrections": "Korrekturen",
    
    # Actions
    "Start Assistant": "Assistent starten",
    "Stop": "Stopp",
    "Exit": "Beenden",
    "Save Config": "Konfiguration speichern",
    "Cancel": "Abbrechen",
    "Browse": "Durchsuchen",
    "Add": "Hinzufügen",
    "Edit": "Bearbeiten",
    "Delete": "Löschen",
    "Refresh": "Aktualisieren",
    "Clear": "Löschen",
    "New": "Neu",
    "Create": "Erstellen",
    "Remove": "Entfernen",
    "Import": "Importieren",
    "Export": "Exportieren",
    "Backup": "Sicherung",
    "Restore": "Wiederherstellen",
    "Test": "Testen",
    "Run": "Ausführen",
    "Save": "Speichern",
    "Apply": "Anwenden",
   
    # Gaming Terms (HCS VoicePacks compatible)
    "Bindings": "Tastenbelegung",
    "Binds": "Tastenbelegung",
    "Game Action": "Spiel-Aktion",
    "Voice Command": "Sprachbefehl",
    "Mapped Key": "Zugeordnete Taste",
    "Process Name": "Prozessname",
    "Binding Profile": "Belegungsprofil",
    "Macro": "Makro",
    "Macros": "Makros",
    "Profile": "Profil",
    "Game Integration": "Spiel-Integration",
    "Runtime Status": "Laufzeitstatus",
    "Runtime Environment": "Laufzeitumgebung",
    
    # Speech/Voice
    "Wake Word": "Aktivierungswort",
    "Speech Recognition": "Spracherkennung",
    "Text-to-Speech": "Text-zu-Sprache",
    "Active Model": "Aktives Modell",
    "Active Voice": "Aktive Stimme",
    "Voice Triggers": "Sprach-Trigger",
    "Voice Corrections": "Sprachkorrekturen",
    
    # Status messages
    "Saved": "Gespeichert",
    "Success": "Erfolgreich",
    "Error": "Fehler",
    "Info": "Info",
    "Warning": "Warnung",
    "Complete": "Vollständig",
    "Failed": "Fehlgeschlagen",
    "Stopped": "Gestoppt",
    "Downloaded": "Heruntergeladen",
    "Downloading": "Herunterladen",
    "Importing": "Importieren",
    
    # Common UI
    "Theme": "Thema",
    "Scale": "Skalierung",
    "Filter": "Filter",
    "Search": "Suchen",
    "Advanced Voice Control for Linux": "Erweiterte Sprachsteuerung für Linux",
}

def translate_to_german(po_file):
    """Apply German translations to .po file."""
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('msgid "'):
            msgid = line.split('msgid "')[1].rstrip('"\n')
            msgstr_line = lines[i + 1] if i + 1 < len(lines) else 'msgstr ""\n'
            
            if msgid and msgid in GERMAN_GLOSSARY:
                german = GERMAN_GLOSSARY[msgid]
                msgstr_line = f'msgstr "{german}"\n'
            
            output.append(line)
            output.append(msgstr_line)
            i += 2
        else:
            output.append(line)
            i += 1
    
    with open(po_file, 'w', encoding='utf-8') as f:
        f.writelines(output)
    
    print(f"✓ German translations applied to {po_file}")

if __name__ == '__main__':
    import sys
    po_file = sys.argv[1] if len(sys.argv) > 1 else 'locale/de/LC_MESSAGES/tuxtalks.po'
    translate_to_german(po_file)
    print(f"Translated {len(GERMAN_GLOSSARY)} terms")
