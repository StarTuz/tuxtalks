#!/usr/bin/env python3
"""
Automated German translation for TuxTalks using gaming-specific glossary.
Enhances all .po files in the German locale.
"""

import re
import os
import sys

# Gaming-specific glossary (English -> German)
GAMING_GLOSSARY = {
    # UI Elements (general terms)
    "Settings": "Einstellungen",
    "General": "Allgemein",
    "Voice": "Stimme",
    "Games": "Spiele",
    "Speech Engines": "Sprach-Engines",
    "Input": "Eingabe",
    "Vocabulary": "Vokabular",
    "Help": "Hilfe",
    "Content Packs": "Inhaltspakete",
    "Corrections": "Korrekturen",
    "Training": "Training",
    "Player": "Player",
    
    # Actions
    "Start Assistant": "Assistent starten",
    "Stop": "Stopp",
    "Exit": "Beenden",
    "Save Config": "Konf. speichern",
    "Cancel": "Abbrechen",
    "Browse": "Durchsuchen",
    "Add": "Hinzufügen",
    "Edit": "Bearbeiten",
    "Delete": "Löschen",
    "Refresh": "Aktualisieren",
    "Clear": "Leeren",
    "New": "Neu",
    "Create": "Erstellen",
    "Remove": "Entfernen",
    "Import": "Importieren",
    "Export": "Exportieren",
    "Backup": "Backup",
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
    "Game Action": "Spielaktion",
    "Voice Command": "Sprachbefehl",
    "Mapped Key": "Zugeordnete Taste",
    "Process Name": "Prozessname",
    "Binding Profile": "Belegungsprofil",
    "Macro": "Makro",
    "Macros": "Makros",
    "Profile": "Profil",
    "Game Integration": "Spielintegration",
    "Runtime Status": "Laufzeitstatus",
    "Runtime Environment": "Laufzeitumgebung",
    "Custom Commands": "Benutzerdefinierte Befehle",
    "Game Bindings": "Spielbelegungen",
    "Active Profile Bindings": "Belegungen des aktiven Profils",
    
    # Speech/Voice
    "Wake Word": "Aktivierungswort",
    "Wake Word Settings": "Aktivierungswort-Einstellungen",
    "Speech Recognition": "Spracherkennung",
    "Speech Recognition (Vosk)": "Spracherkennung (Vosk)",
    "Text-to-Speech": "Text-zu-Sprache",
    "Text-to-Speech (Piper)": "Text-zu-Sprache (Piper)",
    "Active Model": "Aktives Modell",
    "Active Voice": "Aktive Stimme",
    "Voice Triggers": "Sprachauslöser",
    "Voice Corrections": "Sprachkorrekturen",
    "Voice Fingerprint": "Sprach-Fingerabdruck",
    "Voice Learning": "Sprach-Lernen",
    "Voice Training": "Sprachtraining",
    
    # UI Labels
    "Theme": "Design",
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
    "Preferences": "Präferenzen",
    
    # Status messages
    "Saved": "Gespeichert",
    "Success": "Erfolg",
    "Error": "Fehler",
    "Info": "Info",
    "Warning": "Warnung",
    "Complete": "Abgeschlossen",
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
    "Game Bindings File": "Spielbelegungsdatei",
    "Bindings Path": "Belegungspfad",
    "Bindings File Path": "Pfad zur Belegungsdatei",
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
    "Scan Results": "Scannergebnisse",
    "Command Line": "Befehlszeile",
    "Command Line / Path": "Befehlszeile / Pfad",
    
    # Specific Actions
    "Enable Game Integration": "Spielintegration aktivieren",
    "Modify Trigger": "Auslöser ändern",
    "Clear Trigger": "Auslöser löschen",
    "Delete Selected": "Auswahl löschen",
    "Clear All": "Alles löschen",
    "Use Selected": "Auswahl verwenden",
    "Restore Defaults": "Standards wiederherstellen",
    "Import Defaults": "Standards importieren",
    
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
    "Basic": "Grundlagen",
    "Advanced": "Fortgeschritten",
    "Recent Ignored/Missed Commands": "Zuletzt ignorierte/verpasste Befehle",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Drücke die Tastenkombination auf deiner Tastatur:",
    "(Example: Ctrl + Alt + H)": "(Beispiel: Strg + Alt + H)",
    "Clear": "Löschen",
    "Capture": "Erfassen",
    "Key to Press:": "Taste zum Drücken:",
    "Modifiers:": "Modifikatoren:",
    
    # Game-Specific
    "Game Integration Status": "Spielintegrations-Status",
    "Game:": "Spiel:",
    "Binds:": "Belegungen:",
    "Macro Profile:": "Makroprofil:",
    "Runtime Status:": "Laufzeitstatus:",
    "Profile Name (Variant):": "Profilname (Variante):",
    "Binding Profile Name:": "Belegungsprofilname:",
    "Bindings File Path (Optional):": "Pfad zur Belegungsdatei (Optional):",
    "Process Name (e.g. X4.exe):": "Prozessname (z.B. X4.exe):",
    "Game Type:": "Spieltyp:",
    "Game Name:": "Spielname:",
    "Process Name:": "Prozessname:",
    "Runtime Environment:": "Laufzeitumgebung:",
    
    # Advanced Features
    "External Audio Assets": "Externe Audio-Assets",
    "Audio Directory:": "Audio-Verzeichnis:",
    "Reference File": "Referenzdatei",
    "Sound Pool": "Sound-Pool",
    "Playback Mode": "Wiedergabemodus",
    "Random": "Zufällig",
    "Simultaneous": "Gleichzeitig",
    "Sequential": "Sequenziell",
    "Round-Robin": "Round-Robin",
    
    # Common long phrases (German translations tend to be longer)
    "Advanced Voice Control for Linux": "Fortgeschrittene Sprachsteuerung für Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Push-to-Talk",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "OK",
    "Ctrl": "Strg",
    "Alt": "Alt",
    "Shift": "Umschalt",
    
    # Wizard setup
    "TuxTalks First-Run Setup": "TuxTalks Ersteinrichtung",
    "Welcome to TuxTalks! 🐧": "Willkommen bei TuxTalks! 🐧",
    "TuxTalks is your powerful, secure, and offline voice command assistant for Linux gaming.\n\nThis wizard will help you set up your core preferences in just a few minutes so you can start talking to your favorite games and media players.": "TuxTalks ist dein leistungsstarker, sicherer und Offline-Sprachbefehls-Assistent für Linux-Gaming.\n\nDieser Assistent hilft dir, deine Grundeinstellungen in nur wenigen Minuten vorzunehmen, damit du anfangen kannst, mit deinen Lieblingsspielen und Mediaplayern zu sprechen.",
    "Ready to begin?": "Bereit zum Start?",
    "Step 1: Interface Language": "Schritt 1: Benutzeroberflächen-Sprache",
    "Select the language for the TuxTalks interface:": "Wähle die Sprache für die TuxTalks-Oberfläche:",
    "Note: RTL support is automatically enabled for Arabic.": "Hinweis: RTL-Unterstützung wird für Arabisch automatisch aktiviert.",
    "Step 2: Voice Recognition (ASR)": "Schritt 2: Spracherkennung (ASR)",
    "To process your voice offline, TuxTalks needs a language model.\n\nBased on your language selection, we recommend the following model:": "Um deine Stimme offline zu verarbeiten, benötigt TuxTalks ein Sprachmodell.\n\nBasierend auf deiner Sprachauswahl empfehlen wir das folgende Modell:",
    "Download & Install": "Herunterladen & Installieren",
    "Step 3: Initial Integration": "Schritt 3: Erst-Integration",
    "Choose your primary media player:": "Wähle deinen primären Mediaplayer:",
    "Tip: You can change this and add games later in the main settings.": "Tipp: Du kannst dies später in den Haupteinstellungen ändern und Spiele hinzufügen.",
    "All Set! 🎉": "Alles bereit! 🎉",
    "Setup is complete. TuxTalks is now configured with your language and voice preferences.\n\nClick 'Finish' to open the main settings where you can further customize your experience, add games, and calibrate your microphone.": "Das Setup ist abgeschlossen. TuxTalks ist nun mit Ihren Sprach- und Voice-Präferenzen konfiguriert.\n\nKlicken Sie auf 'Fertig stellen', um die Haupteinstellungen zu öffnen, wo Sie Ihr Erlebnis weiter anpassen, Spiele hinzufügen und Ihr Mikrofon kalibrieren können.",
    "Skip Setup?": "Setup überspringen?",
    "Closing this window will skip the setup wizard. You can still configure everything manually in the settings.\n\nSkip and don't show again?": "Das Schließen dieses Fensters überspringt den Einrichtungsassistenten. Sie können weiterhin alles manuell in den Einstellungen konfigurieren.\n\nÜberspringen und nicht mehr anzeigen?",
}

