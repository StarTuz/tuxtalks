"""
TuxTalks Internationalization Support
Provides gettext translation functions for the application.
"""
import gettext
import os
import locale
import sys

# Get the directory where locale files are installed
# For pipx installations, data_files puts them in venv root
def find_locale_dir():
    """Find the locale directory in various installation scenarios."""
    
    # Try 1: Alongside this module (development/source)
    module_dir = os.path.dirname(os.path.abspath(__file__))
    locale_path = os.path.join(module_dir, 'locale')
    if os.path.exists(locale_path):
        return locale_path
    
    # Try 2: In venv root (pipx data_files installation)
    # data_files installs to sys.prefix/locale
    venv_locale = os.path.join(sys.prefix, 'locale')
    if os.path.exists(venv_locale):
        return venv_locale
    
    # Try 3: Package-relative (try to find tuxtalks package)
    try:
        import tuxtalks
        if hasattr(tuxtalks, '__file__'):
            pkg_dir = os.path.dirname(tuxtalks.__file__)
            locale_path = os.path.join(pkg_dir, 'locale')
            if os.path.exists(locale_path):
                return locale_path
    except:
        pass
    
    # Try 4: System-wide
    system_locale = '/usr/local/share/locale'
    if os.path.exists(system_locale):
        return system_locale
    
    # Fallback to module dir even if it doesn't exist (will use English)
    return os.path.join(module_dir, 'locale')

LOCALE_DIR = find_locale_dir()


def init_translation(lang=None):
    """
    Initialize translations for the application.
    
    Args:
        lang: Language code (e.g., 'es', 'de', 'fr'). If None, uses system default.
    
    Returns:
        Translation function (_)
    """
    if lang is None:
        # Try to get language from environment
        lang, _ = locale.getdefaultlocale()
        if lang:
            lang = lang.split('_')[0]  # Get just 'es' from 'es_ES'
        else:
            lang = 'en'
    
    # DEBUG
    print(f"[i18n DEBUG] Initializing translation for language: {lang}")
    print(f"[i18n DEBUG] LOCALE_DIR: {LOCALE_DIR}")
    print(f"[i18n DEBUG] LOCALE_DIR exists: {os.path.exists(LOCALE_DIR)}")
    
    try:
        # Try to load the specified language
        translation = gettext.translation(
            'tuxtalks',
            localedir=LOCALE_DIR,
            languages=[lang],
            fallback=True
        )
        translation.install()
        print(f"[i18n DEBUG] Translation loaded successfully for {lang}")
        return translation.gettext
    except Exception as e:
        print(f"[i18n DEBUG] Warning: Could not load translations for '{lang}': {e}")
        # Return identity function if translation fails
        return lambda x: x

# Default translation function (will be overridden by config)
_ = init_translation('en')

def set_language(lang):
    """
    Set the active language for translations.
    
    Args:
        lang: Language code (e.g., 'es', 'ar', 'de')
    """
    global _
    _ = init_translation(lang)


# RTL (Right-to-Left) language support
RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur']  # Arabic, Hebrew, Persian, Urdu

def is_rtl(lang=None):
    """
    Check if the specified language (or current language) is RTL.
    
    Args:
        lang: Language code to check. If None, uses current UI language.
    
    Returns:
        bool: True if language is RTL, False otherwise
    """
    if lang is None:
        from config import cfg
        lang = cfg.get("UI_LANGUAGE", "en")
    
    return lang in RTL_LANGUAGES


def get_text_anchor(lang=None):
    """
    Get appropriate text anchor for the language direction.
    
    Args:
        lang: Language code. If None, uses current UI language.
    
    Returns:
        str: 'e' for RTL (right), 'w' for LTR (left)
    """
    return 'e' if is_rtl(lang) else 'w'


def get_justify(lang=None):
    """
    Get text justification for the language direction.
    
    Args:
        lang: Language code. If None, uses current UI language.
        
    Returns:
        str: 'right' for RTL, 'left' for LTR
    """
    return 'right' if is_rtl(lang) else 'left'


def mirror_padding(padding, lang=None):
    """
    Mirror horizontal padding for RTL languages.
    
    Args:
        padding: Tuple of (left, top, right, bottom) or (horizontal, vertical)
        lang: Language code. If None, uses current UI language.
    
    Returns:
        tuple: Mirrored padding for RTL, or original for LTR
    """
    if not is_rtl(lang):
        return padding
    
    if len(padding) == 4:
        # (left, top, right, bottom) -> (right, top, left, bottom)
        return (padding[2], padding[1], padding[0], padding[3])
    elif len(padding) == 2:
        # (horizontal, vertical) stays the same
        return padding
    else:
        return padding
