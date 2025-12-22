#!/bin/bash
# TuxTalks Steam Deck Installation Script
# Optimized for SteamOS and Steam Deck hardware

set -e

echo "🎮 TuxTalks Steam Deck Installation"
echo "==================================="
echo ""

# Detect if running on Steam Deck
IS_STEAMDECK=false
if [ -f "/etc/os-release" ]; then
    if grep -q "steamdeck" /etc/os-release 2>/dev/null || grep -q "SteamOS" /etc/os-release 2>/dev/null; then
        IS_STEAMDECK=true
        echo "✅ Steam Deck / SteamOS detected"
    fi
fi

if [ "$IS_STEAMDECK" = false ]; then
    echo "⚠️  Warning: This script is optimized for Steam Deck"
    echo "   You can still install, but some features may not apply"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Ensure pipx is installed
echo ""
echo "📦 Step 1/5: Checking for pipx..."
if ! command -v pipx &> /dev/null; then
    echo "   Installing pipx..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    
    # Add to current session
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "   ✅ pipx already installed"
fi

# Step 2: Install TuxTalks
echo ""
echo "📦 Step 2/5: Installing TuxTalks..."
if pipx list | grep -q "tuxtalks"; then
    echo "   Upgrading existing installation..."
    pipx upgrade tuxtalks
else
    echo "   Installing TuxTalks..."
    pipx install tuxtalks
fi

# Step 3: Download compact Vosk model for Steam Deck
echo ""
echo "🗣️  Step 3/5: Downloading compact voice model..."
VOSK_DIR="$HOME/.cache/vosk"
VOSK_MODEL="vosk-model-small-en-us-0.15"
VOSK_URL="https://alphacephei.com/vosk/models/${VOSK_MODEL}.zip"

mkdir -p "$VOSK_DIR"

if [ ! -d "$VOSK_DIR/$VOSK_MODEL" ]; then
    echo "   Downloading $VOSK_MODEL (~40MB)..."
    cd "$VOSK_DIR"
    
    if command -v curl &> /dev/null; then
        curl -L -O "$VOSK_URL"
    elif command -v wget &> /dev/null; then
        wget "$VOSK_URL"
    else
        echo "   ❌ Error: Neither curl nor wget found"
        exit 1
    fi
    
    echo "   Extracting model..."
    unzip -q "${VOSK_MODEL}.zip"
    rm "${VOSK_MODEL}.zip"
    echo "   ✅ Voice model installed"
else
    echo "   ✅ Voice model already installed"
fi

# Step 4: Create Steam Deck config preset
echo ""
echo "⚙️  Step 4/5: Creating Steam Deck config..."
CONFIG_DIR="$HOME/.config/tuxtalks"
CONFIG_FILE="$CONFIG_DIR/config.json"

mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_FILE" << 'EOF'
{
    "VOSK_MODEL": "vosk-model-small-en-us-0.15",
    "ENABLE_WAKE_WORD": false,
    "PTT_KEY": "<ctrl>",
    "SAMPLE_RATE": 16000,
    "ENABLE_TTS": false,
    "GUI_THEME": "sun-valley-dark",
    "AUTO_START": false,
    "PERFORMANCE_MODE": "steamdeck"
}
EOF

echo "   ✅ Config created at $CONFIG_FILE"

# Step 5: Create Gaming Mode shortcut
echo ""
echo "🎮 Step 5/5: Creating Gaming Mode shortcut..."
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/tuxtalks-launcher.desktop"

mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Name=TuxTalks Launcher
Comment=Voice Control for Linux Gaming
Exec=tuxtalks-launcher
Icon=microphone
Terminal=false
Type=Application
Categories=Game;Utility;
StartupNotify=true
EOF

chmod +x "$DESKTOP_FILE"
echo "   ✅ Desktop shortcut created"

# Final instructions
echo ""
echo "✅ Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "   Desktop Mode:"
echo "   1. Launch 'TuxTalks Launcher' from application menu"
echo "   2. Configure your games in the Games tab"
echo "   3. Test voice commands (Hold Ctrl + speak)"
echo ""
echo "   Gaming Mode:"
echo "   1. Add TuxTalks as a Non-Steam game"
echo "   2. Configure before launching your game"
echo "   3. Use controller button for Push-to-Talk"
echo ""
echo "🔧 Steam Deck Optimizations Applied:"
echo "   - Compact voice model (saves RAM)"
echo "   - Push-to-Talk only (saves battery)"
echo "   - TTS disabled (saves CPU)"
echo "   - 16kHz sampling (lower quality, better performance)"
echo ""
echo "📖 Documentation: https://github.com/startux/tuxtalks"
echo ""
echo "⚠️  Note: Steam Deck support is BETA - untested on real hardware"
echo "   Please report issues on GitHub"
echo ""
