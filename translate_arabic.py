#!/usr/bin/env python3
"""
Automated Arabic translation for TuxTalks using gaming-specific glossary.
Enhances all .po files in the Arabic locale.
Supports RTL text direction considerations.
"""

import re
import os
import sys

# Gaming-specific glossary (English -> Arabic)
GAMING_GLOSSARY = {
    # UI Elements (general terms)
    "Settings": "الإعدادات",
    "General": "عام",
    "Voice": "الصوت",
    "Games": "الألعاب",
    "Speech Engines": "محركات الكلام",
    "Input": "الإدخال",
    "Vocabulary": "المفردات",
    "Help": "المساعدة",
    "Content Packs": "حزم المحتوى",
    "Corrections": "التصحيحات",
    "Training": "التدريب",
    "Player": "المشغل",
    
    # Actions
    "Start Assistant": "بدء المساعد",
    "Stop": "إيقاف",
    "Exit": "خروج",
    "Save Config": "حفظ التكوين",
    "Cancel": "إلغاء",
    "Browse": "تصفح",
    "Add": "إضافة",
    "Edit": "تعديل",
    "Delete": "حذف",
    "Refresh": "تحديث",
    "Clear": "مسح",
    "New": "جديد",
    "Create": "إنشاء",
    "Remove": "إزالة",
    "Import": "استيراد",
    "Export": "تصدير",
    "Backup": "نسخ احتياطي",
    "Restore": "استعادة",
    "Test": "اختبار",
    "Run": "تشغيل",
    "Save": "حفظ",
    "Apply": "تطبيق",
    "OK": "موافق",
    "Yes": "نعم",
    "No": "لا",
    "Close": "إغلاق",
    "Continue": "استمرار",
    
    # Gaming Terms
    "Bindings": "الارتباطات",
    "Binds": "الارتباطات",
    "Game Action": "إجراء اللعبة",
    "Voice Command": "أمر صوتي",
    "Mapped Key": "المفتاح المخصص",
    "Process Name": "اسم العملية",
    "Binding Profile": "ملف الارتباطات",
    "Macro": "ماكرو",
    "Macros": "ماكرو",
    "Profile": "ملف شخصي",
    "Game Integration": "تكامل اللعبة",
    "Runtime Status": "حالة التشغيل",
    "Runtime Environment": "بيئة التشغيل",
    "Custom Commands": "أوامر مخصصة",
    "Game Bindings": "ارتباطات اللعبة",
    "Active Profile Bindings": "ارتباطات الملف النشط",
    
    # Speech/Voice
    "Wake Word": "كلمة التنبيه",
    "Wake Word Settings": "إعدادات كلمة التنبيه",
    "Speech Recognition": "التعرف على الكلام",
    "Speech Recognition (Vosk)": "التعرف على الكلام (Vosk)",
    "Text-to-Speech": "تحويل النص إلى كلام",
    "Text-to-Speech (Piper)": "تحويل النص إلى كلام (Piper)",
    "Active Model": "النموذج النشط",
    "Active Voice": "الصوت النشط",
    "Voice Triggers": "محفزات الصوت",
    "Voice Corrections": "تصحيحات الصوت",
    "Voice Fingerprint": "بصمة الصوت",
    "Voice Learning": "تعلم الصوت",
    "Voice Training": "تدريب الصوت",
    
    # UI Labels
    "Theme": "المظهر",
    "Scale": "الحجم",
    "Filter": "تصفية",
    "Search": "بحث",
    "Name": "الاسم",
    "Description": "الوصف",
    "Path": "المسار",
    "File": "ملف",
    "Folder": "مجلد",
    "Directory": "دليل",
    "Configuration": "التكوين",
    "Options": "خيارات",
    "Preferences": "تفضيلات",
    
    # Status messages
    "Saved": "تم الحفظ",
    "Success": "نجاح",
    "Error": "خطأ",
    "Info": "معلومات",
    "Warning": "تحذير",
    "Complete": "مكتمل",
    "Failed": "فشل",
    "Stopped": "متوقف",
    "Downloaded": "تم التنزيل",
    "Downloading": "جاري التنزيل",
    "Importing": "جاري الاستيراد",
    "Loading": "جاري التحميل",
    "Processing": "جاري المعالجة",
    "Ready": "جاهز",
    "Running": "قيد التشغيل",
    
    # Game Integration Specific
    "Game": "لعبة",
    "Game Type": "نوع اللعبة",
    "Game Name": "اسم اللعبة",
    "Game Group": "مجموعة اللعبة",
    "Game Bindings File": "ملف ارتباطات اللعبة",
    "Bindings Path": "مسار الارتباطات",
    "Bindings File Path": "مسار ملف الارتباطات",
    "Configuration Name": "اسم التكوين",
    "Profile Name": "اسم الملف الشخصي",
    "Macro Profile": "ملف الماكرو",
    "Defined Macros": "الماكرو المعرفة",
    "Macro Steps": "خطوات الماكرو",
    "Delay": "تأخير",
    "Action": "إجراء",
    "Key": "مفتاح",
    "Source": "المصدر",
    "Built-in": "مدمج",
    "Custom": "مخصص",
    "Pack": "حزمة",
    
    # Wizard/Dialog
    "Add Game": "إضافة لعبة",
    "Edit Game": "تعديل اللعبة",
    "Remove Game": "إزالة اللعبة",
    "Add Bind": "إضافة ارتباط",
    "Edit Bind": "تعديل الارتباط",
    "Remove Bind": "إزالة الارتباط",
    "Default Binds": "الارتباطات الافتراضية",
    "Add Command": "إضافة أمر",
    "Add Game Profile": "إضافة ملف لعبة",
    "Create Profile": "إنشاء ملف شخصي",
    "Save Settings": "حفظ الإعدادات",
    "Profile Settings": "إعدادات الملف الشخصي",
    "Profile Configuration": "تكوين الملف الشخصي",
    
    # Steps/Process
    "Step 1": "الخطوة 1",
    "Step 2": "الخطوة 2",
    "Step 3": "الخطوة 3",
    "Select Running Game Process": "اختيار عملية اللعبة الجارية",
    "Scan Processes": "فحص العمليات",
    "Scan Results": "نتائج الفحص",
    "Command Line": "سطر الأوامر",
    "Command Line / Path": "سطر الأوامر / المسار",
    
    # Specific Actions
    "Enable Game Integration": "تفعيل تكامل اللعبة",
    "Modify Trigger": "تعديل المحفز",
    "Clear Trigger": "مسح المحفز",
    "Delete Selected": "حذف المحدد",
    "Clear All": "مسح الكل",
    "Use Selected": "استخدام المحدد",
    "Restore Defaults": "استعادة الافتراضيات",
    "Import Defaults": "استيراد الافتراضيات",
    
    # Voice/Audio
    "Wake Word:": "كلمة التنبيه:",
    "Active Model:": "النموذج النشط:",
    "Active Voice:": "الصوت النشط:",
    "Browse Folder": "تصفح المجلد",
    "Download from URL": "تنزيل من رابط",
    "Delete Voice": "حذف الصوت",
    "Import New Voice": "استيراد صوت جديد",
    "Load from File (.onnx)": "تحميل من ملف (.onnx)",
    
    # Correction/Training
    "When I hear...": "عندما أسمع...",
    "I should understand...": "يجب أن أفهم...",
    "Test & Train": "اختبار وتدريب",
    "Record": "تسجيل",
    "Dur:": "المدة:",
    "Add as Correction": "إضافة كـ تصحيح",
    "Targeted Train": "تدريب مستهدف",
    "Basic": "أساسي",
    "Advanced": "متقدم",
    "Recent Ignored/Missed Commands": "الأوامر الأخيرة المتجاهلة/المفقودة",
    
    # Key Binding
    "Press the key combination on your keyboard:": "اضغط على مجموعة المفاتيح من لوحة المفاتيح:",
    "(Example: Ctrl + Alt + H)": "(مثال: Ctrl + Alt + H)",
    "Clear": "مسح",
    "Capture": "التقاط",
    "Key to Press:": "المفتاح للضغط:",
    "Modifiers:": "المعدلات:",
    
    # Game-Specific
    "Game Integration Status": "حالة تكامل اللعبة",
    "Game:": "لعبة:",
    "Binds:": "ارتباطات:",
    "Macro Profile:": "ملف الماكرو:",
    "Runtime Status:": "حالة التشغيل:",
    "Profile Name (Variant):": "اسم الملف (البديل):",
    "Binding Profile Name:": "اسم ملف الارتباطات:",
    "Bindings File Path (Optional):": "مسار ملف الارتباطات (اختياري):",
    "Process Name (e.g. X4.exe):": "اسم العملية (مثال: X4.exe):",
    "Game Type:": "نوع اللعبة:",
    "Game Name:": "اسم اللعبة:",
    "Process Name:": "اسم العملية:",
    "Runtime Environment:": "بيئة التشغيل:",
    
    # Advanced Features
    "External Audio Assets": "موارد صوتية خارجية",
    "Audio Directory:": "دليل الصوت:",
    "Reference File": "ملف مرجعي",
    "Sound Pool": "مجمع الأصوات",
    "Playback Mode": "وضع التشغيل",
    "Random": "عشوائي",
    "Simultaneous": "متزامن",
    "Sequential": "متسلسل",
    "Round-Robin": "دوري",
    
    # Common long phrases
    "Advanced Voice Control for Linux": "تحكم صوتي متقدم لـ لينكس",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "اضغط للتحدث",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "موافق",
    "Ctrl": "Ctrl",
    "Alt": "Alt",
    "Shift": "Shift",
    
    # Wizard setup
    "TuxTalks First-Run Setup": "الإعداد الأول لـ TuxTalks",
    "Welcome to TuxTalks! 🐧": "مرحباً بك في TuxTalks! 🐧",
    "TuxTalks is your powerful, secure, and offline voice command assistant for Linux gaming.\n\nThis wizard will help you set up your core preferences in just a few minutes so you can start talking to your favorite games and media players.": "TuxTalks هو مساعد الأوامر الصوتية القوي والآمن والذي يعمل بدون اتصال لألعاب لينكس.\n\nسيساعدك هذا المعالج في إعداد تفضيلاتك الأساسية في بضع دقائق فقط حتى تتمكن من البدء في التحدث إلى ألعابك ومشغلات الوسائط المفضلة لديك.",
    "Ready to begin?": "هل أنت مستعد للبدء؟",
    "Step 1: Interface Language": "الخطوة 1: لغة الواجهة",
    "Select the language for the TuxTalks interface:": "اختر لغة واجهة TuxTalks:",
    "Note: RTL support is automatically enabled for Arabic.": "ملاحظة: دعم RTL مفعل تلقائياً للغة العربية.",
    "Step 2: Voice Recognition (ASR)": "الخطوة 2: التعرف على الكلام (ASR)",
    "To process your voice offline, TuxTalks needs a language model.\n\nBased on your language selection, we recommend the following model:": "لمعالجة صوتك بدون اتصال، يحتاج TuxTalks إلى نموذج لغوي.\n\nبناءً على اختيارك للغة، نوصي بالنموذج التالي:",
    "Download & Install": "تنزيل وتثبيت",
    "Step 3: Initial Integration": "الخطوة 3: التكامل الأولي",
    "Choose your primary media player:": "اختر مشغل الوسائط الأساسي:",
    "Tip: You can change this and add games later in the main settings.": "نصيحة: يمكنك تغيير هذا وإضافة الألعاب لاحقاً في الإعدادات الرئيسية.",
    "All Set! 🎉": "تم كل شيء! 🎉",
    "Setup is complete. TuxTalks is now configured with your language and voice preferences.\n\nClick 'Finish' to open the main settings where you can further customize your experience, add games, and calibrate your microphone.": "اكتمل الإعداد. تم تكوين TuxTalks الآن بتفضيلات اللغة والصوت الخاصة بك.\n\nانقر فوق 'إنهاء' لفتح الإعدادات الرئيسية حيث يمكنك تخصيص تجربتك بشكل أكبر، وإضافة الألعاب، ومعايرة الميكروفون الخاص بك.",
    "Skip Setup?": "تخطي الإعداد؟",
    "Closing this window will skip the setup wizard. You can still configure everything manually in the settings.\n\nSkip and don't show again?": "إغلاق هذه النافذة سيؤدي إلى تخطي معالج الإعداد. لا يزال بإمكانك تكوين كل شيء يدويًا في الإعدادات.\n\nتخطي وعدم الإظهار مرة أخرى؟",
}

