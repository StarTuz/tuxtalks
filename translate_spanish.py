#!/usr/bin/env python3
"""
Automated Spanish translation for TuxTalks using gaming-specific glossary.
Enhances all .po files in the Spanish locale.
"""

import re
import os
import sys

# Gaming-specific glossary (English -> Spanish)
GAMING_GLOSSARY = {
    # UI Elements (general terms)
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
    "Training": "Entrenamiento",
    "Player": "Reproductor",
    
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
    "OK": "Aceptar",
    "Yes": "Sí",
    "No": "No",
    "Close": "Cerrar",
    "Continue": "Continuar",
    
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
    "Custom Commands": "Comandos Personalizados",
    "Game Bindings": "Asignaciones de Juego",
    "Active Profile Bindings": "Asignaciones del Perfil Activo",
    
    # Speech/Voice
    "Wake Word": "Palabra de Activación",
    "Wake Word Settings": "Configuración de Palabra de Activación",
    "Speech Recognition": "Reconocimiento de Voz",
    "Speech Recognition (Vosk)": "Reconocimiento de Voz (Vosk)",
    "Text-to-Speech": "Texto a Voz",
    "Text-to-Speech (Piper)": "Texto a Voz (Piper)",
    "Active Model": "Modelo Activo",
    "Active Voice": "Voz Activa",
    "Voice Triggers": "Activadores de Voz",
    "Voice Corrections": "Correcciones de Voz",
    "Voice Fingerprint": "Huella de Voz",
    "Voice Learning": "Aprendizaje de Voz",
    "Voice Training": "Entrenamiento de Voz",
    
    # UI Labels
    "Theme": "Tema",
    "Scale": "Escala",
    "Filter": "Filtro",
    "Search": "Buscar",
    "Name": "Nombre",
    "Description": "Descripción",
    "Path": "Ruta",
    "File": "Archivo",
    "Folder": "Carpeta",
    "Directory": "Directorio",
    "Configuration": "Configuración",
    "Options": "Opciones",
    "Preferences": "Preferencias",
    
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
    "Loading": "Cargando",
    "Processing": "Procesando",
    "Ready": "Listo",
    "Running": "Ejecutando",
    
    # Game Integration Specific
    "Game": "Juego",
    "Game Type": "Tipo de Juego",
    "Game Name": "Nombre del Juego",
    "Game Group": "Grupo de Juego",
    "Game Bindings File": "Archivo de Asignaciones del Juego",
    "Bindings Path": "Ruta de Asignaciones",
    "Bindings File Path": "Ruta del Archivo de Asignaciones",
    "Configuration Name": "Nombre de Configuración",
    "Profile Name": "Nombre de Perfil",
    "Macro Profile": "Perfil de Macros",
    "Defined Macros": "Macros Definidas",
    "Macro Steps": "Pasos de Macro",
    "Delay": "Retraso",
    "Action": "Acción",
    "Key": "Tecla",
    "Source": "Origen",
    "Built-in": "Integrado",
    "Custom": "Personalizado",
    "Pack": "Paquete",
    
    # Wizard/Dialog
    "Add Game": "Agregar Juego",
    "Edit Game": "Editar Juego",
    "Remove Game": "Eliminar Juego",
    "Add Bind": "Agregar Asignación",
    "Edit Bind": "Editar Asignación",
    "Remove Bind": "Eliminar Asignación",
    "Default Binds": "Asignaciones Predeterminadas",
    "Add Command": "Agregar Comando",
    "Add Game Profile": "Agregar Perfil de Juego",
    "Create Profile": "Crear Perfil",
    "Save Settings": "Guardar Configuración",
    "Profile Settings": "Configuración de Perfil",
    "Profile Configuration": "Configuración de Perfil",
    
    # Steps/Process
    "Step 1": "Paso 1",
    "Step 2": "Paso 2",
    "Step 3": "Paso 3",
    "Select Running Game Process": "Seleccionar Proceso de Juego en Ejecución",
    "Scan Processes": "Escanear Procesos",
    "Scan Results": "Resultados del Escaneo",
    "Command Line": "Línea de Comandos",
    "Command Line / Path": "Línea de Comandos / Ruta",
    
    # Specific Actions
    "Enable Game Integration": "Habilitar Integración de Juegos",
    "Modify Trigger": "Modificar Activador",
    "Clear Trigger": "Limpiar Activador",
    "Delete Selected": "Eliminar Seleccionado",
    "Clear All": "Limpiar Todo",
    "Use Selected": "Usar Seleccionado",
    "Restore Defaults": "Restaurar Predeterminados",
    "Import Defaults": "Importar Predeterminados",
    
    # Voice/Audio
    "Wake Word:": "Palabra de Activación:",
    "Active Model:": "Modelo Activo:",
    "Active Voice:": "Voz Activa:",
    "Browse Folder": "Explorar Carpeta",
    "Download from URL": "Descargar desde URL",
    "Delete Voice": "Eliminar Voz",
    "Import New Voice": "Importar Nueva Voz",
    "Load from File (.onnx)": "Cargar desde Archivo (.onnx)",
    
    # Correction/Training
    "When I hear...": "Cuando escucho...",
    "I should understand...": "Debería entender...",
    "Test & Train": "Probar y Entrenar",
    "Record": "Grabar",
    "Dur:": "Dur:",
    "Add as Correction": "Agregar como Corrección",
    "Targeted Train": "Entrenamiento Dirigido",
    "Basic": "Básico",
    "Advanced": "Avanzado",
    "Recent Ignored/Missed Commands": "Comandos Recientes Ignorados/Perdidos",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Presiona la combinación de teclas en tu teclado:",
    "(Example: Ctrl + Alt + H)": "(Ejemplo: Ctrl + Alt + H)",
    "Clear": "Limpiar",
    "Capture": "Capturar",
    "Key to Press:": "Tecla a Presionar:",
    "Modifiers:": "Modificadores:",
    
    # Game-Specific
    "Game Integration Status": "Estado de Integración de Juego",
    "Game:": "Juego:",
    "Binds:": "Asignaciones:",
    "Macro Profile:": "Perfil de Macros:",
    "Runtime Status:": "Estado de Ejecución:",
    "Profile Name (Variant):": "Nombre de Perfil (Variante):",
    "Binding Profile Name:": "Nombre de Perfil de Asignaciones:",
    "Bindings File Path (Optional):": "Ruta del Archivo de Asignaciones (Opcional):",
    "Process Name (e.g. X4.exe):": "Nombre del Proceso (ej. X4.exe):",
    "Game Type:": "Tipo de Juego:",
    "Game Name:": "Nombre del Juego:",
    "Process Name:": "Nombre del Proceso:",
    "Runtime Environment:": "Entorno de Ejecución:",
    
    # Advanced Features
    "External Audio Assets": "Recursos de Audio Externos",
    "Audio Directory:": "Directorio de Audio:",
    "Reference File": "Archivo de Referencia",
    "Sound Pool": "Grupo de Sonidos",
    "Playback Mode": "Modo de Reproducción",
    "Random": "Aleatorio",
    "Simultaneous": "Simultáneo",
    "Sequential": "Secuencial",
    "Round-Robin": "Rotativo",
    
    # Common long phrases (abbreviated)
    "Advanced Voice Control for Linux": "Control de Voz Avanzado para Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Pulsar para Hablar",
    "PTT": "PPH",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "Aceptar",
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

# Sentence fragments/phrases
PHRASES = {
    "Configuration saved.": "Configuración guardada.",
    "TuxTalks is already running.": "TuxTalks ya está en ejecución.",
    "Unsaved Changes": "Cambios no guardados",
    "You have unsaved changes. Save before starting?": "¿Tiene cambios sin guardar. ¿Guardar antes de iniciar?",
    "Assistant stopped.": "Asistente detenido.",
    "Please select a game first.": "Por favor, seleccione un juego primero.",
    "No game selected.": "Ningún juego seleccionado.",
    "Profile name cannot be empty.": "El nombre del perfil no puede estar vacío.",
    "Failed to create macro profile.": "Error al crear el perfil de macro.",
    "Failed to delete macro profile.": "Error al eliminar el perfil de macro.",
    "Failed to rename macro profile.": "Error al renombrar el perfil de macro.",
    "No profile selected.": "Ningún perfil seleccionado.",
    "Process Name required.": "Nombre de proceso requerido.",
    "Select a row to delete.": "Seleccione una fila para eliminar.",
    "Delete selected correction?": "¿Eliminar la corrección seleccionada?",
    "Perfect match! No training needed.": "¡Coincidencia perfecta! No se necesita entrenamiento.",
    "Correction added.": "Corrección agregada.",
    "Test a phrase first.": "Pruebe una frase primero.",
    "Scaling saved. Restart required for full effect.": "Escalado guardado. Se requiere reiniciar para que surta efecto.",
    "All detected game actions typically have voice commands assigned!\nYou can still edit existing ones.": "¡Todas las acciones de juego detectadas suelen tener comandos de voz asignados!\nAún puede editar los existentes.",
    "Please select a Game grouping first.": "Seleccione primero un grupo de Juego.",
    "Internal Error: Active bindings path is unknown.": "Error interno: la ruta de las asignaciones activas es desconocida.",
    "Select an action to rebind.": "Seleccione una acción para reasignar.",
    "No profiles found in this group.": "No se encontraron perfiles en este grupo.",
    "No standard binding files found for this game type.": "No se encontraron archivos de asignación estándar para este tipo de juego.",
    "Failed to remove profiles.": "Error al eliminar perfiles.",
    "Name already taken.": "El nombre ya está en uso.",
    "No profiles found. (Check console for path/parsing errors)": "No se encontraron perfiles. (Consulte la consola para ver errores de ruta/análisis)",
    "Import Complete": "Importación completada",
    "No profiles found.": "No se encontraron perfiles.",
    "Elite Dangerous appears to be running.\n\nChanges made now may NOT take effect immediately or could be overwritten by the game.\n\nContinue anyway?": "Elite Dangerous parece estar ejecutándose.\n\nEs posible que los cambios realizados ahora NO surtan efecto de inmediato o que el juego los sobrescriba.\n\n¿Continuar de todos modos?",
    "Scan and import standard Elite Dangerous ControlSchemes?\nThis may double up profiles if you already have them, but skips duplicate names.": "¿Escanear e importar ControlSchemes estándar de Elite Dangerous?\nEsto puede duplicar perfiles si ya los tiene, pero omite los nombres duplicados.",
    "Importing voice in background...": "Importando voz en segundo plano...",
    "Downloading voice in background...": "Descargando voz en segundo plano...",
    "Failed to install voice.": "Error al instalar la voz.",
    "Failed to import voice.": "Error al importar la voz.",
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
    # This is a simplified parser for .po files that usually have simple structures
    pattern = re.compile(r'(msgid\s+"(.*?)")\s+(msgstr\s+"(.*?)")', re.DOTALL)
    
    def replace_func(match):
        full_msgid_part = match.group(1)
        english_text = match.group(2)
        full_msgstr_part = match.group(3)
        existing_translation = match.group(4)
        
        # Don't overwrite existing non-empty translations unless they are just placeholders
        if existing_translation and existing_translation != english_text:
             return match.group(0)
             
        spanish = translate_string(english_text)
        if spanish:
            return f'{full_msgid_part}\nmsgstr "{spanish}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Auto-translated {filepath}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    es_dir = os.path.join(script_dir, 'locale/es/LC_MESSAGES/')
    
    if os.path.exists(es_dir):
        for filename in os.listdir(es_dir):
            if filename.endswith('.po'):
                auto_translate_po(os.path.join(es_dir, filename))
        
        print("\nNext steps:")
        print("1. Review translations in locale/es/LC_MESSAGES/")
        print("2. Compile: pybabel compile -d locale")
        print("3. Test: Set UI_LANGUAGE=es in config, run launcher")
    else:
        print(f"Error: {es_dir} not found")
        sys.exit(1)
