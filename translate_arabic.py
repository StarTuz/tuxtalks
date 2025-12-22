#!/usr/bin/env python3
"""
Automated Arabic translation for TuxTalks using gaming-specific glossary.
Special handling for RTL text direction.
"""

import re
import os
import sys

# Arabic Gaming Glossary (English -> Arabic)
ARABIC_GLOSSARY = {
    # UI Elements
    "Settings": "الإعدادات",
    "General": "عام",
    "Voice": "الصوت",
    "Games": "الألعاب",
    "Speech Engines": "محركات الكلام",
    "Input": "الإدخال",
    "Vocabulary": "المفردات",
    "Help": "مساعدة",
    "Content Packs": "حزم المحتوى",
    "Corrections": "التصحيحات",
    "Training": "تدريب",
    "Player": "مشغل",
    
    # Actions
    "Start Assistant": "بدء المساعد",
    "Stop": "إيقاف",
    "Exit": "خروج",
    "Save Config": "حفظ الإعدادات",
    "Cancel": "إلغاء",
    "Browse": "تصفح",
    "Add": "إضافة",
    "Edit": "تحرير",
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
    "Bindings": "ربط المفاتيح",
    "Binds": "ربط المفاتيح",
    "Game Action": "إجراء اللعبة",
    "Voice Command": "أمر صوتي",
    "Mapped Key": "مفتاح مربوط",
    "Process Name": "اسم العملية",
    "Binding Profile": "ملف تعريف الربط",
    "Macro": "ماكرو",
    "Macros": "ماكروهات",
    "Profile": "ملف التعريف",
    "Game Integration": "تكامل اللعبة",
    "Runtime Status": "حالة التشغيل",
    "Runtime Environment": "بيئة التشغيل",
    "Custom Commands": "الأوامر المخصصة",
    "Game Bindings": "ربط مفاتيح اللعبة",
    "Active Profile Bindings": "روابط ملف التعريف النشط",
    
    # Speech/Voice
    "Wake Word": "كلمة التنشيط",
    "Wake Word Settings": "إعدادات كلمة التنشيط",
    "Speech Recognition": "التعرف على الكلام",
    "Speech Recognition (Vosk)": "التعرف على الكلام (Vosk)",
    "Text-to-Speech": "النص إلى كلام",
    "Text-to-Speech (Piper)": "النص إلى كلام (Piper)",
    "Active Model": "النموذج النشط",
    "Active Voice": "الصوت النشط",
    "Voice Triggers": "محفزات صوتية",
    "Voice Corrections": "تصحيحات صوتية",
    "Voice Fingerprint": "بصمة الصوت",
    "Voice Learning": "تعلم الصوت",
    "Voice Training": "تدريب الصوت",
    
    # UI Labels
    "Theme": "السمة",
    "Scale": "المقياس",
    "Filter": "فلتر",
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
    "Saved": "محفوظ",
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
    "Running": "جاري التشغيل",
    
    # Game Integration Specific
    "Game": "اللعبة",
    "Game Type": "نوع اللعبة",
    "Game Name": "اسم اللعبة",
    "Game Group": "مجموعة اللعبة",
    "Game Bindings File": "ملف ربط اللعبة",
    "Bindings Path": "مسار الربط",
    "Bindings File Path": "مسار ملف الربط",
    "Configuration Name": "اسم التكوين",
    "Profile Name": "اسم ملف التعريف",
    "Macro Profile": "ملف تعريف الماكرو",
    "Defined Macros": "الماكروات المعرفة",
    "Macro Steps": "خطوات الماكرو",
    "Delay": "تأخير",
    "Action": "إجراء",
    "Key": "مفتاح",
    "Source": "مصدر",
    "Built-in": "مدمج",
    "Custom": "مخصص",
    "Pack": "حزمة",
    
    # Wizard/Dialog
    "Add Game": "إضافة لعبة",
    "Edit Game": "تحرير لعبة",
    "Remove Game": "إزالة لعبة",
    "Add Bind": "إضافة ربط",
    "Edit Bind": "تحرير ربط",
    "Remove Bind": "إزالة ربط",
    "Default Binds": "الروابط الافتراضية",
    "Add Command": "إضافة أمر",
    "Add Game Profile": "إضافة ملف تعريف لعبة",
    "Create Profile": "إنشاء ملف تعريف",
    "Save Settings": "حفظ الإعدادات",
    "Profile Settings": "إعدادات ملف التعريف",
    "Profile Configuration": "تكوين ملف التعريف",
    
    # Steps/Process
    "Step 1": "الخطوة 1",
    "Step 2": "الخطوة 2",
    "Step 3": "الخطوة 3",
    "Select Running Game Process": "اختيار عملية اللعبة المشغلة",
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
    "Wake Word:": "كلمة التنشيط:",
    "Active Model:": "النموذج النشط:",
    "Active Voice:": "الصوت النشط:",
    "Browse Folder": "تصفح المجلد",
    "Download from URL": "تنزيل من عنوان URL",
    "Delete Voice": "حذف الصوت",
    "Import New Voice": "استيراد صوت جديد",
    "Load from File (.onnx)": "تحميل من ملف (.onnx)",
    
    # Correction/Training
    "When I hear...": "عندما أسمع...",
    "I should understand...": "يجب أن أفهم...",
    "Test & Train": "اختبار وتدريب",
    "Record": "تسجيل",
    "Dur:": "المدة:",
    "Add as Correction": "إضافة كتصحيح",
    "Targeted Train": "تدريب موجه",
    "Basic": "أساسي",
    "Advanced": "متقدم",
    "Recent Ignored/Missed Commands": "الأوامر الأخيرة المتجاهلة/المفقودة",
    
    # Key Binding
    "Press the key combination on your keyboard:": "اضغط على مجموعة المفاتيح على لوحة المفاتيح:",
    "(Example: Ctrl + Alt + H)": "(مثال: Ctrl + Alt + H)",
    "Clear": "مسح",
    "Capture": "التقاط",
    "Key to Press:": "المفتاح المطلوب ضغطه:",
    "Modifiers:": "المعدلات:",
    
    # Game-Specific
    "Game Integration Status": "حالة تكامل اللعبة",
    "Game:": "اللعبة:",
    "Binds:": "الروابط:",
    "Macro Profile:": "ملف تعريف الماكرو:",
    "Runtime Status:": "حالة التشغيل:",
    "Profile Name (Variant):": "اسم ملف التعريف (متغير):",
    "Binding Profile Name:": "اسم ملف تعريف الربط:",
    "Bindings File Path (Optional):": "مسار ملف الربط (اختياري):",
    "Process Name (e.g. X4.exe):": "اسم العملية (مثلاً X4.exe):",
    "Game Type:": "نوع اللعبة:",
    "Game Name:": "اسم اللعبة:",
    "Process Name:": "اسم العملية:",
    "Runtime Environment:": "بيئة التشغيل:",
    
    # Advanced Features
    "External Audio Assets": "أصول الصوت الخارجية",
    "Audio Directory:": "دليل الصوت:",
    "Reference File": "ملف مرجعي",
    "Sound Pool": "مجمع الأصوات",
    "Playback Mode": "وضع التشغيل",
    "Random": "عشوائي",
    "Simultaneous": "متزامن",
    "Sequential": "تسلسلي",
    "Round-Robin": "دائري",
    
    # Common long phrases (abbreviated)
    "Advanced Voice Control for Linux": "التحكم الصوتي المتقدم لنظام Linux",
    "TuxTalks": "TuxTalks",
    "Push-to-Talk": "اضغط للتحدث",
    "PTT": "PTT",
    
    # Special UI indicators
    "PID": "PID",
    "OK": "موافق",
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
    "Configuration saved.": "تم حفظ التكوين.",
    "TuxTalks is already running.": "TuxTalks قيد التشغيل بالفعل.",
    "Unsaved Changes": "تغييرات غير محفوظة",
    "You have unsaved changes. Save before starting?": "لديك تغييرات غير محفوظة. هل تريد الحفظ قبل البدء؟",
    "Assistant stopped.": "تم إيقاف المساعد.",
    "Please select a game first.": "يرجى اختيار لعبة أولاً.",
    "No game selected.": "لم يتم اختيار لعبة.",
    "Profile name cannot be empty.": "لا يمكن أن يكون اسم ملف التعريف فارغاً.",
    "Failed to create macro profile.": "فشل إنشاء ملف تعريف الماكرو.",
    "Failed to delete macro profile.": "فشل حذف ملف تعريف الماكرو.",
    "Failed to rename macro profile.": "فشل إعادة تسمية ملف تعريف الماكرو.",
    "No profile selected.": "لم يتم اختيار ملف تعريف.",
    "Process Name required.": "اسم العملية مطلوب.",
    "Select a row to delete.": "اختر صفا لحذفه.",
    "Delete selected correction?": "هل تريد حذف التصحيح المحدد؟",
    "Perfect match! No training needed.": "تطابق تام! لا حاجة للتدريب.",
    "Correction added.": "تم إضافة التصحيح.",
    "Test a phrase first.": "اختبر عبارة أولاً.",
}

def translate_string(english):
    """Translate an English string to Arabic."""
    if english in ARABIC_GLOSSARY:
        return ARABIC_GLOSSARY[english]
    if english in PHRASES:
        return PHRASES[english]
    
    trimmed = english.strip()
    if trimmed != english and trimmed in ARABIC_GLOSSARY:
        return ARABIC_GLOSSARY[trimmed]
    if trimmed != english and trimmed in PHRASES:
        return PHRASES[trimmed]
    
    if english.endswith(':'):
        base = english[:-1].strip()
        if base in ARABIC_GLOSSARY:
            return f"{ARABIC_GLOSSARY[base]}:"
        
    if english.endswith('...'):
        base = english[:-3].strip()
        if base in ARABIC_GLOSSARY:
            return f"{ARABIC_GLOSSARY[base]}..."

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
             
        arabic = translate_string(english_text)
        if arabic:
            return f'{full_msgid_part}\nmsgstr "{arabic}"'
        else:
            return match.group(0)

    new_content = pattern.sub(replace_func, content)
    
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
