"""
RTL (Right-to-Left) Layout Helpers for TuxTalks
Provides utilities for handling RTL language layouts in Tkinter.
"""

from i18n import is_rtl, get_text_anchor, get_justify


def configure_label_rtl(label, lang=None):
    """
    Configure a label widget for RTL/LTR display.
    
    Args:
        label: ttk.Label widget
        lang: Language code (None = use current)
    """
    anchor = get_text_anchor(lang)
    justify = get_justify(lang)
    label.config(anchor=anchor, justify=justify)


def configure_entry_rtl(entry, lang=None):
    """
    Configure an entry widget for RTL/LTR display.
    
    Args:
        entry: ttk.Entry widget
        lang: Language code (None = use current)
    """
    justify = get_justify(lang)
    entry.config(justify=justify)


def get_button_pack_side(lang=None):
    """
    Get the appropriate pack side for buttons in RTL/LTR.
    
    Args:
        lang: Language code (None = use current)
    
    Returns:
        str: 'right' for RTL, 'left' for LTR
    """
    # Note: In RTL, we still pack from right to maintain visual order
    return 'right' if is_rtl(lang) else 'left'


def reverse_button_order(buttons, lang=None):
    """
    Reverse button order for RTL languages.    
    Args:
        buttons: List of button widgets
        lang: Language code (None = use current)
    
    Returns:
        list: Reversed list for RTL, original for LTR
    """
    if is_rtl(lang):
        return list(reversed(buttons))
    return buttons


def configure_treeview_rtl(tree, lang=None):
    """
    Configure a treeview for RTL display.
    Note: Tkinter treeview has limited RTL support.
    
    Args:
        tree: ttk.Treeview widget
        lang: Language code (None = use current)
    """
    # Treeview alignment is challenging in Tkinter
    # We can only set column anchors
    if is_rtl(lang):
        for col in tree['columns']:
            tree.heading(col, anchor='e')
            tree.column(col, anchor='e')
    else:
        for col in tree['columns']:
            tree.heading(col, anchor='w')
            tree.column(col, anchor='w')


def get_frame_pack_anchor(lang=None):
    """
    Get frame pack anchor for RTL/LTR.
    
    Args:
        lang: Language code (None = use current)
    
    Returns:
        str: 'e' for RTL, 'w' for LTR
    """
    return 'e' if is_rtl(lang) else 'w'
