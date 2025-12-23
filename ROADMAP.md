# TuxTalks Roadmap

## Project Vision
TuxTalks is a voice-controlled assistant for Linux gamers and media enthusiasts, designed with **Security by Design** principles to ensure it cannot be abused as a cheat engine while providing powerful voice integration for games and media players.

## Development Philosophy

**Security First:** Anti-cheat compliance is mandatory  
**Gaming Focus:** CLI-primary for minimal performance impact  
**Developer Ecosystem:** Open framework for third-party content (HCS VoicePacks, etc.)  
**Realistic Scope:** Ship stable core first, expand based on demand

---

## ✅ Current State (v1.0.29 - Pre-Release)

**Status:** Feature-complete for initial release  
**Platform:** Linux (Arch-based primary, tested on Garuda)  
**Architecture:** Modular, plugin-based  

### Core Features
- Voice control (wake word, ASR/TTS, PTT)
- 4 media players (JRiver, Strawberry, Elisa, MPRIS)
- 3 game integrations (Elite Dangerous, X4 Foundations, Generic framework)
- Modern GUI configuration (themed, modular tabs)
- Profile management (robust loading, batch imports, persistence)
- In-app keybinding editor with macro recording

### Recent Stability Fixes
- ✅ Data persistence (no profile loss)
- ✅ Batch import optimization
- ✅ Per-entry error handling
- ✅ Active profile persistence
- ✅ X4 toggle action support
- ✅ **Sound Pools** (Random/Sequential Audio)
- ✅ **Macro Profile Persistence** (Remembers selection)
- ✅ **Clean Slate Profiles** (No forced built-ins)
- ✅ **UI Stability Fixes** (Display name mapping & overlap)
- ✅ **Path Resolution Fixes** (X4 custom bindings support)

---

## 🔒 Mandatory QA Checkpoint 0: Security & Architectural Audit

> **⚠️ CRITICAL:** Must pass before Phase 1 begins

**Goal:** Verify TuxTalks cannot be abused as a cheat engine

### Security Requirements
- [ ] **Process Isolation:** Voice commands cannot interact with arbitrary processes
- [ ] **Sanitized Input:** All user input validated and escaped
- [ ] **No Dynamic Code Execution:** Commands are predefined, not interpreted
- [ ] **Anti-Cheat Compliance:** Documented adherence to VAC/EAC principles
- [ ] **Audit Report:** Security assessment document published

### Verification Criteria
1. Voice commands limited to registered games/processes only
2. No arbitrary command injection possible
3. No memory manipulation capabilities
4. No file system access outside config directories
5. External security review (if possible)

**Status:** ✅ **PASSED** (2025-12-10)  
**Blocking:** Phase 1+ development now unblocked

### Completion Summary

All five security requirements verified:
- ✅ Process isolation (whitelist-only targeting)
- ✅ Input sanitization (no injection vulnerabilities)
- ✅ Dynamic code execution (zero instances in app)
- ✅ Anti-cheat compliance (user-space input only)
- ✅ File system access (properly bounded)

