#!/usr/bin/env python3
"""
Automated French translation for TuxTalks using gaming-specific glossary.
Enhances all .po files in the French locale.
"""

import re
import os
import sys

# Gaming-specific glossary (English -> French)
GAMING_GLOSSARY = {
    # UI Elements (general terms)
    "Settings": "Paramètres",
    "General": "Général",
    "Voice": "Voix",
    "Games": "Jeux",
    "Speech Engines": "Moteurs de parole",
    "Input": "Entrée",
    "Vocabulary": "Vocabulaire",
    "Help": "Aide",
    "Content Packs": "Packs de contenu",
    "Corrections": "Corrections",
    "Training": "Entraînement",
    "Player": "Lecteur",
    
    # Actions
    "Start Assistant": "Démarrer l'assistant",
    "Stop": "Arrêter",
    "Exit": "Quitter",
    "Save Config": "Enregistrer la conf",
    "Cancel": "Annuler",
    "Browse": "Parcourir",
    "Add": "Ajouter",
    "Edit": "Modifier",
    "Delete": "Supprimer",
    "Refresh": "Actualiser",
    "Clear": "Effacer",
    "New": "Nouveau",
    "Create": "Créer",
    "Remove": "Supprimer",
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
    "Bindings": "Raccourcis",
    "Binds": "Raccourcis",
    "Game Action": "Action de jeu",
    "Voice Command": "Commande vocale",
    "Mapped Key": "Touche assignée",
    "Process Name": "Nom du processus",
    "Binding Profile": "Profil de raccourcis",
    "Macro": "Macro",
    "Macros": "Macros",
    "Profile": "Profil",
    "Game Integration": "Intégration de jeu",
    "Runtime Status": "État d'exécution",
    "Runtime Environment": "Environnement d'exécution",
    "Custom Commands": "Commandes personnalisées",
    "Game Bindings": "Raccourcis de jeu",
    "Active Profile Bindings": "Raccourcis du profil actif",
    
    # Speech/Voice
    "Wake Word": "Mot d'activation",
    "Wake Word Settings": "Paramètres du mot d'activation",
    "Speech Recognition": "Reconnaissance vocale",
    "Speech Recognition (Vosk)": "Reconnaissance vocale (Vosk)",
    "Text-to-Speech": "Synthèse vocale",
    "Text-to-Speech (Piper)": "Synthèse vocale (Piper)",
    "Active Model": "Modèle actif",
    "Active Voice": "Voix active",
    "Voice Triggers": "Déclencheurs vocaux",
    "Voice Corrections": "Corrections vocales",
    "Voice Fingerprint": "Empreinte vocale",
    "Voice Learning": "Apprentissage vocal",
    "Voice Training": "Entraînement vocal",
    
    # UI Labels
    "Theme": "Thème",
    "Scale": "Échelle",
    "Filter": "Filtrer",
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
    "Game Type": "Type de jeu",
    "Game Name": "Nom du jeu",
    "Game Group": "Groupe de jeu",
    "Game Bindings File": "Fichier de raccourcis du jeu",
    "Bindings Path": "Chemin des raccourcis",
    "Bindings File Path": "Chemin du fichier de raccourcis",
    "Configuration Name": "Nom de la configuration",
    "Profile Name": "Nom du profil",
    "Macro Profile": "Profil de macro",
    "Defined Macros": "Macros définies",
    "Macro Steps": "Étapes de macro",
    "Delay": "Délai",
    "Action": "Action",
    "Key": "Touche",
    "Source": "Source",
    "Built-in": "Intégré",
    "Custom": "Personnalisé",
    "Pack": "Pack",
    
    # Wizard/Dialog
    "Add Game": "Ajouter un jeu",
    "Edit Game": "Modifier le jeu",
    "Remove Game": "Supprimer le jeu",
    "Add Bind": "Ajouter un raccourci",
    "Edit Bind": "Modifier le raccourci",
    "Remove Bind": "Supprimer le raccourci",
    "Default Binds": "Raccourcis par défaut",
    "Add Command": "Ajouter une commande",
    "Add Game Profile": "Ajouter un profil de jeu",
    "Create Profile": "Créer un profil",
    "Save Settings": "Enregistrer les paramètres",
    "Profile Settings": "Paramètres du profil",
    "Profile Configuration": "Configuration du profil",
    
    # Steps/Process
    "Step 1": "Étape 1",
    "Step 2": "Étape 2",
    "Step 3": "Étape 3",
    "Select Running Game Process": "Sélectionner le processus de jeu en cours",
    "Scan Processes": "Scanner les processus",
    "Scan Results": "Résultats du scan",
    "Command Line": "Ligne de commande",
    "Command Line / Path": "Ligne de commande / Chemin",
    
    # Specific Actions
    "Enable Game Integration": "Activer l'intégration du jeu",
    "Modify Trigger": "Modifier le déclencheur",
    "Clear Trigger": "Effacer le déclencheur",
    "Delete Selected": "Supprimer la sélection",
    "Clear All": "Tout effacer",
    "Use Selected": "Utiliser la sélection",
    "Restore Defaults": "Restaurer les paramètres par défaut",
    "Import Defaults": "Importer les paramètres par défaut",
    
    # Voice/Audio
    "Wake Word:": "Mot d'activation :",
    "Active Model:": "Modèle actif :",
    "Active Voice:": "Voix active :",
    "Browse Folder": "Parcourir le dossier",
    "Download from URL": "Télécharger depuis une URL",
    "Delete Voice": "Supprimer la voix",
    "Import New Voice": "Importer une nouvelle voix",
    "Load from File (.onnx)": "Charger depuis un fichier (.onnx)",
    
    # Correction/Training
    "When I hear...": "Quand j'entends...",
    "I should understand...": "Je devrais comprendre...",
    "Test & Train": "Tester et entraîner",
    "Record": "Enregistrer",
    "Dur:": "Duré :",
    "Add as Correction": "Ajouter comme correction",
    "Targeted Train": "Entraînement ciblé",
    "Basic": "Basique",
    "Advanced": "Avancé",
    "Recent Ignored/Missed Commands": "Commandes ignorées/manquées récentes",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Appuyez sur la combinaison de touches de votre clavier :",
    "(Example: Ctrl + Alt + H)": "(Exemple : Ctrl + Alt + H)",
    "Clear": "Effacer",
    "Capture": "Capturer",
    "Key to Press:": "Touche à presser :",
    "Modifiers:": "Modificateurs :",
    
    # Game-Specific
    "Game Integration Status": "État de l'intégration du jeu",
    "Game:": "Jeu :",
    "Binds:": "Raccourcis :",
    "Macro Profile:": "Profil de macro :",
    "Runtime Status:": "État d'exécution :",
    "Profile Name (Variant):": "Nom du profil (variante) :",
    "Binding Profile Name:": "Nom du profil de raccourcis :",
    "Bindings File Path (Optional):": "Chemin du fichier de raccourcis (optionnel) :",
    "Process Name (e.g. X4.exe):": "Nom du processus (ex: X4.exe) :",
    "Game Type:": "Type de jeu :",
    "Game Name:": "Nom du jeu :",
    "Process Name:": "Nom du processus :",
    "Runtime Environment:": "Environnement d'exécution :",
    
    # Advanced Features
    "External Audio Assets": "Ressources audio externes",
    "Audio Directory:": "Répertoire audio :",
    "Reference File": "Fichier de référence",
    "Sound Pool": "Banque de sons",
    "Playback Mode": "Mode de lecture",
    "Random": "Aléatoire",
    "Simultaneous": "Simultané",
    "Sequential": "Séquentiel",
    "Round-Robin": "Rotation",
    
    # Common long phrases
    "Advanced Voice Control for Linux": "Contrôle vocal avancé pour Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Push-to-Talk",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "OK",
    "Ctrl": "Ctrl",
    "Alt": "Alt",
    "Shift": "Maj",
    
    # Wizard setup
    "TuxTalks First-Run Setup": "Configuration initiale de TuxTalks",
    "Welcome to TuxTalks! 🐧": "Bienvenue sur TuxTalks ! 🐧",
    "TuxTalks is your powerful, secure, and offline voice command assistant for Linux gaming.\n\nThis wizard will help you set up your core preferences in just a few minutes so you can start talking to your favorite games and media players.": "TuxTalks est votre assistant de commande vocale puissant, sécurisé et hors ligne pour le jeu sur Linux.\n\nCet assistant vous aidera à configurer vos préférences de base en quelques minutes afin que vous puissiez commencer à parler à vos jeux et lecteurs multimédia préférés.",
    "Ready to begin?": "Prêt à commencer ?",
    "Step 1: Interface Language": "Étape 1 : Langue de l'interface",
    "Select the language for the TuxTalks interface:": "Sélectionnez la langue de l'interface TuxTalks :",
    "Note: RTL support is automatically enabled for Arabic.": "Note : Le support RTL est automatiquement activé pour l'arabe.",
    "Step 2: Voice Recognition (ASR)": "Étape 2 : Reconnaissance vocale (ASR)",
    "To process your voice offline, TuxTalks needs a language model.\n\nBased on your language selection, we recommend the following model:": "Pour traiter votre voix hors ligne, TuxTalks a besoin d'un modèle linguistique.\n\nSur la base de votre sélection de langue, nous recommandons le modèle suivant :",
    "Download & Install": "Télécharger et installer",
    "Step 3: Initial Integration": "Étape 3 : Intégration initiale",
    "Choose your primary media player:": "Choisissez votre lecteur multimédia principal :",
    "Tip: You can change this and add games later in the main settings.": "Astuce : Vous pouvez changer cela et ajouter des jeux plus tard dans les paramètres principaux.",
    "All Set! 🎉": "Tout est prêt ! 🎉",
    "Setup is complete. TuxTalks is now configured with your language and voice preferences.\n\nClick 'Finish' to open the main settings where you can further customize your experience, add games, and calibrate your microphone.": "La configuration est terminée. TuxTalks est maintenant configuré avec vos préférences de langue et de voix.\n\nCliquez sur 'Terminer' pour ouvrir les paramètres principaux où vous pourrez personnaliser davantage votre expérience, ajouter des jeux et calibrer votre microphone.",
    "Skip Setup?": "Passer la configuration ?",
    "Closing this window will skip the setup wizard. You can still configure everything manually in the settings.\n\nSkip and don't show again?": "Fermer cette fenêtre fera passer l'assistant de configuration. Vous pouvez toujours tout configurer manuellement dans les paramètres.\n\nPasser et ne plus afficher ?",
}

