#!/usr/bin/env python3
"""
Automated German translation for TuxTalks using gaming-specific glossary.
Focused on HCS VoicePacks terminology where applicable.
"""

import re
import os
import sys

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
    "Training": "Training",
    "Player": "Reproductor",
    
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
    "OK": "OK",
    "Yes": "Ja",
    "No": "Nein",
    "Close": "Schließen",
    "Continue": "Weiter",
    
    # Gaming Terms
    "Bindings": "Tastenbelegungen",
    "Binds": "Belegungen",
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
    "Custom Commands": "Benutzerdefinierte Befehle",
    "Game Bindings": "Spiel-Tastenbelegungen",
    "Active Profile Bindings": "Aktive Profilbelegungen",
    
    # Speech/Voice
    "Wake Word": "Aktivierungswort",
    "Wake Word Settings": "Aktivierungswort-Einstellungen",
    "Speech Recognition": "Spracherkennung",
    "Speech Recognition (Vosk)": "Spracherkennung (Vosk)",
    "Text-to-Speech": "Text-zu-Sprache",
    "Text-to-Speech (Piper)": "Text-zu-Sprache (Piper)",
    "Active Model": "Aktives Modell",
    "Active Voice": "Aktive Stimme",
    "Voice Triggers": "Sprach-Trigger",
    "Voice Corrections": "Sprachkorrekturen",
    "Voice Fingerprint": "Sprach-Fingerabdruck",
    "Voice Learning": "Sprach-Lernen",
    "Voice Training": "Sprachtraining",
    
    # UI Labels
    "Theme": "Thema",
    "Scale": "Skalierung",
    "Filter": "Filter",
    "Search": "Suchen",
    "Name": "Name",
    "Description": "Beschreibung",
    "Path": "Pfad",
    "File": "Datei",
    "Folder": "Ordner",
    "Directory": "Verzeichnis",
    "Configuration": "Konfiguration",
    "Options": "Optionen",
    "Preferences": "Einstellungen",
    
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
    "Downloading": "Wird heruntergeladen",
    "Importing": "Wird importiert",
    "Loading": "Wird geladen",
    "Processing": "Wird verarbeitet",
    "Ready": "Bereit",
    "Running": "Wird ausgeführt",
    
    # Game Integration Specific
    "Game": "Spiel",
    "Game Type": "Spieltyp",
    "Game Name": "Spielname",
    "Game Group": "Spielgruppe",
    "Game Bindings File": "Spiel-Belegungsdatei",
    "Bindings Path": "Belegungspfad",
    "Bindings File Path": "Belegungsdateipfad",
    "Configuration Name": "Konfigurationsname",
    "Profile Name": "Profilname",
    "Macro Profile": "Makroprofil",
    "Defined Macros": "Definierte Makros",
    "Macro Steps": "Makroschritte",
    "Delay": "Verzögerung",
    "Action": "Aktion",
    "Key": "Taste",
    "Source": "Quelle",
    "Built-in": "Eingebaut",
    "Custom": "Benutzerdefiniert",
    "Pack": "Paket",
    
    # Wizard/Dialog
    "Add Game": "Spiel hinzufügen",
    "Edit Game": "Spiel bearbeiten",
    "Remove Game": "Spiel entfernen",
    "Add Bind": "Belegung hinzufügen",
    "Edit Bind": "Belegung bearbeiten",
    "Remove Bind": "Belegung entfernen",
    "Default Binds": "Standardbelegungen",
    "Add Command": "Befehl hinzufügen",
    "Add Game Profile": "Spielprofil hinzufügen",
    "Create Profile": "Profil erstellen",
    "Save Settings": "Einstellungen speichern",
    "Profile Settings": "Profileinstellungen",
    "Profile Configuration": "Profilkonfiguration",
    
    # Steps/Process
    "Step 1": "Schritt 1",
    "Step 2": "Schritt 2",
    "Step 3": "Schritt 3",
    "Select Running Game Process": "Laufenden Spielprozess auswählen",
    "Scan Processes": "Prozesse scannen",
    "Scan Results": "Scan-Ergebnisse",
    "Command Line": "Befehlszeile",
    "Command Line / Path": "Befehlszeile / Pfad",
    
    # Specific Actions
    "Enable Game Integration": "Spiel-Integration aktivieren",
    "Modify Trigger": "Trigger ändern",
    "Clear Trigger": "Trigger löschen",
    "Delete Selected": "Ausgewählte löschen",
    "Clear All": "Alles löschen",
    "Use Selected": "Ausgewählte verwenden",
    "Restore Defaults": "Standardwerte wiederherstellen",
    "Import Defaults": "Standardwerte importieren",
    
    # Voice/Audio
    "Wake Word:": "Aktivierungswort:",
    "Active Model:": "Aktives Modell:",
    "Active Voice:": "Aktive Stimme:",
    "Browse Folder": "Ordner durchsuchen",
    "Download from URL": "Von URL herunterladen",
    "Delete Voice": "Stimme löschen",
    "Import New Voice": "Neue Stimme importieren",
    "Load from File (.onnx)": "Aus Datei laden (.onnx)",
    
    # Correction/Training
    "When I hear...": "Wenn ich höre...",
    "I should understand...": "Sollte ich verstehen...",
    "Test & Train": "Testen & Trainieren",
    "Record": "Aufnehmen",
    "Dur:": "Dauer:",
    "Add as Correction": "Als Korrektur hinzufügen",
    "Targeted Train": "Gezieltes Training",
    "Basic": "Einfach",
    "Advanced": "Erweitert",
    "Recent Ignored/Missed Commands": "Zuletzt ignorierte/verpasste Befehle",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Drücken Sie die Tastenkombination auf Ihrer Tastatur:",
    "(Example: Ctrl + Alt + H)": "(Beispiel: Strg + Alt + H)",
    "Clear": "Löschen",
    "Capture": "Erfassen",
    "Key to Press:": "Zu drückende Taste:",
    "Modifiers:": "Modifikatoren:",
    
    # Game-Specific
    "Game Integration Status": "Spiel-Integrationsstatus",
    "Game:": "Spiel:",
    "Binds:": "Belegungen:",
    "Macro Profile:": "Makroprofil:",
    "Runtime Status:": "Laufzeitstatus:",
    "Profile Name (Variant):": "Profilname (Variante):",
    "Binding Profile Name:": "Profilname der Belegung:",
    "Bindings File Path (Optional):": "Pfad zur Belegungsdatei (Optional):",
    "Process Name (e.g. X4.exe):": "Prozessname (z.B. X4.exe):",
    "Game Type:": "Spieltyp:",
    "Game Name:": "Spielname:",
    "Process Name:": "Prozessname:",
    "Runtime Environment:": "Laufzeitumgebung:",
    
    # Advanced Features
    "External Audio Assets": "Externe Audio-Ressourcen",
    "Audio Directory:": "Audio-Verzeichnis:",
    "Reference File": "Referenzdatei",
    "Sound Pool": "Sound-Pool",
    "Playback Mode": "Wiedergabemodus",
    "Random": "Zufällig",
    "Simultaneous": "Gleichzeitig",
    "Sequential": "Sequentiell",
    "Round-Robin": "Reihum",
    
    # Common long phrases (abbreviated)
    "Advanced Voice Control for Linux": "Erweiterte Sprachsteuerung für Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Push-to-Talk",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "OK",
    "Ctrl": "Strg",
    "Alt": "Alt",
    "Shift": "Umschalt",
    
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
    "Configuration saved.": "Konfiguration gespeichert.",
    "TuxTalks is already running.": "TuxTalks läuft bereits.",
    "Unsaved Changes": "Nicht gespeicherte Änderungen",
    "You have unsaved changes. Save before starting?": "Sie haben nicht gespeicherte Änderungen. Vor dem Start speichern?",
    "Assistant stopped.": "Assistent gestoppt.",
    "Please select a game first.": "Bitte wählen Sie zuerst ein Spiel aus.",
    "No game selected.": "Kein Spiel ausgewählt.",
    "Profile name cannot be empty.": "Profilname darf nicht leer sein.",
    "Failed to create macro profile.": "Makroprofil konnte nicht erstellt werden.",
    "Failed to delete macro profile.": "Makroprofil konnte nicht gelöscht werden.",
    "Failed to rename macro profile.": "Makroprofil konnte nicht umbenannt werden.",
    "No profile selected.": "Kein Profil ausgewählt.",
    "Process Name required.": "Prozessname erforderlich.",
    "Select a row to delete.": "Wählen Sie eine Zeile zum Löschen aus.",
    "Delete selected correction?": "Ausgewählte Korrektur löschen?",
    "Perfect match! No training needed.": "Perfekte Übereinstimmung! Kein Training erforderlich.",
    "Correction added.": "Korrektur hinzugefügt.",
    "Test a phrase first.": "Testen Sie zuerst eine Phrase.",
}

