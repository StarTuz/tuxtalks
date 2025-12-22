#!/usr/bin/env python3
"""
Automated French translation for TuxTalks using gaming-specific glossary.
"""

import re
import os
import sys

# French Gaming Glossary (English -> French)
FRENCH_GLOSSARY = {
    # UI Elements
    "Settings": "Paramètres",
    "General": "Général",
    "Voice": "Voix",
    "Games": "Jeux",
    "Speech Engines": "Moteurs Vocaux",
    "Input": "Entrée",
    "Vocabulary": "Vocabulaire",
    "Help": "Aide",
    "Content Packs": "Packs de Contenu",
    "Corrections": "Corrections",
    "Training": "Entraînement",
    "Player": "Lecteur",
    
    # Actions
    "Start Assistant": "Démarrer l'Assistant",
    "Stop": "Arrêter",
    "Exit": "Quitter",
    "Save Config": "Enregistrer la Config",
    "Cancel": "Annuler",
    "Browse": "Parcourir",
    "Add": "Ajouter",
    "Edit": "Modifier",
    "Delete": "Supprimer",
    "Refresh": "Actualiser",
    "Clear": "Effacer",
    "New": "Nouveau",
    "Create": "Créer",
    "Remove": "Retirer",
    "Import": "Importer",
    "Export": "Exporter",
    "Backup": "Sauvegarde",
    "Restore": "Restaurer",
    "Test": "Tester",
    "Run": "Exécuter",
    "Save": "Enregistrer",
    "Apply": "Appliquer",
    "OK": "OK",
    "Yes": "Oui",
    "No": "Non",
    "Close": "Fermer",
    "Continue": "Continuer",
    
    # Gaming Terms
    "Bindings": "Affectations",
    "Binds": "Affectations",
    "Game Action": "Action de Jeu",
    "Voice Command": "Commande Vocale",
    "Mapped Key": "Touche Assignée",
    "Process Name": "Nom du Processus",
    "Binding Profile": "Profil d'Affectation",
    "Macro": "Macro",
    "Macros": "Macros",
    "Profile": "Profil",
    "Game Integration": "Intégration Jeu",
    "Runtime Status": "Statut d'Exécution",
    "Runtime Environment": "Environnement d'Exécution",
    "Custom Commands": "Commandes Personnalisées",
    "Game Bindings": "Raccourcis de Jeu",
    "Active Profile Bindings": "Affectations du Profil Actif",
    
    # Speech/Voice
    "Wake Word": "Mot d'Activation",
    "Wake Word Settings": "Paramètres du Mot d'Activation",
    "Speech Recognition": "Reconnaissance Vocale",
    "Speech Recognition (Vosk)": "Reconnaissance Vocale (Vosk)",
    "Text-to-Speech": "Synthèse Vocale",
    "Text-to-Speech (Piper)": "Synthèse Vocale (Piper)",
    "Active Model": "Modèle Actif",
    "Active Voice": "Voix Active",
    "Voice Triggers": "Déclencheurs Vocaux",
    "Voice Corrections": "Corrections Vocales",
    "Voice Fingerprint": "Empreinte Vocale",
    "Voice Learning": "Apprentissage Vocal",
    "Voice Training": "Entraînement Vocal",
    
    # UI Labels
    "Theme": "Thème",
    "Scale": "Échelle",
    "Filter": "Filtre",
    "Search": "Rechercher",
    "Name": "Nom",
    "Description": "Description",
    "Path": "Chemin",
    "File": "Fichier",
    "Folder": "Dossier",
    "Directory": "Répertoire",
    "Configuration": "Configuration",
    "Options": "Options",
    "Preferences": "Préférences",
    
    # Status messages
    "Saved": "Enregistré",
    "Success": "Succès",
    "Error": "Erreur",
    "Info": "Info",
    "Warning": "Avertissement",
    "Complete": "Terminé",
    "Failed": "Échoué",
    "Stopped": "Arrêté",
    "Downloaded": "Téléchargé",
    "Downloading": "Téléchargement en cours",
    "Importing": "Importation en cours",
    "Loading": "Chargement en cours",
    "Processing": "Traitement en cours",
    "Ready": "Prêt",
    "Running": "En cours d'exécution",
    
    # Game Integration Specific
    "Game": "Jeu",
    "Game Type": "Type de Jeu",
    "Game Name": "Nom du Jeu",
    "Game Group": "Groupe de Jeu",
    "Game Bindings File": "Fichier de Raccourcis de Jeu",
    "Bindings Path": "Chemin des Raccourcis",
    "Bindings File Path": "Chemin du Fichier de Raccourcis",
    "Configuration Name": "Nom de la Configuration",
    "Profile Name": "Nom du Profil",
    "Macro Profile": "Profil de Macro",
    "Defined Macros": "Macros Définies",
    "Macro Steps": "Étapes de Macro",
    "Delay": "Délai",
    "Action": "Action",
    "Key": "Touche",
    "Source": "Source",
    "Built-in": "Intégré",
    "Custom": "Personnalisé",
    "Pack": "Pack",
    
    # Wizard/Dialog
    "Add Game": "Ajouter un Jeu",
    "Edit Game": "Modifier le Jeu",
    "Remove Game": "Supprimer le Jeu",
    "Add Bind": "Ajouter un Raccourci",
    "Edit Bind": "Modifier le Raccourci",
    "Remove Bind": "Supprimer le Raccourci",
    "Default Binds": "Raccourcis par Défaut",
    "Add Command": "Ajouter une Commande",
    "Add Game Profile": "Ajouter un Profil de Jeu",
    "Create Profile": "Créer un Profil",
    "Save Settings": "Enregistrer Paramètres",
    "Profile Settings": "Paramètres de Profil",
    "Profile Configuration": "Configuration de Profil",
    
    # Steps/Process
    "Step 1": "Étape 1",
    "Step 2": "Étape 2",
    "Step 3": "Étape 3",
    "Select Running Game Process": "Sélectionner un Processus de Jeu en Cours",
    "Scan Processes": "Analyser les Processus",
    "Scan Results": "Résultats de l'Analyse",
    "Command Line": "Ligne de Commande",
    "Command Line / Path": "Ligne de Commande / Chemin",
    
    # Specific Actions
    "Enable Game Integration": "Activer l'Intégration Jeu",
    "Modify Trigger": "Modifier le Déclencheur",
    "Clear Trigger": "Effacer le Déclencheur",
    "Delete Selected": "Supprimer Sélection",
    "Clear All": "Tout Effacer",
    "Use Selected": "Utiliser Sélection",
    "Restore Defaults": "Restaurer les Défauts",
    "Import Defaults": "Importer les Défauts",
    
    # Voice/Audio
    "Wake Word:": "Mot d'Activation :",
    "Active Model:": "Modèle Actif :",
    "Active Voice:": "Voix Active :",
    "Browse Folder": "Parcourir Dossier",
    "Download from URL": "Télécharger depuis URL",
    "Delete Voice": "Supprimer la Voix",
    "Import New Voice": "Importer Nouvelle Voix",
    "Load from File (.onnx)": "Charger depuis Fichier (.onnx)",
    
    # Correction/Training
    "When I hear...": "Quand j'entends...",
    "I should understand...": "Je devrais comprendre...",
    "Test & Train": "Tester & Entraîner",
    "Record": "Enregistrer",
    "Dur:": "Duré :",
    "Add as Correction": "Ajouter comme Correction",
    "Targeted Train": "Entraînement Ciblé",
    "Basic": "Basique",
    "Advanced": "Avancé",
    "Recent Ignored/Missed Commands": "Commandes Récemment Ignorées/Manquées",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Appuyez sur la combinaison de touches sur votre clavier :",
    "(Example: Ctrl + Alt + H)": "(Exemple : Ctrl + Alt + H)",
    "Clear": "Effacer",
    "Capture": "Capturer",
    "Key to Press:": "Touche à Appuyer :",
    "Modifiers:": "Modificateurs :",
    
    # Game-Specific
    "Game Integration Status": "Statut de l'Intégration Jeu",
    "Game:": "Jeu :",
    "Binds:": "Raccourcis :",
    "Macro Profile:": "Profil de Macro :",
    "Runtime Status:": "Statut d'Exécution :",
    "Profile Name (Variant):": "Nom du Profil (Variante) :",
    "Binding Profile Name:": "Nom du Profil de Raccourci :",
    "Bindings File Path (Optional):": "Chemin du Fichier de Raccourcis (Optionnel) :",
    "Process Name (e.g. X4.exe):": "Nom du Processus (ex: X4.exe) :",
    "Game Type:": "Type de Jeu :",
    "Game Name:": "Nom du Jeu :",
    "Process Name:": "Nom du Processus :",
    "Runtime Environment:": "Environnement d'Exécution :",
    
    # Advanced Features
    "External Audio Assets": "Ressources Audio Externes",
    "Audio Directory:": "Répertoire Audio :",
    "Reference File": "Fichier de Référence",
    "Sound Pool": "Groupe de Sons",
    "Playback Mode": "Mode de Lecture",
    "Random": "Aléatoire",
    "Simultaneous": "Simultané",
    "Sequential": "Séquentiel",
    "Round-Robin": "Alternance",
    
    # Common long phrases (abbreviated)
    "Advanced Voice Control for Linux": "Contrôle Vocal Avancé pour Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Appuyer pour Parler",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "OK",
    "Ctrl": "Ctrl",
    "Alt": "Alt",
    "Shift": "Maj",
    
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
    "Configuration saved.": "Configuration enregistrée.",
    "TuxTalks is already running.": "TuxTalks est déjà en cours d'exécution.",
    "Unsaved Changes": "Changements non enregistrés",
    "You have unsaved changes. Save before starting?": "Vous avez des changements non enregistrés. Enregistrer avant de démarrer ?",
    "Assistant stopped.": "Assistant arrêté.",
    "Please select a game first.": "Veuillez d'abord sélectionner un jeu.",
    "No game selected.": "Aucun jeu sélectionné.",
    "Profile name cannot be empty.": "Le nom du profil ne peut pas être vide.",
    "Failed to create macro profile.": "Échec de la création du profil de macro.",
    "Failed to delete macro profile.": "Échec de la suppression du profil de macro.",
    "Failed to rename macro profile.": "Échec du changement de nom du profil de macro.",
    "No profile selected.": "Aucun profil sélectionné.",
    "Process Name required.": "Nom du processus requis.",
    "Select a row to delete.": "Sélectionnez une ligne à supprimer.",
    "Delete selected correction?": "Supprimer la correction sélectionnée ?",
    "Perfect match! No training needed.": "Correspondance parfaite ! Aucun entraînement nécessaire.",
    "Correction added.": "Correction ajoutée.",
    "Test a phrase first.": "Testez d'abord une phrase.",
}