# Sentence fragments/phrases
PHRASES = {
    "Configuration saved.": "Configuration enregistrée.",
    "TuxTalks is already running.": "TuxTalks est déjà en cours d'exécution.",
    "Unsaved Changes": "Modifications non enregistrées",
    "You have unsaved changes. Save before starting?": "Vous avez des modifications non enregistrées. Enregistrer avant de démarrer ?",
    "Assistant stopped.": "Assistant arrêté.",
    "Please select a game first.": "Veuillez d'abord sélectionner un jeu.",
    "No game selected.": "Aucun jeu sélectionné.",
    "Profile name cannot be empty.": "Le nom du profil ne peut pas être vide.",
    "Failed to create macro profile.": "Échec de la création du profil de macro.",
    "Failed to delete macro profile.": "Échec de la suppression du profil de macro.",
    "Failed to rename macro profile.": "Échec du renommage du profil de macro.",
    "No profile selected.": "Aucun profil sélectionné.",
    "Process Name required.": "Nom du processus requis.",
    "Select a row to delete.": "Sélectionnez une ligne à supprimer.",
    "Delete selected correction?": "Supprimer la correction sélectionnée ?",
    "Perfect match! No training needed.": "Correspondance parfaite ! Aucun entraînement requis.",
    "Correction added.": "Correction ajoutée.",
    "Test a phrase first.": "Testez d'abord une phrase.",
    "Scaling saved. Restart required for full effect.": "Échelle enregistrée. Redémarrage requis pour un effet complet.",
    "All detected game actions typically have voice commands assigned!\nYou can still edit existing ones.": "Toutes les actions de jeu détectées ont généralement des commandes vocales assignées !\nVous pouvez toujours modifier les commandes existantes.",
    "Please select a Game grouping first.": "Veuillez d'abord sélectionner un groupe de jeux.",
    "Internal Error: Active bindings path is unknown.": "Erreur interne : le chemin des raccourcis actifs est inconnu.",
    "Select an action to rebind.": "Sélectionnez une action à réassigner.",
    "No profiles found in this group.": "Aucun profil trouvé dans ce groupe.",
    "No standard binding files found for this game type.": "Aucun fichier de raccourcis standard trouvé pour ce type de jeu.",
    "Failed to remove profiles.": "Échec de la suppression des profils.",
    "Name already taken.": "Ce nom est déjà pris.",
    "No profiles found. (Check console for path/parsing errors)": "Aucun profil trouvé. (Consultez la console pour les erreurs de chemin/analyse)",
    "Import Complete": "Importation terminée",
    "No profiles found.": "Aucun profil trouvé.",
    "Elite Dangerous appears to be running.\n\nChanges made now may NOT take effect immediately or could be overwritten by the game.\n\nContinue anyway?": "Elite Dangerous semble être en cours d'exécution.\n\nLes modifications apportées maintenant peuvent NE PAS prendre effet immédiatement ou pourraient être écrasées par le jeu.\n\nContinuer quand même ?",
    "Scan and import standard Elite Dangerous ControlSchemes?\nThis may double up profiles if you already have them, but skips duplicate names.": "Scanner et importer les ControlSchemes standard d'Elite Dangerous ?\nCela peut doubler les profils si vous les avez déjà, mais ignore les noms en double.",
    "Importing voice in background...": "Importation de la voix en arrière-plan...",
    "Downloading voice in background...": "Téléchargement de la voix en arrière-plan...",
    "Failed to install voice.": "Échec de l'installation de la voix.",
    "Failed to import voice.": "Échec de l'importation de la voix.",
}

def translate_string(english):
    """Translate an English string to French."""
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
            return f"{GAMING_GLOSSARY[base]} :"
        
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
             
        french = translate_string(english_text)
        if french:
            return f'{full_msgid_part}\nmsgstr "{french}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    # Write back
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
