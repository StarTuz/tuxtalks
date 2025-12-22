#!/usr/bin/env python3
"""
Automated Spanish translation for Tux Talks using gaming-specific glossary.
This creates translations for the extracted .po file.
"""

import re

# Gaming-specific glossary (English -> Spanish)
GAMING_GLOSSARY = {
    # UI El (general terms)
    "Settings": "Configuración",
    "General": "General",
    "Voice": "Voz",
    "Games": "Juegos",
    "Speech Engines": "Motores de Voz",
    "Input": "Entrada",
    "Vocabulary": "Vocabulario",
    "Help": "Ayuda",
    "Content Packs": "Paquetes de Contenido",
    "Corrections": "Correcciones",
    
    # Actions
    "Start Assistant": "Iniciar Asistente",
    "Stop": "Detener",
    "Exit": "Salir",
    "Save Config": "Guardar Configuración",
    "Cancel": "Cancelar",
    "Browse": "Examinar",
    "Add": "Agregar",
    "Edit": "Editar",
    "Delete": "Eliminar",
    "Refresh": "Actualizar",
    "Clear": "Limpiar",
    "New": "Nuevo",
    "Create": "Crear",
    "Remove": "Eliminar",
    "Import": "Importar",
    "Export": "Exportar",
    "Backup": "Copia de seguridad",
    "Restore": "Restaurar",
    "Test": "Probar",
    "Run": "Ejecutar",
    "Save": "Guardar",
    "Apply": "Aplicar",
   
    # Gaming Terms
    "Bindings": "Asignaciones",
    "Binds": "Asignaciones",
    "Game Action": "Acción del Juego",
    "Voice Command": "Comando de Voz",
    "Mapped Key": "Tecla Asignada",
    "Process Name": "Nombre del Proceso",
    "Binding Profile": "Perfil de Asignaciones",
    "Macro": "Macro",
    "Macros": "Macros",
    "Profile": "Perfil",
    "Game Integration": "Integración de Juego",
    "Runtime Status": "Estado de Ejecución",
    "Runtime Environment": "Entorno de Ejecución",
    
    # Speech/Voice
    "Wake Word": "Palabra de Activación",
    "Speech Recognition": "Reconocimiento de Voz",
    "Text-to-Speech": "Texto a Voz",
    "Active Model": "Modelo Activo",
    "Active Voice": "Voz Activa",
    "Voice Triggers": "Activadores de Voz",
    "Voice Corrections": "Correcciones de Voz",
    
    # Status messages
    "Saved": "Guardado",
    "Success": "Éxito",
    "Error": "Error",
    "Info": "Información",
    "Warning": "Advertencia",
    "Complete": "Completado",
    "Failed": "Falló",
    "Stopped": "Detenido",
    "Downloaded": "Descargado",
    "Downloading": "Descargando",
    "Importing": "Importando",
    
    # Common UI elements
    "Theme": "Tema",
    "Scale": "Escala",
    "Filter": "Filtro",
    "Search": "Buscar",
    "Advanced Voice Control for Linux": "Control de Voz Avanzado para Linux",
    "TuxTalks": "TuxTalks",
    
    # Specific features
    "Push-to-Talk": "Pulsar para Hablar",
    "PTT": "PPH",
    "Enable Game Integration": "Habilitar Integración de Juegos",
    "Macro Steps": "Pasos de Macro",
    "Delay": "Retraso",
    "Action": "Acción",
    "Key": "Tecla",
    "Source": "Origen",
}

# Sentence fragments/phrases
PHRASES = {
    "Configuration saved.": "Configuración guardada.",
    "TuxTalks is already running.": "TuxTalks ya está en ejecución.",
    "Unsaved Changes": "Cambios No Guardados",
    "You have unsaved changes. Save before starting?": "Tienes cambios sin guardar. ¿Guardar antes de iniciar? ",
    "Assistant stopped.": "Asistente detenido.",
    "Please select a game first.": "Por favor, selecciona un juego primero.",
    "No game selected.": "Ningún juego seleccionado",
    "Profile name cannot be empty.": "El nombre de perfil no puede estar vacío.",
    "Failed to create macro profile.": "Error al crear perfil de macro.",
    "Failed to delete macro profile.": "Error al eliminar perfil de macro.",
    "Failed to rename macro profile.": "Error al renombrar perfil de macro.",
    "No profile selected.": "Ningún perfil seleccionado.",
    "Process Name required.": "Nombre de proceso requerido.",
    "Select a row to delete.": "Selecciona una fila para eliminar.",
    "Delete selected correction?": "¿Eliminar corrección seleccionada?",
    "Perfect match! No training needed.": "¡Coincidencia perfecta! No se necesita entrenamiento.",
    "Correction added.": "Corrección agregada.",
    "Test a phrase first.": "Prueba una frase primero.",
}

def translate_string(english):
    """Translate an English string to Spanish."""
    # Direct match
    if english in GAMING_GLOSSARY:
        return GAMING_GLOSSARY[english]
    if english in PHRASES:
        return PHRASES[english]
    
    # Check for close matches (trim spaces)
    trimmed = english.strip()
    if trimmed != english and trimmed in GAMING_GLOSSARY:
        return GAMING_GLOSSARY[trimmed]
    
    # Don't translate emojis, symbols, technical terms
    if not any(c.isalpha() for c in english):
        return english
    
    if english in ["PID", "UTF-8", "PTT", "X4", "TuxTalks"]:
        return english
    
    # Return empty for now - manual translation needed
    return ""

def auto_translate_po(filepath):
    """Automatically translate a .po file with our glossary."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    output_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Find msgid lines
        if line.startswith('msgid "') and i + 1 < len(lines):
            msgid_line = line
            msgstr_line = lines[i + 1]
            
            # Extract English text
            match = re.search(r'msgid "(.*)"', msgid_line)
            if match:
                english_text = match.group(1)
                
                # Skip empty msgid
                if english_text:
                    spanish = translate_string(english_text)
                    
                    if spanish:
                        # Replace msgstr
                        msgstr_line = f'msgstr "{spanish}"'
            
            output_lines.append(msgid_line)
            output_lines.append(msgstr_line)
            i += 2
        else:
            output_lines.append(line)
            i += 1
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"✓ Auto-translated {filepath}")
    print("\nNote: Some strings need manual translation.")
    print("Please review locale/es/LC_MESSAGES/messages.po")

if __name__ == '__main__':
    import sys
    import os
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    po_file = os.path.join(script_dir, 'locale/es/LC_MESSAGES/messages.po')
    
    if os.path.exists(po_file):
        auto_translate_po(po_file)
        print("\nNext steps:")
        print("1. Review translations: less locale/es/LC_MESSAGES/messages.po")
        print("2. Compile: pybabel compile -d locale")
        print("3. Test: Set UI_LANGUAGE=es in config, run launcher")
    else:
        print(f"Error: {po_file} not found")
        sys.exit(1)