def translate_string(english):
    """Translate an English string to French."""
    if english in FRENCH_GLOSSARY:
        return FRENCH_GLOSSARY[english]
    if english in PHRASES:
        return PHRASES[english]
    
    trimmed = english.strip()
    if trimmed != english and trimmed in FRENCH_GLOSSARY:
        return FRENCH_GLOSSARY[trimmed]
    if trimmed != english and trimmed in PHRASES:
        return PHRASES[trimmed]
    
    if english.endswith(':'):
        base = english[:-1].strip()
        if base in FRENCH_GLOSSARY:
            return f"{FRENCH_GLOSSARY[base]} :"
        
    if english.endswith('...'):
        base = english[:-3].strip()
        if base in FRENCH_GLOSSARY:
            return f"{FRENCH_GLOSSARY[base]}..."

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
             
        french = translate_string(english_text)
        if french:
            return f'{full_msgid_part}\nmsgstr "{french}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Auto-translated {filepath}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fr_dir = os.path.join(script_dir, 'locale/fr/LC_MESSAGES/')
    
    if os.path.exists(fr_dir):
        for filename in os.listdir(fr_dir):
            if filename.endswith('.po'):
                auto_translate_po(os.path.join(fr_dir, filename))
        
        print("\nNext steps:")
        print("1. Review translations in locale/fr/LC_MESSAGES/")
        print("2. Compile: pybabel compile -d locale")
    else:
        print(f"Error: {fr_dir} not found")
        sys.exit(1)
