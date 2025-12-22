#!/usr/bin/env python3
"""
Ukrainian translation for TuxTalks using gaming-specific glossary.
"""

# Ukrainian Gaming Glossary (English -> Ukrainian)
UKRAINIAN_GLOSSARY = {
    # UI Elements
    "Settings": "Налаштування",
    "General": "Загальні",
    "Voice": "Голос",
    "Games": "Ігри",
    "Speech Engines": "Голосові Движки",
    "Input": "Введення",
    "Vocabulary": "Словник",
    "Help": "Допомога",
    "Content Packs": "Пакети Вмісту",
    "Corrections": "Виправлення",
    
    # Actions
    "Start Assistant": "Запустити Асистента",
    "Stop": "Зупинити",
    "Exit": "Вихід",
    "Save Config": "Зберегти Конфігурацію",
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
    "Test": "Тест",
    "Run": "Виконати",
    "Save": "Зберегти",
    "Apply": "Застосувати",
   
    # Gaming Terms
    "Bindings": "Прив'язки",
    "Binds": "Прив'язки",
    "Game Action": "Ігрова Дія",
    "Voice Command": "Голосова Команда",
    "Mapped Key": "Призначена Клавіша",
    "Process Name": "Ім'я Процесу",
    "Binding Profile": "Профіль Прив'язок",
    "Macro": "Макрос",
    "Macros": "Макроси",
    "Profile": "Профіль",
    "Game Integration": "Інтеграція Гри",
    "Runtime Status": "Статус Виконання",
    "Runtime Environment": "Середовище Виконання",
    
    # Speech/Voice
    "Wake Word": "Слово Активації",
    "Speech Recognition": "Розпізнавання Мовлення",
    "Text-to-Speech": "Текст у Мовлення",
    "Active Model": "Активна Модель",
    "Active Voice": "Активний Голос",
    "Voice Triggers": "Голосові Тригери",
    "Voice Corrections": "Голосові Виправлення",
    
    # Status messages
    "Saved": "Збережено",
    "Success": "Успіх",
    "Error": "Помилка",
    "Info": "Інформація",
    "Warning": "Попередження",
    "Complete": "Завершено",
    "Failed": "Невдача",
    "Stopped": "Зупинено",
    "Downloaded": "Завантажено",
    "Downloading": "Завантаження",
    "Importing": "Імпорт",
    
    # Common UI
    "Theme": "Тема",
    "Scale": "Масштаб",
    "Filter": "Фільтр",
    "Search": "Пошук",
    "Advanced Voice Control for Linux": "Розширене Голосове Керування для Linux",
}

def translate_to_ukrainian(po_file):
    """Apply Ukrainian translations to .po file."""
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('msgid "'):
            msgid = line.split('msgid "')[1].rstrip('"\n')
            msgstr_line = lines[i + 1] if i + 1 < len(lines) else 'msgstr ""\n'
            
            if msgid and msgid in UKRAINIAN_GLOSSARY:
                ukrainian = UKRAINIAN_GLOSSARY[msgid]
                msgstr_line = f'msgstr "{ukrainian}"\n'
            
            output.append(line)
            output.append(msgstr_line)
            i += 2
        else:
            output.append(line)
            i += 1
    
    with open(po_file, 'w', encoding='utf-8') as f:
        f.writelines(output)
    
    print(f"✓ Ukrainian translations applied to {po_file}")

if __name__ == '__main__':
    import sys
    po_file = sys.argv[1] if len(sys.argv) > 1 else 'locale/uk/LC_MESSAGES/tuxtalks.po'
    translate_to_ukrainian(po_file)
    print(f"Translated {len(UKRAINIAN_GLOSSARY)} terms")
