# TuxTalks

![Anti-Cheat Safe](https://img.shields.io/badge/Anti--Cheat-Safe-brightgreen?style=flat-square)
![Security Audited](https://img.shields.io/badge/Security-Audited-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Beta-orange?style=flat-square)

**TuxTalks** is a privacy-focused, accessible voice assistant for Linux gamers and media enthusiasts. It provides seamless voice control for games like Elite Dangerous and X4 Foundations, as well as powerful media library management.

> **🛡️ Anti-Cheat Certified:** TuxTalks operates entirely in user-space using standard input protocols. It does not read memory, hook processes, or modify game files in memory. It is compliant with VAC, EAC, and BattlEye safety guidelines. [See Security Audit](SECURITY_AUDIT.md).

---

## 🚀 Key Features

*   **🗣️ Voice Control**: Natural language commands for Media and Games.
*   **🎮 Game Integration**: 
    *   **Elite Dangerous**: Automatic binding sync, macros, and context awareness.
    *   **X4 Foundations**: 1:1 synchronization with `inputmap.xml`.
    *   **Generic**: Create custom voice-to-key profiles for any application.
*   **🎓 Voice Learning**: Self-improving accuracy. TuxTalks learns your voice patterns automatically (100% local).
*   **🎵 Media**: Deep integration with **JRiver Media Center**, Strawberry, Elisa, and standard MPRIS players.
*   **🌍 Multi-Language**: Support for 6 languages (EN, ES, DE, FR, UK, CY, AR) with full RTL support.
*   **📦 Content Packs**: Extensible via the **Licensed Asset Loader (LAL)** framework.

---

## 📚 Documentation

*   **[User Manual](docs/USER_MANUAL.md)**: Detailed installation and usage guide.
*   **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Solutions for common issues.
*   **[LAL Developer Reference](docs/LAL_REFERENCE.md)**: Build your own content packs.
*   **[Security Audit](SECURITY_AUDIT.md)**: Technical details on anti-cheat compliance.
*   **[Development Guide](DEVELOPMENT.md)**: Architecture and contribution guide.

---

## ⚡ Quick Start

### Installation

```bash
# Recommended: Install via pipx for isolation
pipx install tuxtalks
```

### First Run

Run the setup wizard to configure your language, microphone, and games:

```bash
tuxtalks --setup
```

### Launching

```bash
# Start the assistant (CLI mode)
tuxtalks

# Open settings GUI
tuxtalks --gui
```

---

## 🎓 Automatic Voice Learning

TuxTalks includes a revolutionary **local learning system**.
1.  **Passive Mode**: If AI corrects your command (e.g., "Play Ever" -> "Play ABBA"), TuxTalks learns this correction permanently.
2.  **Active Mode**: Use the **Training Tab** in the GUI to teach specific phrases.
3.  **Privacy**: All data is stored locally in `~/.local/share/tuxtalks/voice_fingerprint.json`. Nothing is ever uploaded.

---

## 🤝 Contributing

We welcome contributions!
*   **Translations**: Help us reach more languages. [See Guide](CONTRIBUTING_TRANSLATIONS.md).
*   **Code**: Check out [DEVELOPMENT.md](DEVELOPMENT.md).
*   **Packs**: Create and share macro packs using LAL.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
