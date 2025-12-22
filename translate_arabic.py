#!/usr/bin/env python3
"""
Arabic translation for TuxTalks using gaming-specific glossary.
Special handling for RTL text direction.
"""

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
    
    # Speech/Voice
    "Wake Word": "كلمة التنشيط",
    "Speech Recognition": "التعرف على الكلام",
    "Text-to-Speech": "النص إلى كلام",
    "Active Model": "النموذج النشط",
    "Active Voice": "الصوت النشط",
    "Voice Triggers": "محفزات صوتية",
    "Voice Corrections": "تصحيحات صوتية",
    
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
    
    # Common UI
    "Theme": "السمة",
    "Scale": "المقياس",
    "Filter": "فلتر",
    "Search": "بحث",
    "Advanced Voice Control for Linux": "التحكم الصوتي المتقدم لنظام Linux",
}

def translate_to_arabic(po_file):
    """Apply Arabic translations to .po file."""
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('msgid "'):
            msgid = line.split('msgid "')[1].rstrip('"\n')
            msgstr_line = lines[i + 1] if i + 1 < len(lines) else 'msgstr ""\n'
            
            if msgid and msgid in ARABIC_GLOSSARY:
                arabic = ARABIC_GLOSSARY[msgid]
                msgstr_line = f'msgstr "{arabic}"\n'
            
            output.append(line)
            output.append(msgstr_line)
            i += 2
        else:
            output.append(line)
            i += 1
    
    with open(po_file, 'w', encoding='utf-8') as f:
        f.writelines(output)
    
    print(f"✓ Arabic translations applied to {po_file}")

if __name__ == '__main__':
    import sys
    po_file = sys.argv[1] if len(sys.argv) > 1 else 'locale/ar/LC_MESSAGES/tuxtalks.po'
    translate_to_arabic(po_file)
    print(f"Translated {len(ARABIC_GLOSSARY)} terms")
    print("Note: Arabic is RTL (Right-to-Left) language")