# Sentence fragments/phrases
PHRASES = {
    "Configuration saved.": "Konfiguration gespeichert.",
    "TuxTalks is already running.": "TuxTalks läuft bereits.",
    "Unsaved Changes": "Ungespeicherte Änderungen",
    "You have unsaved changes. Save before starting?": "Du hast ungespeicherte Änderungen. Vor dem Start speichern?",
    "Assistant stopped.": "Assistent gestoppt.",
    "Please select a game first.": "Bitte wähle zuerst ein Spiel aus.",
    "No game selected.": "Kein Spiel ausgewählt.",
    "Profile name cannot be empty.": "Profilname darf nicht leer sein.",
    "Failed to create macro profile.": "Erstellen des Makroprofils fehlgeschlagen.",
    "Failed to delete macro profile.": "Löschen des Makroprofils fehlgeschlagen.",
    "Failed to rename macro profile.": "Umbenennen des Makroprofils fehlgeschlagen.",
    "No profile selected.": "Kein Profil ausgewählt.",
    "Process Name required.": "Prozessname erforderlich.",
    "Select a row to delete.": "Wähle eine Zeile zum Löschen aus.",
    "Delete selected correction?": "Ausgewählte Korrektur löschen?",
    "Perfect match! No training needed.": "Perfekte Übereinstimmung! Kein Training erforderlich.",
    "Correction added.": "Korrektur hinzugefügt.",
    "Test a phrase first.": "Teste zuerst eine Phrase.",
    "Scaling saved. Restart required for full effect.": "Skalierung gespeichert. Neustart für volle Wirkung erforderlich.",
    "All detected game actions typically have voice commands assigned!\nYou can still edit existing ones.": "Allen erkannten Spielaktionen sind normalerweise Sprachbefehle zugewiesen!\nDu kannst bestehende noch bearbeiten.",
    "Please select a Game grouping first.": "Bitte wähle zuerst eine Spielgruppe aus.",
    "Internal Error: Active bindings path is unknown.": "Interner Fehler: Aktiver Belegungspfad ist unbekannt.",
    "Select an action to rebind.": "Wähle eine Aktion zur Neubelegung aus.",
    "No profiles found in this group.": "Keine Profile in dieser Gruppe gefunden.",
    "No standard binding files found for this game type.": "Keine Standardbelegungsdateien für diesen Spieltyp gefunden.",
    "Failed to remove profiles.": "Entfernen der Profile fehlgeschlagen.",
    "Name already taken.": "Name bereits vergeben.",
    "No profiles found. (Check console for path/parsing errors)": "Keine Profile gefunden. (Konsole auf Pfad-/Parsing-Fehler prüfen)",
    "Import Complete": "Import abgeschlossen",
    "No profiles found.": "Keine Profile gefunden.",
    "Elite Dangerous appears to be running.\n\nChanges made now may NOT take effect immediately or could be overwritten by the game.\n\nContinue anyway?": "Elite Dangerous scheint zu laufen.\n\nJetzt vorgenommene Änderungen werden möglicherweise NICHT sofort wirksam oder könnten vom Spiel überschrieben werden.\n\nTrotzdem fortfahren?",
    "Scan and import standard Elite Dangerous ControlSchemes?\nThis may double up profiles if you already have them, but skips duplicate names.": "Standard-Elite-Dangerous-ControlSchemes scannen und importieren?\nDies kann Profile verdoppeln, wenn du sie bereits hast, überspringt aber doppelte Namen.",
    "Importing voice in background...": "Stimme wird im Hintergrund importiert...",
    "Downloading voice in background...": "Stimme wird im Hintergrund heruntergeladen...",
    "Failed to install voice.": "Installation der Stimme fehlgeschlagen.",
    "Failed to import voice.": "Import der Stimme fehlgeschlagen.",
}

def translate_string(english):
    """Translate an English string to German."""
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
             
        german = translate_string(english_text)
        if german:
            return f'{full_msgid_part}\nmsgstr "{german}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    # Write back
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
