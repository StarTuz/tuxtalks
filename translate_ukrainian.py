#!/usr/bin/env python3
"""
Automated Ukrainian translation for TuxTalks using gaming-specific glossary.
Enhances all .po files in the Ukrainian locale.
"""

import re
import os
import sys

# Gaming-specific glossary (English -> Ukrainian)
GAMING_GLOSSARY = {
    # UI Elements (general terms)
    "Settings": "Налаштування",
    "General": "Загальні",
    "Voice": "Голос",
    "Games": "Ігри",
    "Speech Engines": "Голосові рушії",
    "Input": "Ввід",
    "Vocabulary": "Словник",
    "Help": "Довідка",
    "Content Packs": "Пакети вмісту",
    "Corrections": "Виправлення",
    "Training": "Навчання",
    "Player": "Плеєр",
    
    # Actions
    "Start Assistant": "Запустити помічника",
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
    "Import": "Імпортувати",
    "Export": "Експортувати",
    "Backup": "Резервна копія",
    "Restore": "Відновити",
    "Test": "Тестувати",
    "Run": "Запустити",
    "Save": "Зберегти",
    "Apply": "Застосувати",
    "OK": "Гаразд",
    "Yes": "Так",
    "No": "Ні",
    "Close": "Закрити",
    "Continue": "Продовжити",
    
    # Gaming Terms
    "Bindings": "Прив'язки",
    "Binds": "Клавіші",
    "Game Action": "Ігрова дія",
    "Voice Command": "Голосова команда",
    "Mapped Key": "Призначена клавіша",
    "Process Name": "Назва процесу",
    "Binding Profile": "Профіль прив'язок",
    "Macro": "Макрос",
    "Macros": "Макроси",
    "Profile": "Профіль",
    "Game Integration": "Інтеграція з іграми",
    "Runtime Status": "Статус виконання",
    "Runtime Environment": "Середовище виконання",
    "Custom Commands": "Власні команди",
    "Game Bindings": "Ігрові прив'язки",
    "Active Profile Bindings": "Прив'язки активного профілю",
    
    # Speech/Voice
    "Wake Word": "Слово активації",
    "Wake Word Settings": "Налаштування слова активації",
    "Speech Recognition": "Розпізнавання мовлення",
    "Speech Recognition (Vosk)": "Розпізнавання мовлення (Vosk)",
    "Text-to-Speech": "Перетворення тексту в мовлення",
    "Text-to-Speech (Piper)": "Синтез мовлення (Piper)",
    "Active Model": "Активна модель",
    "Active Voice": "Активний голос",
    "Voice Triggers": "Голосові тригери",
    "Voice Corrections": "Голосові виправлення",
    "Voice Fingerprint": "Голосовий відбиток",
    "Voice Learning": "Вивчення голосу",
    "Voice Training": "Навчання голосу",
    
    # UI Labels
    "Theme": "Тема",
    "Scale": "Масштаб",
    "Filter": "Фільтр",
    "Search": "Пошук",
    "Name": "Ім'я",
    "Description": "Опис",
    "Path": "Шлях",
    "File": "Файл",
    "Folder": "Папка",
    "Directory": "Директорія",
    "Configuration": "Конфігурація",
    "Options": "Опції",
    "Preferences": "Налаштування",
    
    # Status messages
    "Saved": "Збережено",
    "Success": "Успіх",
    "Error": "Помилка",
    "Info": "Інфо",
    "Warning": "Попередження",
    "Complete": "Завершено",
    "Failed": "Помилка",
    "Stopped": "Зупинено",
    "Downloaded": "Завантажено",
    "Downloading": "Завантаження",
    "Importing": "Імпортування",
    "Loading": "Завантаження",
    "Processing": "Обробка",
    "Ready": "Готово",
    "Running": "Працює",
    
    # Game Integration Specific
    "Game": "Гра",
    "Game Type": "Тип гри",
    "Game Name": "Назва гри",
    "Game Group": "Група ігор",
    "Game Bindings File": "Файл прив'язок гри",
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
    "Custom": "Власний",
    "Pack": "Пакет",
    
    # Wizard/Dialog
    "Add Game": "Додати гру",
    "Edit Game": "Редагувати гру",
    "Remove Game": "Видалити гру",
    "Add Bind": "Додати прив'язку",
    "Edit Bind": "Редагувати прив'язку",
    "Remove Bind": "Видалити прив'язку",
    "Default Binds": "Стандартні прив'язки",
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
    "Select Running Game Process": "Оберіть процес гри, що запущена",
    "Scan Processes": "Сканувати процеси",
    "Scan Results": "Результати сканування",
    "Command Line": "Командний рядок",
    "Command Line / Path": "Командний рядок / Шлях",
    
    # Specific Actions
    "Enable Game Integration": "Увімкнути інтеграцію з іграми",
    "Modify Trigger": "Змінити тригер",
    "Clear Trigger": "Очистити тригер",
    "Delete Selected": "Видалити обране",
    "Clear All": "Очистити все",
    "Use Selected": "Використовувати обране",
    "Restore Defaults": "Відновити стандартні",
    "Import Defaults": "Імпортувати стандартні",
    
    # Voice/Audio
    "Wake Word:": "Слово активації:",
    "Active Model:": "Активна модель:",
    "Active Voice:": "Активний голос:",
    "Browse Folder": "Огляд папки",
    "Download from URL": "Завантажити з URL",
    "Delete Voice": "Видалити голос",
    "Import New Voice": "Імпортувати новий голос",
    "Load from File (.onnx)": "Завантажити з файлу (.onnx)",
    
    # Correction/Training
    "When I hear...": "Коли я чую...",
    "I should understand...": "Я маю зрозуміти...",
    "Test & Train": "Тестування та навчання",
    "Record": "Запис",
    "Dur:": "Трив.:",
    "Add as Correction": "Додати як виправлення",
    "Targeted Train": "Цільове навчання",
    "Basic": "Базовий",
    "Advanced": "Розширений",
    "Recent Ignored/Missed Commands": "Останні ігноровані/пропущені команди",
    
    # Key Binding
    "Press the key combination on your keyboard:": "Натисніть комбінацію клавіш на клавіатурі:",
    "(Example: Ctrl + Alt + H)": "(Приклад: Ctrl + Alt + H)",
    "Clear": "Очистити",
    "Capture": "Захоплення",
    "Key to Press:": "Клавіша для натискання:",
    "Modifiers:": "Модифікатори:",
    
    # Game-Specific
    "Game Integration Status": "Статус інтеграції з іграми",
    "Game:": "Гра:",
    "Binds:": "Прив'язки:",
    "Macro Profile:": "Профіль макросів:",
    "Runtime Status:": "Статус виконання:",
    "Profile Name (Variant):": "Назва профілю (варіант):",
    "Binding Profile Name:": "Назва профілю прив'язок:",
    "Bindings File Path (Optional):": "Шлях до файлу прив'язок (опціонально):",
    "Process Name (e.g. X4.exe):": "Назва процесу (напр. X4.exe):",
    "Game Type:": "Тип гри:",
    "Game Name:": "Назва гри:",
    "Process Name:": "Назва процесу:",
    "Runtime Environment:": "Середовище виконання:",
    
    # Advanced Features
    "External Audio Assets": "Зовнішні аудіо-ресурси",
    "Audio Directory:": "Директорія аудіо:",
    "Reference File": "Еталонний файл",
    "Sound Pool": "Пул звуків",
    "Playback Mode": "Режим відтворення",
    "Random": "Випадково",
    "Simultaneous": "Одночасно",
    "Sequential": "Послідовно",
    "Round-Robin": "Циклічно",
    
    # Common long phrases
    "Advanced Voice Control for Linux": "Розширене голосове керування для Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "Натисни та говори",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "Гаразд",
    "Ctrl": "Ctrl",
    "Alt": "Alt",
    "Shift": "Shift",
    
    # Wizard setup
    "TuxTalks First-Run Setup": "Перший запуск TuxTalks",
    "Welcome to TuxTalks! 🐧": "Ласкаво просимо до TuxTalks! 🐧",
    "TuxTalks is your powerful, secure, and offline voice command assistant for Linux gaming.\n\nThis wizard will help you set up your core preferences in just a few minutes so you can start talking to your favorite games and media players.": "TuxTalks — це ваш потужний, безпечний та офлайновий помічник для голосового керування іграми на Linux.\n\nЦей майстер допоможе вам налаштувати основні параметри за кілька хвилин, щоб ви могли почати спілкуватися зі своїми улюбленими іграми та медіаплеєрами.",
    "Ready to begin?": "Готові почати?",
    "Step 1: Interface Language": "Крок 1: Мова інтерфейсу",
    "Select the language for the TuxTalks interface:": "Оберіть мову інтерфейсу TuxTalks:",
    "Note: RTL support is automatically enabled for Arabic.": "Примітка: підтримка RTL автоматично вмикається для арабської мови.",
    "Step 2: Voice Recognition (ASR)": "Крок 2: Розпізнавання мовлення (ASR)",
    "To process your voice offline, TuxTalks needs a language model.\n\nBased on your language selection, we recommend the following model:": "Для офлайн-обробки вашого голосу TuxTalks потрібна мовна модель.\n\nНа основі вашого вибору мови ми рекомендуємо наступну модель:",
    "Download & Install": "Завантажити та встановити",
    "Step 3: Initial Integration": "Крок 3: Початкова інтеграція",
    "Choose your primary media player:": "Оберіть основний медіаплеєр:",
    "Tip: You can change this and add games later in the main settings.": "Порада: ви зможете змінити це та додати ігри пізніше в основних налаштуваннях.",
    "All Set! 🎉": "Все готово! 🎉",
    "Setup is complete. TuxTalks is now configured with your language and voice preferences.\n\nClick 'Finish' to open the main settings where you can further customize your experience, add games, and calibrate your microphone.": "Налаштування завершено. TuxTalks тепер налаштовано відповідно до вашої мови та голосових уподобань.\n\nНатисніть «Завершити», щоб відкрити основні налаштування, де ви зможете додатково налаштувати систему, додати ігри та відкалібрувати мікрофон.",
    "Skip Setup?": "Пропустити налаштування?",
    "Closing this window will skip the setup wizard. You can still configure everything manually in the settings.\n\nSkip and don't show again?": "Закриття цього вікна призведе до пропуску майстра налаштування. Ви все ще можете налаштувати все вручну в налаштуваннях.\n\nПропустити і більше не показувати?",
}

