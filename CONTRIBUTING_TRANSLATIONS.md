# Contributing Translations to TuxTalks

Thank you for your interest in helping translate TuxTalks! This guide will help you contribute translations in your native language.

## 🌍 Current Translation Status

| Language | Code | Completion | Priority |
|----------|------|------------|----------|
| English | `en` | 100% (native) | - |
| Spanish | `es` | ~27% | **HIGH** (large gaming market) |
| German | `de` | ~15% | MEDIUM |
| French | `fr` | ~15% | MEDIUM |
| Ukrainian | `uk` | ~15% | MEDIUM |
| Welsh | `cy` | ~15% | LOW |
| Arabic | `ar` | ~15% | MEDIUM (RTL showcase) |

**Want to add a new language?** Open an issue and we'll set it up!

---

## 🚀 Quick Start Guide

### Option 1: For Non-Technical Contributors (Recommended)

**We'll set up a web-based translation platform (Crowdin/Weblate) soon.** Check back or star the repo for updates!

In the meantime, you can:
1. Open an issue titled "Translation improvements for [Language]"
2. List the strings you want to improve
3. We'll incorporate your suggestions

### Option 2: For Technical Contributors

#### Step 1: Set Up Development Environment

```bash
# Clone the repository
git clone https://github.com/StarTuz/tuxtalks.git
cd tuxtalks

# Install gettext tools (if not installed)
# Arch Linux / Garuda
sudo pacman -S gettext

# Ubuntu / Debian
sudo apt install gettext

# Fedora
sudo dnf install gettext
```

#### Step 2: Find Your Language File

Translation files are in `locale/[language_code]/LC_MESSAGES/tuxtalks.po`

Example:
- Spanish: `locale/es/LC_MESSAGES/tuxtalks.po`
- German: `locale/de/LC_MESSAGES/tuxtalks.po`
- French: `locale/fr/LC_MESSAGES/tuxtalks.po`

#### Step 3: Edit the .po File

Open the file with any text editor or specialized tools like **Poedit**.

**Example entry:**
```po
#: launcher.py:122
msgid "Start Assistant"
msgstr "Iniciar Asistente"   # <-- Your translation goes here
```

**Untranslated entries** look like:
```po
#: launcher.py:195
msgid "Wake Word:"
msgstr ""   # <-- Empty! Needs translation
```

#### Step 4: Translate

**Guidelines:**
- Keep formatting intact (e.g., `%s`, `{0}`, `\n`)
- Maintain the same tone (friendly, technical where needed)
- Test button/label lengths (UI space is limited)
- Use standardized gaming terminology for your language

**Example:**
```po
msgid "Enable Game Integration"
msgstr "Activar Integración de Juegos"   # Spanish
msgstr "Spielintegration aktivieren"      # German
msgstr "Activer l'intégration du jeu"    # French
```

#### Step 5: Compile and Test

```bash
# Compile your translation
msgfmt -o locale/es/LC_MESSAGES/tuxtalks.mo locale/es/LC_MESSAGES/tuxtalks.po

# Test it
python launcher.py --language es
```

#### Step 6: Submit a Pull Request

```bash
# Create a branch
git checkout -b translation-spanish-improvements

# Commit your changes
git add locale/es/LC_MESSAGES/tuxtalks.po
git commit -m "Improved Spanish translations (nn% complete)"

# Push and create PR
git push origin translation-spanish-improvements
```

---

## 📝 Translation Priorities

### **High Priority** (User-facing UI)
1. Main menu tabs (General, Voice, Games, etc.)
2. Common buttons (Start, Stop, Save, Cancel)
3. Error messages
4. Game integration screen
5. First-run setup (when implemented)

### **Medium Priority** (Advanced features)
1. Macro editor
2. Content packs tab
3. Settings descriptions
4. Help text

### **Low Priority** (Debug/Developer)
1. Advanced technical terms
2. Debug messages
3. Developer documentation

---

## 🎯 Translation Quality Guidelines

### Do's ✅
- **Use natural language** for your region
- **Test the UI** to ensure labels fit
- **Be consistent** with terminology
- **Ask questions** if context is unclear (open an issue)
- **Mark uncertain translations** with a comment:
  ```po
  # TODO: Verify "macro" translation in gaming context
  msgid "Macro Profile:"
  msgstr "Perfil de Macro:"
  ```

### Don'ts ❌
- **Don't use machine translation only** - Review and refine!
- **Don't translate technical terms** that should stay in English:
  - "Vosk", "Piper", "PTT" (Push-to-Talk)
  - File extensions (.xml, .binds)
  - JSON keys or code
- **Don't change formatting codes** like `%s`, `{0}`, `\n`
- **Don't translate brand names**: Elite Dangerous, X4 Foundations, JRiver

---

## 🛠️ Using Translation Tools

### Poedit (Recommended for Beginners)
Free GUI tool for editing .po files.

**Installation:**
- Linux: `sudo pacman -S poedit` (Arch) or `sudo apt install poedit` (Ubuntu)
- Download: https://poedit.net/

**Advantages:**
- Visual interface
- Shows translation context
- Suggests translations
- Validates formatting

### Manual Editing
Any text editor works, but specialized editors help:
- **VSCode**: Install "gettext" extension
- **Vim/Emacs**: Syntax highlighting for .po files

---

## 🌟 Translation Workflow (Automated Scripts)

We have semi-automated translation scripts for rapid initial translations:

```bash
# Generate draft translations using DeepL/Google Translate API
python translate_spanish.py

# Review and refine the output in locale/es/LC_MESSAGES/tuxtalks.po
# Human review is REQUIRED before merging!
```

**Note:** These scripts create **drafts only**. Native speaker review and refinement is essential.

---

## ❓ FAQ

### Q: How do I test my translation without installing TuxTalks?
**A:** You can compile the .mo file and set the `LANGUAGE` environment variable:
```bash
msgfmt -o locale/es/LC_MESSAGES/tuxtalks.mo locale/es/LC_MESSAGES/tuxtalks.po
LANGUAGE=es python launcher.py
```

### Q: What if a translation doesn't fit in the UI?
**A:** Use abbreviations common in your language, or open an issue to request UI adjustments.

### Q: Can I translate voice commands?
**A:** Not yet! Voice command localization is planned for v1.1+ via the LAL framework. For now, focus on UI text.

### Q: I found an error in an existing translation. How do I fix it?
**A:** Submit a PR with the fix, or open an issue describing the problem.

### Q: What about Right-to-Left (RTL) languages like Arabic?
**A:** TuxTalks has full RTL support! Just translate the strings normally - the UI will auto-adjust.

---

## 🏆 Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- App "About" section (planned)
- Release notes for translation milestones

**Top contributors** per language may be listed as "Language Maintainers."

---

## 📞 Need Help?

- **General questions**: Open a [GitHub Discussion](https://github.com/StarTuz/tuxtalks/discussions)
- **Translation issues**: Open an [Issue](https://github.com/StarTuz/tuxtalks/issues) with label `translation`
- **Quick fixes**: Comment on existing translation PRs

---

## 🎁 Translation Bounties (Future)

We're considering:
- **Translation contests** for new languages
- **Bounties** for completing high-priority languages to 100%
- **Recognition badges** for significant contributors

Stay tuned!

---

**Thank you for helping make TuxTalks accessible to gamers worldwide!** 🌍🎮🎤