def translate_string(english):
    """Translate an English string to German."""
    if english in GERMAN_GLOSSARY:
        return GERMAN_GLOSSARY[english]
    if english in PHRASES:
        return PHRASES[english]
    
    trimmed = english.strip()
    if trimmed != english and trimmed in GERMAN_GLOSSARY:
        return GERMAN_GLOSSARY[trimmed]
    if trimmed != english and trimmed in PHRASES:
        return PHRASES[trimmed]
    
    if english.endswith(':'):
        base = english[:-1].strip()
        if base in GERMAN_GLOSSARY:
            return f"{GERMAN_GLOSSARY[base]}:"
        
    if english.endswith('...'):
        base = english[:-3].strip()
        if base in GERMAN_GLOSSARY:
            return f"{GERMAN_GLOSSARY[base]}..."

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
             
        german = translate_string(english_text)
        if german:
            return f'{full_msgid_part}\nmsgstr "{german}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Auto-translated {filepath}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    de_dir = os.path.join(script_dir, 'locale/de/LC_MESSAGES/')
    
    if os.path.exists(de_dir):
        for filename in os.listdir(de_dir):
            if filename.endswith('.po'):
                auto_translate_po(os.path.join(de_dir, filename))
        
        print("\nNext steps:")
        print("1. Review translations in locale/de/LC_MESSAGES/")
        print("2. Compile: pybabel compile -d locale")
    else:
        print(f"Error: {de_dir} not found")
        sys.exit(1)
