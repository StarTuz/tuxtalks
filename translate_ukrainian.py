#!/usr/bin/env python3
"""
Automated Ukrainian translation for TuxTalks using gaming-specific glossary.
"""

import re
import os
import sys

# Ukrainian Gaming Glossary (English -> Ukrainian)
UKRAINIAN_GLOSSARY = {
    # UI Elements
    "Settings": "Налаштування",
    "General": "Загальні",
    "Voice": "Голос",
    "Games": "Ігри",
    "Speech Engines": "Голосові рушії",
    "Input": "Ввід",
    "Vocabulary": "Словник",
    "Help": "Довідка",
    "Content Packs": "Пакети контенту",
    "Corrections": "Виправлення",
    "Training": "Тренування",
    "Player": "Програвач",
    
    # Actions
    "Start Assistant": "Запустити асистента",
    "Stop": "Зупинити",
    "Exit": "Вийти",
    "Save Config": "Зберегти конфігурацію",
    "Cancel": "Скасувати",
    "Browse": "Огляд",
    "Add": "Додати",
    "Edit": "Редагувати",
    "Delete": "Видалити",
    "Refresh": "Оновити",
    "Clear": "Очистити",
    "New": "Новий",
    "Create": "Створити",
    "Remove": "Видалити",
    "Import": "Імпорт",
    "Export": "Експорт",
    "Backup": "Резервна копія",
    "Restore": "Відновити",
    "Test": "Тестувати",
    "Run": "Запустити",
    "Save": "Зберегти",
    "Apply": "Застосувати",
    "OK": "OK",
    "Yes": "Так",
    "No": "Ні",
    "Close": "Закрити",
    "Continue": "Продовжити",
    
    # Gaming Terms
    "Bindings": "Прив'язки",
    "Binds": "Прив'язки",
    "Game Action": "Ігрова дія",
    "Voice Command": "Голосова команда",
    "Mapped Key": "Призначена клавіша",
    "Process Name": "Назва процесу",
    "Binding Profile": "Профіль прив'язок",
    "Macro": "Макрос",
    "Macros": "Макроси",
    "Profile": "Профіль",
    "Game Integration": "Інтеграція гри",
    "Runtime Status": "Статус виконання",
    "Runtime Environment": "Середовище виконання",
    "Custom Commands": "Спеціальні команди",
    "Game Bindings": "Ігрові прив'язки",
    "Active Profile Bindings": "Прив'язки активного профілю",
    
    # Speech/Voice
    "Wake Word": "Слово активації",
    "Wake Word Settings": "Налаштування слова активації",
    "Speech Recognition": "Розпізнавання мовлення",
    "Speech Recognition (Vosk)": "Розпізнавання мовлення (Vosk)",
    "Text-to-Speech": "Перетворення тексту в мовлення",
    "Text-to-Speech (Piper)": "Перетворення тексту в мовлення (Piper)",
    "Active Model": "Активна модель",
    "Active Voice": "Активний голос",
    "Voice Triggers": "Голосові тригери",
    "Voice Corrections": "Голосові виправлення",
    "Voice Fingerprint": "Голосовий відбиток",
    "Voice Learning": "Голосове навчання",
    "Voice Training": "Голосове тренування",
    
    # UI Labels
    "Theme": "Тема",
    "Scale": "Масштаб",
    "Filter": "Фільтр",
    "Search": "Пошук",
    "Name": "Назва",
    "Description": "Опис",
    "Path": "Шлях",
    "File": "Файл",
    "Folder": "Папка",
    "Directory": "Каталог",
    "Configuration": "Конфігурація",
    "Options": "Опції",
    "Preferences": "Налаштування",
    
    # Status messages
    "Saved": "Збережено",
    "Success": "Успішно",
    "Error": "Помилка",
    "Info": "Інфо",
    "Warning": "Попередження",
    "Complete": "Завершено",
    "Failed": "Невдача",
    "Stopped": "Зупинено",
    "Downloaded": "Завантажено",
    "Downloading": "Завантаження",
    "Importing": "Імпортування",
    "Loading": "Завантаження",
    "Processing": "Обробка",
    "Ready": "Готово",
    "Running": "Запущено",
    
    # Game Integration Specific
    "Game": "Гра",
    "Game Type": "Тип гри",
    "Game Name": "Назва гри",
    "Game Group": "Група гри",
    "Game Bindings File": "Файл ігрових прив'язок",
    "Bindings Path": "Шлях до прив'язок",
    "Bindings File Path": "Шлях до файлу прив'язок",
    "Configuration Name": "Назва конфігурації",
    "Profile Name": "Назва профілю",
    "Macro Profile": "Профіль макросів",
    "Defined Macros": "Визначені макроси",
    "Macro Steps": "Кроки макросу",
    "Delay": "Затримка",
    "Action": "Дія",
    "Key": "Клавіша",
    "Source": "Джерело",
    "Built-in": "Вбудований",
    "Custom": "Спеціальний",
    "Pack": "Пакет",
    
    # Wizard/Dialog
    "Add Game": "Додати гру",
    "Edit Game": "Редагувати гру",
    "Remove Game": "Видалити гру",
    "Add Bind": "Додати прив'язку",
    "Edit Bind": "Редагувати прив'язку",
    "Remove Bind": "Видалити прив'язку",
    "Default Binds": "Прив'язки за замовчуванням",
    "Add Command": "Додати команду",
    "Add Game Profile": "Додати профіль гри",
    "Create Profile": "Створити профіль",
    "Save Settings": "Зберегти налаштування",
    "Profile Settings": "Налаштування профілю",
    "Profile Configuration": "Конфігурація профілю",
    
    # Steps/Process
    "Step 1": "Крок 1",
    "Step 2": "Крок 2",
    "Step 3": "Крок 3",
    "Select Running Game Process": "Оберіть запущений процес гри",
    "Scan Processes": "Сканувати процеси",
    "Scan Results": "Результати сканування",
    "Command Line": "Командний рядок",
    "Command Line / Path": "Командний рядок / Шлях",
    
    # Specific Actions
    "Enable Game Integration": "Увімкнути інтеграцію гри",
    "Modify Trigger": "Змінити тригер",
    "Clear Trigger": "Очистити тригер",
    "Delete Selected": "Видалити обране",
    "Clear All": "Очистити все",
    "Use Selected": "Використати обране",
    "Restore Defaults": "Відновити за замовчуванням",
    "Import Defaults": "Імпортувати за замовчуванням",
    
    # Voice/Audio
    "Wake Word:": "Слово активації:",
    "Active Model:": "Активна модель:",
    "Active Voice:": "Активний голос:",
    "Browse Folder": "Огляд папки",
    "Download from URL": "Завантажити за URL",
    "Delete Voice": "Видалити голос",
    "Import New Voice": "Імпортувати новий голос",
    "Load from File (.onnx)": "Завантажити з файлу (.onnx)",
    
    # Correction/Training
    "When I hear...": "Коли я чую...",
    "I should understand...": "Я маю розуміти...",
    "Test & Train": "Тестувати та тренувати",
    "Record": "Записати",
    "Dur:": "Трив.:",
    "Add as Correction": "Додати як виправлення",
    "Targeted Train": "Цільове тренування",
    "Basic": "Базовий",
    "Advanced": "Розширений",
    "Recent Ignored/Missed Commands": "Останні ігноровані/пропущені команди",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Натисніть комбінацію клавіш на клавіатурі:",
    "(Example: Ctrl + Alt + H)": "(Приклад: Ctrl + Alt + H)",
    "Clear": "Очистити",
    "Capture": "Захопити",
    "Key to Press:": "Клавіша для натискання:",
    "Modifiers:": "Модифікатори:",
    
    # Game-Specific
    "Game Integration Status": "Статус інтеграції гри",
    "Game:": "Гра:",
    "Binds:": "Прив'язки:",
    "Macro Profile:": "Профіль макросів:",
    "Runtime Status:": "Статус виконання:",
    "Profile Name (Variant):": "Назва профілю (варіант):",
    "Binding Profile Name:": "Назва профілю прив'язок:",
    "Bindings File Path (Optional):": "Шлях до файлу прив'язок (опціонально):",
    "Process Name (e.g. X4.exe):": "Назва процесу (наприклад, X4.exe):",
    "Game Type:": "Тип гри:",
    "Game Name:": "Назва гри:",
    "Process Name:": "Назва процесу:",
    "Runtime Environment:": "Середовище виконання:",
    
    # Advanced Features
    "External Audio Assets": "Зовнішні аудіоресурси",
    "Audio Directory:": "Аудіокаталог:",
    "Reference File": "Довідковий файл",
    "Sound Pool": "Пул звуків",
    "Playback Mode": "Режим відтворення",
    "Random": "Випадковий",
    "Simultaneous": "Одночасний",
    "Sequential": "Послідовний",
    "Round-Robin": "Почерговий",
    
    # Common long phrases (abbreviated)
    "Advanced Voice Control for Linux": "Розширене голосове керування для Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Натисни, щоб говорити",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "OK",
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

PHRASES = {
    "Configuration saved.": "Конфігурацію збережено.",
    "TuxTalks is already running.": "TuxTalks вже запущено.",
    "Unsaved Changes": "Незбережені зміни",
    "You have unsaved changes. Save before starting?": "У вас є незбережені зміни. Зберегти перед запуском?",
    "Assistant stopped.": "Асистента зупинено.",
    "Please select a game first.": "Будь ласка, спочатку оберіть гру.",
    "No game selected.": "Гру не обрано.",
    "Profile name cannot be empty.": "Назва профілю не може бути порожньою.",
    "Failed to create macro profile.": "Не вдалося створити профіль макросів.",
    "Failed to delete macro profile.": "Не вдалося видалити профіль макросів.",
    "Failed to rename macro profile.": "Не вдалося перейменувати профіль макросів.",
    "No profile selected.": "Профіль не обрано.",
    "Process Name required.": "Потрібна назва процесу.",
    "Select a row to delete.": "Оберіть рядок для видалення.",
    "Delete selected correction?": "Видалити обране виправлення?",
    "Perfect match! No training needed.": "Ідеальний збіг! Тренування не потрібне.",
    "Correction added.": "Виправлення додано.",
    "Test a phrase first.": "Спочатку протестуйте фразу.",
}

def translate_string(english):
    """Translate an English string to Ukrainian."""
    if english in UKRAINIAN_GLOSSARY:
        return UKRAINIAN_GLOSSARY[english]
    if english in PHRASES:
        return PHRASES[english]
    
    trimmed = english.strip()
    if trimmed != english and trimmed in UKRAINIAN_GLOSSARY:
        return UKRAINIAN_GLOSSARY[trimmed]
    if trimmed != english and trimmed in PHRASES:
        return PHRASES[trimmed]
    
    if english.endswith(':'):
        base = english[:-1].strip()
        if base in UKRAINIAN_GLOSSARY:
            return f"{UKRAINIAN_GLOSSARY[base]}:"
        
    if english.endswith('...'):
        base = english[:-3].strip()
        if base in UKRAINIAN_GLOSSARY:
            return f"{UKRAINIAN_GLOSSARY[base]}..."

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
             
        ukrainian = translate_string(english_text)
        if ukrainian:
            return f'{full_msgid_part}\nmsgstr "{ukrainian}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Auto-translated {filepath}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    uk_dir = os.path.join(script_dir, 'locale/uk/LC_MESSAGES/')
    
    if os.path.exists(uk_dir):
        for filename in os.listdir(uk_dir):
            if filename.endswith('.po'):
                auto_translate_po(os.path.join(uk_dir, filename))
        
        print("\nNext steps:")
        print("1. Review translations in locale/uk/LC_MESSAGES/")
        print("2. Compile: pybabel compile -d locale")
    else:
        print(f"Error: {uk_dir} not found")
        sys.exit(1)
