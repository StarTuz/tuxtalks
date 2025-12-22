#!/usr/bin/env python3
"""
French translation for TuxTalks using gaming-specific glossary.
"""

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
    
    # Actions
    "Start Assistant": "Démarrer l'Assistant",
    "Stop": "Arrêter",
    "Exit": "Quitter",
    "Save Config": "Enregistrer Config",
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
    
    # Speech/Voice
    "Wake Word": "Mot d'Activation",
    "Speech Recognition": "Reconnaissance Vocale",
    "Text-to-Speech": "Synthèse Vocale",
    "Active Model": "Modèle Actif",
    "Active Voice": "Voix Active",
    "Voice Triggers": "Déclencheurs Vocaux",
    "Voice Corrections": "Corrections Vocales",
    
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
    "Downloading": "Téléchargement",
    "Importing": "Importation",
    
    # Common UI
    "Theme": "Thème",
    "Scale": "Échelle",
    "Filter": "Filtre",
    "Search": "Rechercher",
    "Advanced Voice Control for Linux": "Contrôle Vocal Avancé pour Linux",
}

def translate_to_french(po_file):
    """Apply French translations to .po file."""
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('msgid "'):
            msgid = line.split('msgid "')[1].rstrip('"\n')
            msgstr_line = lines[i + 1] if i + 1 < len(lines) else 'msgstr ""\n'
            
            if msgid and msgid in FRENCH_GLOSSARY:
                french = FRENCH_GLOSSARY[msgid]
                msgstr_line = f'msgstr "{french}"\n'
            
            output.append(line)
            output.append(msgstr_line)
            i += 2
        else:
            output.append(line)
            i += 1
    
    with open(po_file, 'w', encoding='utf-8') as f:
        f.writelines(output)
    
    print(f"✓ French translations applied to {po_file}")

if __name__ == '__main__':
    import sys
    po_file = sys.argv[1] if len(sys.argv) > 1 else 'locale/fr/LC_MESSAGES/tuxtalks.po'
    translate_to_french(po_file)
    print(f"Translated {len(FRENCH_GLOSSARY)} terms")