# Sentence fragments/phrases
PHRASES = {
    "Configuration saved.": "Конфігурацію збережено.",
    "TuxTalks is already running.": "TuxTalks уже запущено.",
    "Unsaved Changes": "Незбережені зміни",
    "You have unsaved changes. Save before starting?": "У вас є незбережені зміни. Зберегти перед запуском?",
    "Assistant stopped.": "Помічника зупинено.",
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
    "Perfect match! No training needed.": "Ідеальний збіг! Навчання не потрібне.",
    "Correction added.": "Виправлення додано.",
    "Test a phrase first.": "Спочатку протестуйте фразу.",
    "Scaling saved. Restart required for full effect.": "Масштаб збережено. Для повного ефекту потрібен перезапуск.",
    "All detected game actions typically have voice commands assigned!\nYou can still edit existing ones.": "Для всіх виявлених ігрових дій зазвичай призначені голосові команди!\nВи все ще можете редагувати існуючі.",
    "Please select a Game grouping first.": "Будь ласка, спочатку оберіть групу ігор.",
    "Internal Error: Active bindings path is unknown.": "Внутрішня помилка: шлях до активних прив'язок невідомий.",
    "Select an action to rebind.": "Оберіть дію для перепризначення.",
    "No profiles found in this group.": "У цій групі профілів не знайдено.",
    "No standard binding files found for this game type.": "Стандартних файлів прив'язок для цього типу гри не знайдено.",
    "Failed to remove profiles.": "Не вдалося видалити профілі.",
    "Name already taken.": "Назва вже зайнята.",
    "No profiles found. (Check console for path/parsing errors)": "Профілів не знайдено. (Перевірте консоль на наявність помилок шляху/парсингу)",
    "Import Complete": "Імпорт завершено",
    "No profiles found.": "Профілів не знайдено.",
    "Elite Dangerous appears to be running.\n\nChanges made now may NOT take effect immediately or could be overwritten by the game.\n\nContinue anyway?": "Схоже, Elite Dangerous запущено.\n\nЗміни, внесені зараз, можуть НЕ набути чинності негайно або можуть бути перезаписані грою.\n\nПродовжити в будь-якому разі?",
    "Scan and import standard Elite Dangerous ControlSchemes?\nThis may double up profiles if you already have them, but skips duplicate names.": "Сканувати та імпортувати стандартні схеми керування Elite Dangerous?\nЦе може призвести до дублювання профілів, якщо вони вже існують, але імена-дублікати будуть пропущені.",
    "Importing voice in background...": "Імпортування голосу у фоновому режимі...",
    "Downloading voice in background...": "Завантаження голосу у фоновому режимі...",
    "Failed to install voice.": "Не вдалося встановити голос.",
    "Failed to import voice.": "Не вдалося імпортувати голос.",
}

def translate_string(english):
    """Translate an English string to Ukrainian."""
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
             
        ukrainian = translate_string(english_text)
        if ukrainian:
            return f'{full_msgid_part}\nmsgstr "{ukrainian}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    # Write back
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