# Sentence fragments/phrases
PHRASES = {
    "Configuration saved.": "تم حفظ التكوين.",
    "TuxTalks is already running.": "TuxTalks قيد التشغيل بالفعل.",
    "Unsaved Changes": "تغييرات غير محفوظة",
    "You have unsaved changes. Save before starting?": "لديك تغييرات غير محفوظة. هل تريد الحفظ قبل البدء؟",
    "Assistant stopped.": "توقف المساعد.",
    "Please select a game first.": "يرجى اختيار لعبة أولاً.",
    "No game selected.": "لم يتم اختيار لعبة.",
    "Profile name cannot be empty.": "اسم الملف الشخصي لا يمكن أن يكون فارغاً.",
    "Failed to create macro profile.": "فشل إنشاء ملف الماكرو.",
    "Failed to delete macro profile.": "فشل حذف ملف الماكرو.",
    "Failed to rename macro profile.": "فشل إعادة تسمية ملف الماكرو.",
    "No profile selected.": "لم يتم اختيار ملف شخصي.",
    "Process Name required.": "اسم العملية مطلوب.",
    "Select a row to delete.": "اختر صفا للحذف.",
    "Delete selected correction?": "حذف التصحيح المحدد؟",
    "Perfect match! No training needed.": "تطابق تام! لا حاجة للتدريب.",
    "Correction added.": "تمت إضافة التصحيح.",
    "Test a phrase first.": "اختبر عبارة أولاً.",
    "Scaling saved. Restart required for full effect.": "تم حفظ الحجم. ملوح بإعادة التشغيل للتأثير الكامل.",
    "All detected game actions typically have voice commands assigned!\nYou can still edit existing ones.": "جميع إجراءات اللعبة المكتشفة عادةً ما يكون لها أوامر صوتية مخصصة!\nلا يزال بإمكانك تعديل الأوامر الحالية.",
    "Please select a Game grouping first.": "يرجى اختيار مجموعة ألعاب أولاً.",
    "Internal Error: Active bindings path is unknown.": "خطأ داخلي: مسار الارتباطات النشط غير معروف.",
    "Select an action to rebind.": "اختر إجراء لإعادة ربطه.",
    "No profiles found in this group.": "لم يتم العثور على ملفات في هذه المجموعة.",
    "No standard binding files found for this game type.": "لم يتم العثور على ملفات ارتباط قياسية لنوع اللعبة هذا.",
    "Failed to remove profiles.": "فشل إزالة الملفات.",
    "Name already taken.": "الاسم مستخدم بالفعل.",
    "No profiles found. (Check console for path/parsing errors)": "لم يتم العثور على ملفات. (افحص وحدة التحكم لمعرفة أخطاء المسار/التحليل)",
    "Import Complete": "اكتمل الاستيراد",
    "No profiles found.": "لم يتم العثور على ملفات.",
    "Elite Dangerous appears to be running.\n\nChanges made now may NOT take effect immediately or could be overwritten by the game.\n\nContinue anyway?": "يبدو أن Elite Dangerous قيد التشغيل.\n\nالتغييرات التي يتم إجراؤها الآن قد لا تدخل حيز التنفيذ فوراً أو قد يتم استبدالها بواسطة اللعبة.\n\nهل تريد الاستمرار على أي حال؟",
    "Scan and import standard Elite Dangerous ControlSchemes?\nThis may double up profiles if you already have them, but skips duplicate names.": "فحص واستيراد ControlSchemes القياسية لـ Elite Dangerous؟\nقد يؤدي هذا إلى تكرار الملفات إذا كانت لديك بالفعل، ولكنه يتخطى الأسماء المكررة.",
    "Importing voice in background...": "جاري استيراد الصوت في الخلفية...",
    "Downloading voice in background...": "جاري تنزيل الصوت في الخلفية...",
    "Failed to install voice.": "فشل تثبيت الصوت.",
    "Failed to import voice.": "فشل استيراد الصوت.",
}

def translate_string(english):
    """Translate an English string to Arabic."""
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
             
        arabic = translate_string(english_text)
        if arabic:
            return f'{full_msgid_part}\nmsgstr "{arabic}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Auto-translated {filepath}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ar_dir = os.path.join(script_dir, 'locale/ar/LC_MESSAGES/')
    
    if os.path.exists(ar_dir):
        for filename in os.listdir(ar_dir):
            if filename.endswith('.po'):
                auto_translate_po(os.path.join(ar_dir, filename))
        
        print("\nNext steps:")
        print("1. Review translations in locale/ar/LC_MESSAGES/")
        print("2. Compile: pybabel compile -d locale")
    else:
        print(f"Error: {ar_dir} not found")
        sys.exit(1)