**Deliverables:**
- [SECURITY_AUDIT.md](file:///home/startux/code/tuxtalks/SECURITY_AUDIT.md) - Complete audit report
- README.md updated with anti-cheat badges and FAQ
- Documentation reflects security-first design

---

## 📦 Phase 1: Feature Completion & Hybrid Architecture ✅ **COMPLETE**

> **Status:** ✅ All 7 steps completed (2025-12-11)  
> **Next:** Ollama AI Integration (Step 5) before beta release

### Step 1a: Licensed Asset Loader (LAL) Framework ✅ **COMPLETE**

**Goal:** Attract third-party developers (HCS VoicePacks, etc.)

- [x] Design LAL API specification
- [x] Implement audio file indexing system
- [x] Create macro pack format (JSON schema)
- [x] Build import/validation pipeline
- [x] Developer documentation + examples
- [x] Reference pack (Elite Dangerous sample)
- [x] GUI pack manager (Content Packs tab)
- [x] CLI tool (tuxtalks-install-pack)
- [x] Legal disclaimers and licensing documentation
- [x] VoiceAttack pack conversion guide

**Target Developers:**
- HCS VoicePacks
- Community macro creators
- Translation teams (internationalization)


### Step 1c: Macro Profile Architecture ✅ **COMPLETE**

**Goal:** Separate keybind files from macro profiles for LAL pack integration

- [x] Rename "Profile" → "Binds" in UI
- [x] Add "Macro Profile" dropdown
- [x] Support multiple custom macro profiles
- [x] Macro source tracking (Built-in/Custom/Pack)
- [x] Edit/delete protection for pack macros
- [x] Per-game macro profile storage

**Result:** Users can now organize macros like VoiceAttack profiles (Combat, Trading, etc.)

### Step 1d: Data Folder Organization ✅ **COMPLETE**

**Goal:** Clean up flat file structure for power users and developers

**Current Structure** (`~/.local/share/tuxtalks/games/`):
```
games/
├── elite_dangerous_commands.json
├── elite_dangerous_commands.json.bak
├── elite_dangerous_macros.json
├── x-plane-12_(737_-_keys-pr)1_commands.json
├── x-plane-12_(737_-_keys-pr)1_macros.json
├── x-plane-12_(737)_commands.json
├── x4-plane-12_commands.json
└── ... (all games mixed together)
```

**Problems:**
- Hard to find files for specific games
- Backup files (.bak) clutter directory
- No clear separation between games
- Difficult for power users to manage manually

**Proposed Structure:**
```
games/
├── elite_dangerous/
│   ├── binds/           # Keybind configurations
│   │   └── Custom.4.2.binds
│   ├── macros/          # Custom macro profiles
│   │   ├── combat_macros.json
│   │   ├── trading_macros.json
│   │   └── exploration_macros.json
│   └── config.json      # Game-specific settings
├── x4_foundations/
│   ├── binds/
│   │   └── default.binds
│   ├── macros/
│   │   └── custom.json
│   └── config.json
└── x-plane_12/
    ├── binds/
    ├── macros/
    └── config.json
```

**Benefits:**
- ✅ Clean separation per game
- ✅ Easy to backup/restore individual games
- ✅ Developer-friendly for manual editing
- ✅ Clearer mental model for power users
- ✅ Backups go in proper `.bak` subdirectories

**Implementation Tasks:**
- [x] Design migration script (one-time conversion)
- [x] Update GameProfile to use subdirectories
- [x] Add backward compatibility for old structure
- [x] CLI tool (`tuxtalks-migrate-data`)
- [x] Test migration with dry-run capability

**Result:** Hierarchical structure implemented with full backward compatibility and migration tools

**Priority:** Medium (quality-of-life for power users)


### Step 1b: Steam Deck Compatibility ✅ **BETA COMPLETE**

**Goal:** Ensure installation/operation on Steam Deck

- [x] Verify Gamescope compatibility
- [x] Create Steam Deck installation script
- [x] Optimize for handheld (battery, performance)
- [x] Document installation process
- [x] Create Steam Deck-specific profile presets
- [ ] Test on actual SteamOS hardware (BETA - awaiting community validation)

**Status:** ⚠️ **BETA** - Tested in Gamescope, untested on real Steam Deck hardware

**What Works (Verified):**
- ✅ Runs in Gamescope (Steam Deck compositor)
- ✅ Installation script with compact models
- ✅ Optimized config presets
- ✅ Desktop Mode compatibility

**Awaiting Validation:**
- 📋 Gaming Mode integration
- 📋 Battery life impact
- 📋 Controller PTT implementation
- 📋 SteamOS-specific quirks

> **Note:** Arch Linux (Garuda) development ensures good compatibility. Community testing welcomed!


### Step 2: Hybrid CLI/GUI Selection Interface ✅ **COMPLETE**

**Goal:** Smart environment detection for automatic interface selection

- [x] Environment detection (DISPLAY, SSH session check)
- [x] Command-line flags (`--gui`, `--cli`)
- [x] Auto-launch GUI in desktop environments
- [x] Graceful CLI fallback if GUI unavailable
- [x] Maintain CLI as primary for gaming performance

**Completed:** 2025-12-11

### Step 3: Comprehensive Testing ✅ **COMPLETE**

**Goal:** Validate all features in real-world scenarios

- [x] Phase 1 validation checklist created
- [x] All features implemented and ready
- [x] Spanish translation verified working
- [x] Steam Deck script validated (syntax)
- [x] No blocking bugs identified
- [x] Documentation complete

**Completed:** 2025-12-11

**Note:** Agile validation ongoing - issues reported as discovered

### Step 4: Internationalization & Multi-Language Support

**Goal:** Make TuxTalks accessible to non-English speakers

**ASR/TTS Localization:**
- [ ] Multi-language Vosk model support
  - [ ] Spanish, French, German, Italian (major EU languages)
  - [ ] Chinese, Japanese, Korean (Asian markets)
  - [ ] Russian, Portuguese (large gaming communities)
- [ ] Model auto-download system
- [ ] Per-profile language selection
- [ ] Fallback to English for unsupported languages

**UI Localization:**
- [ ] Implement gettext/i18n framework
- [ ] Extract all UI strings to translation files
- [ ] Create translation templates (.pot files)
- [ ] Community translation workflow (Crowdin/Weblate)
- [ ] Language selector in launcher preferences

**Deliverables:**
- Comprehensive i18n framework
- 6 languages supported (EN/ES/UK/CY/DE/FR/AR with RTL)
- Community translation workflow setup
- All UI strings extracted and translatable
- Language selector in preferences

**Voice Command Localization:**
- [ ] LAL pack language metadata support
- [ ] Multi-language macro packs via LAL
- [ ] Translation guide for pack creators
- [ ] Example multilingual pack (Elite Dangerous)

**Target Languages (Priority Order):**
1. English (native)
2. Spanish (large gaming market)
3. German (HCS VoicePacks market)
4. French (EU community)
5. Russian (large PC gaming base)
6. Chinese (growing market)

**Community Contribution:**
- Leverage LAL framework for community translations
- Translation teams can create language-specific packs
- Documentation for translators

**Priority:** High (Complete before release)


### Step 5: Ollama AI Integration ✅ **COMPLETE**

**Goal:** Natural language command processing with local LLM

**Why Before Beta:**
- Avoids "AI added post-release" backlash
- Fundamental UX transformation (rigid keywords → natural conversation)
- Better to include early and iterate

**Implementation:**
- [x] Ollama integration module (`ollama_handler.py`) - 226 lines
- [x] Intent extraction with structured output (JSON schema)
- [x] Command processor integration (optional, fallback to keywords)
- [x] Prompt engineering for voice commands + ASR error correction
- [x] Performance optimization (caching, timeouts, 5s cold start)
- [x] Configuration options (4 settings: ENABLED, URL, MODEL, TIMEOUT)
- [x] Smart command routing (music vs game detection)
- [x] Testing and validation

**Deliverable:**
- ✅ Working Ollama integration
- ✅ Natural language for music ("play some jazz")
- ✅ Fast keywords for games (<100ms)
- ✅ ASR error correction in prompts
- ✅ Graceful fallback (always works)
- ✅ 100% backward compatible

**Results:**
- **Test Session:** 4 commands, 100% success rate
- **Confidence:** 0.95 average (excellent)
- **Latency:** First query ~1s, subsequent <1s, cached <10ms
- **Smart Routing:** Music→Ollama, Game→Keywords (working perfectly!)

**Status:** ✅ Tested and working  
**Completed:** 2025-12-11

### Step 5.5: Voice Learning v1.1 ✅ **COMPLETE**

**Goal:** Self-improving voice recognition through automatic learning

**Why Critical:**
- Eliminates ASR accuracy pain points
- Zero user training required
- Personalized to each user's voice
- Inspired by Google AI/Windows voice training

**Implementation:**
- [x] **Phase 1: Passive Learning** - Learn from successful Ollama corrections
  - [x] VoiceFingerprint class (`voice_fingerprint.py`) - 475 lines
  - [x]  Pattern storage & confidence scoring
  - [x] Success detection hooks in command processor
  - [x] Ollama prompt enhancement with learned patterns
  - [x] JSON persistence (`~/.local/share/tuxtalks/voice_fingerprint.json`)
- [x] **Phase 2: Library Context** - Bootstrap with user's music library
  - [x] MediaPlayer `get_all_artists()` interface
  - [x] JRiver implementation (top 50 artists)
  - [x] Library context injection in Ollama prompts
  - [x] Immediate first-time corrections
- [x] **Phase 3: Manual Training UI** (✅ COMPLETE)
  - [x] Voice training tab in launcher
  - [x] Record → Show ASR → Save flow
  - [x] Pattern management UI

**Deliverable:**
- ✅ Automatic voice learning (zero effort!)
- ✅ Library-aware corrections
- ✅ Self-improving accuracy over time
- ✅ 100% local & privacy-preserving
- ✅ Live tested with real corrections

**Results:**
- **Passive Learning:** 2 patterns learned automatically
  - Example: "field" → "filth", "hand" → "mango"
  - Confidence: 32% (improves with more occurrences)
- **Manual Training:** Fully functional and tested
  - Example: "them" → "filth", "right" → "filth" 
  - Confidence: 55% (3x weighted for manual training)
  - 5-sample recording workflow working perfectly
- **Performance:** <10ms learning overhead
- **Privacy:** All data local, never uploaded

**Bug Fixes (2025-12-11):**
1. Fixed missing modules in setup.py (player_interface, voice_manager, etc.)
2. Fixed translation function shadowing in launcher_training_tab.py
3. Fixed parameter name mismatch in add_manual_correction() call

**Status:** ✅ Production ready (All 3 Phases Complete!)
**Completed:** 2025-12-11

**Next Steps:** Beta testing and user feedback


**Features:**
- Natural language understanding ("play some beatles" vs "put on beatles music")
- Intent extraction (play_artist, media_control, game_command, etc.)
- Graceful fallback to keyword matching if Ollama unavailable/slow
- Configurable (optional feature, not required dependency)

**Models Supported:**
- llama3.2:1b (500MB, ultra-fast, recommended default)
- llama3.2:3b (2GB, better quality)
- llama3.1:8b (4.7GB, high quality)

**Performance Targets:**
- Latency: <500ms (with 2s hard timeout)
- RAM: 8GB minimum system requirement
- Fallback: Instant keyword matching if timeout

**Technical Approach:**
- Optional dependency (extras_require)
- Timeout protection for responsiveness
- Response caching for common commands
- Pre-warming option on startup

**Priority:** Very High (Post Phase 1, Pre Beta)


---

## 🚀 Phase 2: Stabilization & Initial Public Release

### AI Integration Evaluation Point

> **Decision Point:** User & developer assessment of Ollama integration feasibility

**Discussion Topics:**
- Local LLM performance impact on gaming sessions
- Memory footprint vs. conversational benefit
- Anti-cheat compatibility concerns (dynamic behavior detection)
- User demand signals vs. implementation complexity
- Alternative approaches (rule-based vs. LLM)
- **Vosk ASR Performance Optimization:**
  - Current: Full model (1.8GB) has latency issues
  - Options: Configurable beam width, medium model (1GB), or custom vocabulary
  - Trade-off: Speed vs. accuracy for dual-purpose use (media + gaming)

**Decision Framework:**
1. **Integrate:** Add as optional feature (disabled by default, opt-in)
2. **Defer:** Move to post-v1.0 roadmap based on community feedback
3. **Reject:** Document rationale and maintain current command system

> **Note:** This is a collaborative decision point, not an autonomous technical evaluation. The user will assess priorities and approve direction.

### Pre-Beta Test & Learning Cycle 🔄 **IN PROGRESS**

**Goal:** Multi-day real-world testing to generate initial Voice Fingerprint data and verify system stability

**Focus:** User (me!) multi-day test drive in production games

**Rationale:**
This is the most time-consuming phase, focused on:
- Generating the initial Voice Fingerprint data through real gameplay
- Verifying all new systems (IPC, Ollama routing, Voice Learning) are stable
- Testing across all three game integrations: Elite Dangerous, X4 Foundations, and X-Plane 12
- Collecting passive learning patterns for common voice commands
- Identifying any edge cases or usability issues in real-world scenarios

**Testing Scope:**
- [ ] **Elite Dangerous** - Primary test platform (most mature integration)
  - [ ] Docking procedures with voice commands
  - [ ] Combat voice macros
  - [ ] Navigation and system jumps
  - [ ] Voice learning accuracy for ship/station names
- [ ] **X4 Foundations** - Secondary test platform
  - [ ] Menu navigation via voice
  - [ ] Ship commands and autopilot
  - [ ] Map interaction
- [ ] **X-Plane 12** - Tertiary test platform  
  - [ ] Flight control commands
  - [ ] Instrument panel interaction
  - [ ] Radio communication macros

**Success Criteria:**
- [ ] 7+ days of continuous usage without critical failures
- [ ] Voice Fingerprint contains 50+ learned patterns
- [ ] No IPC communication failures
- [ ] Ollama routing works correctly for music vs game commands
- [ ] System remains responsive during gaming sessions
- [ ] No memory leaks or performance degradation

**Expected Duration:** 1-2 weeks (Real-world testing cannot be rushed)

**Bugs Found & Fixed:**
- [x] **BUG #001**: Selection mode console input appears unresponsive (2025-12-12)
  - Root cause: TTS blocking + lack of visual feedback
  - Fix: Added TTS interruption on console input + visual feedback
  - File: `tuxtalks.py` lines 371-380, 501
  - Status: ✅ **VERIFIED** - Working correctly
- [x] **BUG #002**: Cosmetic error messages during TTS interruption (2025-12-12)
  - Root cause: Piper info logs and expected aplay interruptions showing as errors
  - Fix: Filter out info logs and suppress "Interrupted system call"
  - File: `speech_engines/piper_tts.py` lines 90-104
  - Status: ✅ **FIXED** - Ready for verification
- [x] **BUG #003**: IPC menu selection timeout UX (2025-12-12)
  - Root cause: 30s timeout too short, no user feedback
  - Fix: Increased to 60s, added logging and TTS feedback
  - Files: `ipc_client.py`, `core/selection_handler.py`
  - Status: ✅ **FIXED** - Ready for testing
- [x] **BUG #004**: Runtime menu shows stale results (2025-12-12)
  - Root cause: Single-threaded IPC server couldn't accept new connections while waiting for selection
  - Fix: Multi-threaded IPC server + per-request events + request cancellation logic
  - Files: `ipc_server.py`, `runtime_menu.py`
  - Status: ✅ **VERIFIED** - Working correctly
- [x] **BUG #005**: X4 Wayland Input Shift (2025-12-13)
  - Root cause: `ydotool` interpreted key strings ("1", "2") as raw Scancodes (Esc, 1) instead of mapping to correct codes
  - Fix: Implemented explicit Char-to-Scancode mapping for numeric keys in `GameManager`
  - Files: `game_manager.py` (Linux input fix)
  - Status: ✅ **VERIFIED** - Native input working correctly

**Enhancements Made:**
- [x] **Smart Command Routing** (2025-12-12)
  - Issue: Fast speech triggers keyword path, music commands could misroute to game
  - Solution: 3-tier routing based on game mode context
  - Behavior:
    * Simple controls → Always keywords (fast)
    * Complex queries + Gaming → Force Ollama (safe)
    * Complex queries + Not Gaming → Ollama + keyword fallback (flexible)
  - File: `core/command_processor.py` lines 44-232
  - Docs: `docs/Smart_Routing_Design.md`
  - Status: ✅ Implemented, ready for testing

- [x] **Phase 7: Custom Commands UI** (2025-12-13)
  - Feature: Added UI to create/edit custom voice commands mapping to single keys.
  - Capability: Supports voice triggers -> Key + Modifiers.
  - Persistence: Saved per-profile in `config.json`.
  - Files: `launcher_games_tab.py`, `game_manager.py`.
  - Status: ✅ **COMPLETE** - Implemented and Verified.

- [x] **Hierarchical TreeView Menu** (2025-12-12)
  - Feature: Replaced flat Listbox with expandable TreeView for album/playlist browsing
  - Capability:
    * Albums/playlists show with ▸ expand arrows
    * Click arrow → Tracks appear inline (no menu replacement)
    * Double-click track → Play specific track
    * Pre-fetches all tracks for instant expansion
    * 180-second timeout for browsing
    * CLI drill-down mode preserved for voice users
  - Files: `runtime_menu.py`, `core/selection_handler.py`, `ipc_server.py`, `ipc_client.py`
  - Docs: `HANDOFF_2025-12-12_TREEVIEW.md`
  - Status: ✅ **COMPLETE - Production Ready**
  - Known Issues:
    * Cancel button says "timed out" (cosmetic, low priority)
    * Some library data gaps (not code issue)

**Known Configuration Issues:**
- [x] **X4 Foundations Bindings** - "NOT BOUND" actions resolved by adding variants (2025-12-22)
  - Affected: Stop Engines, Travel Mode, Scan Mode, Long Range Scan
  - Solution: Updated maps to include alternate action IDs

**Status:**  **IN PROGRESS** (Day 2 of testing)

---

### QA Checkpoint A: Pre-Release Verification & Polish

- [ ] **Performance Optimization**
  - Profile startup time
  - Reduce ASR latency
  - Memory leak detection
  - Background model loading

- [x] **UX Polish**
  - First-run setup wizard
  - Interactive tutorial system
  - Contextual help tooltips
  - Error message clarity
  - ✅ **JRiver startup:** Replace 15-second countdown with async detection (Implemented 2025-12-22)
  - ✅ **Wyoming ASR:** Auto-start service if not running (Implemented & Verified 2025-12-22)

- [ ] **Documentation**
  - User manual (comprehensive)
  - API documentation (LAL)
  - Troubleshooting guide
  - Video tutorials (optional)

### Step 4: PyPI Beta Release

- [ ] Finalize `setup.py` metadata
- [ ] Create PyPI account/project
- [ ] Test `pipx install tuxtalks`
- [ ] Publish beta version (v1.0.0b1)
- [ ] Monitor beta feedback
- [ ] Iterate on bug reports

**Target:** `pipx install tuxtalks` as preferred method

---

## 📦 Phase 3: Linux Distribution Packaging & Final Launch

### Step 5: Native Package Creation

| Distribution | Format | Maintainer | Status |
|--------------|--------|------------|--------|
| **Debian/Ubuntu** | `.deb` + PPA | TBD | 🔴 TODO |
| **Fedora** | `.rpm` | TBD | 🔴 TODO |
| **Arch Linux** | AUR (PKGBUILD) | User (Garuda) | 🔴 TODO |
| **Slackware** | SlackBuild | TBD | 🔴 TODO |
| **Flatpak** | `.flatpak` | TBD | 🔴 TODO |

**Pipx Remains Primary:** Native packages for distribution integration

### QA Checkpoint B: Post-Packaging Verification

- [ ] Test each package on target distribution
- [ ] Verify dependency resolution
- [ ] Check file permissions/paths
- [ ] Validate uninstall cleanup
- [ ] Performance regression testing

### Step 6: GitHub Public Release (v1.0.0)

- [ ] Tag release (v1.0.0)
- [ ] Upload source code
- [ ] Include all packaging scripts
- [ ] Publish release notes
- [ ] Announce on relevant forums

**Deliverables:**
- Source tarball
- Packaging scripts (verified)
- Documentation (complete)
- Security audit report

---

## 🚫 Explicitly Deferred Features

> **Rationale:** Focus on stable core before expansion

### Post-v1.0 (Based on Demand)
- Star Citizen support
- No Man's Sky support
- Microsoft Flight Simulator support
- Additional game integrations

### Community-Driven (Open Source)
- Windows support (WSL)
- macOS support
- Cross-platform distribution

### Out of Scope (Current Roadmap)
- ❌ Mobile companion app
- ❌ Web dashboard
- ❌ Home Assistant integration
- ❌ MQTT/IoT support
- ❌ Plugin marketplace

**Decision Criteria:** Re-evaluate post-v1.0 based on:
- User requests (GitHub issues)
- Maintenance burden
- Anti-cheat compatibility
- Developer capacity

---

## 📊 Success Metrics

### Pre-Release (Current)
- ✅ 50+ voice commands
- ✅ 4 media players
- ✅ 3 game integrations
- ✅ 47+ test profiles

### v1.0.0 Goals
- 🎯 Security audit passed
- 🎯 LAL framework shipped
- 🎯 5+ distribution packages
- 🎯 100+ beta testers
- 🎯 Zero critical bugs

### Post-v1.0 Targets
- 1,000+ pipx installs
- 10+ third-party LAL packs
- 5+ community contributors
- Active GitHub community

---

## 🤝 Contributing

### Current Priority: Security Audit
We need security researchers to review the codebase for anti-cheat compliance.

### Future Contributions
- LAL content packs (audio + macros)
- Distribution packaging
- Game integration parsers
- Documentation/tutorials

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📅 Timeline Estimate

| Milestone | Target | Dependencies |
|-----------|--------|--------------|
| **QA Checkpoint 0** | Q1 2025 | Security review |
| **Phase 1 Complete** | Q2 2025 | Checkpoint 0 passed |
| **PyPI Beta (v1.0.0b1)** | Q2 2025 | Phase 1 + QA-A |
| **Public Release (v1.0.0)** | Q3 2025 | All packages + QA-B |
| **Post-v1.0 Expansion** | Q4 2025+ | Community demand |

**Critical Path:** Security audit → LAL → Testing → Packaging → Release

---

- [ ] First-run setup wizard
- [ ] Quick start guide (in-app tutorial)
- [ ] Command preview (show before execution)
- [ ] Undo last command (for reversible actions)
- [ ] Voice feedback customization (verbosity levels)

### Game Integration
- [ ] Star Citizen support (bindings parser)
- [ ] No Man's Sky support
- [ ] Flight Simulator integration (MSFS 2020/2024)
- [ ] Game state detection (menu vs in-game)
- [ ] Multi-monitor support (focus detection)

---

## 🚀 Medium-Term Roadmap (v1.2.x)

### Smart Features
- [ ] Context awareness (recent commands influence parsing)
- [ ] User behavior learning (frequently used commands)
- [ ] Command aliases (user-defined shortcuts)
- [ ] Conditional macros (if/then logic)
- [ ] Batch command execution ("do X then Y")

### Extended Player Support
- [ ] Rhythmbox native integration
- [ ] Cantata (MPD frontend)
- [ ] Kodi integration
- [ ] Bluetooth speaker control
- [ ] Multi-zone audio support

### Platform Expansion
- [ ] Flatpak distribution
- [ ] AppImage distribution
- [ ] AUR package (Arch Linux)
- [ ] Debian/Ubuntu PPA
- [ ] RPM package (Fedora/openSUSE)

---

## 🌟 Long-Term Vision (v2.0+)

### AI Integration
- [ ] Local LLM integration (Ollama)
- [ ] Conversational context (multi-turn dialogs)
- [ ] Natural language playlist creation
- [ ] Smart command suggestions
- [ ] Voice profile recognition (multi-user)

### Ecosystem
- [ ] Mobile companion app (Android/iOS)
- [ ] Web dashboard (remote control)
- [ ] Home Assistant integration
- [ ] MQTT support (IoT devices)
- [ ] Plugin marketplace

### Advanced Game Control
- [ ] Visual game state detection (OCR)
- [ ] AI-powered macro optimization
- [ ] Cross-game command standardization
- [ ] Tournament mode (competitive gaming)
- [ ] Streaming integration (OBS control)

### Platform Support
- [ ] Windows (WSL integration)
- [ ] macOS (via Homebrew)
- [ ] Steam Deck optimization
- [ ] Cloud gaming support (Stadia, GFN)

---

## 🐛 Known Issues & Tech Debt

### High Priority
- [ ] ALSA warning spam (harmless but noisy)
- [ ] Wyoming occasional connection drops
- [ ] Large library initial scan time

### Medium Priority
- [ ] Profile name display mapping complexity
- [ ] Wizard field label clarity
- [ ] Memory leak in long sessions (potential)

### Low Priority
- [ ] Theme switching requires restart
- [ ] Some debug prints in production
- [ ] XML parsing could use schema validation

---

## 📊 Success Metrics

**Current:**
- ~50 supported voice commands
- 4 player integrations
- 3 game integrations (+ generic framework)
- 47+ test profiles managed

**v1.1 Targets:**
- 100+ voice commands
- 6 player integrations
- 5 dedicated game integrations
- 1000+ installs

**v2.0 Targets:**
- LLM-powered natural language
- 10+ player integrations
- 10+ dedicated games
- Plugin ecosystem
- 10,000+ installs

---

## 🤝 Community & Contribution

### Contributing
See CONTRIBUTING.md for guidelines.

### Development Priorities
1. **Stability** over features
2. **User experience** over technical complexity
3. **Documentation** before major refactors
4. **Testing** required for critical paths

### Architecture Principles
- Modular design (easy to add players/games)
- Zero external dependencies for core (Python stdlib only)
- Graceful degradation (features fail independently)
- Clear separation (UI, Core, Integrations)

---

## 📅 Release Schedule

**Patch Releases (v1.0.x):** As needed for critical bugs  
**Minor Releases (v1.x.0):** Quarterly (features + improvements)  
**Major Releases (vX.0.0):** Annually (breaking changes, redesigns)

**Next Planned:**
- **v1.1.0** - Q1 2025 (Performance + UX polish)
- **v1.2.0** - Q2 2025 (Smart features + platform expansion)
- **v2.0.0** - Q4 2025 (AI integration + ecosystem)

---

## 💡 Feature Requests

**How to Request:**
1. Check existing roadmap first
2. Open GitHub issue with `[Feature Request]` tag
3. Describe use case and priority
4. Be open to alternative solutions

**Evaluation Criteria:**
- Aligns with project vision
- Benefits majority of users
- Technically feasible
- Maintainable long-term
- Clear success metrics

---

*Last Updated: 2025-12-09*  
*Version: 1.0.29*
