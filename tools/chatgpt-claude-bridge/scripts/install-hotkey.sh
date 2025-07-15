#!/bin/bash
# Install keyboard shortcut for ChatGPT-Claude Bridge

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_SCRIPT="$SCRIPT_DIR/save-clipboard-to-claude.sh"

echo "🔧 Setting up ChatGPT-Claude Bridge keyboard shortcut..."

# Detect desktop environment
if [ "$XDG_CURRENT_DESKTOP" = "GNOME" ] || [ "$DESKTOP_SESSION" = "gnome" ]; then
    echo "📱 Detected GNOME desktop environment"
    
    # Check if gsettings is available
    if command -v gsettings &> /dev/null; then
        # Improved GNOME setup using custom0 path
        SCRIPT_PATH="$(realpath "$BRIDGE_SCRIPT")"
        SHORTCUT_COMMAND="bash $SCRIPT_PATH"
        
        gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings \
          "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"
        
        gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ name "'Claude Bridge'"
        gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ command "'$SHORTCUT_COMMAND'"
        gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ binding "'<Ctrl><Alt>c'"
        
        echo "✅ GNOME keyboard shortcut installed: Ctrl+Alt+C"
    else
        echo "❌ gsettings not found. Please install dconf-tools."
        exit 1
    fi
    
elif [ "$XDG_CURRENT_DESKTOP" = "KDE" ] || [ "$DESKTOP_SESSION" = "plasma" ]; then
    echo "📱 Detected KDE desktop environment"
    echo "⚠️  KDE setup requires manual configuration:"
    echo "   1. Open System Settings → Shortcuts → Custom Shortcuts"
    echo "   2. Add new shortcut with command: $BRIDGE_SCRIPT"
    echo "   3. Set trigger: Ctrl+Alt+C"
    
else
    echo "❓ Unknown desktop environment: $XDG_CURRENT_DESKTOP"
    echo "📋 Manual setup required:"
    echo "   1. Add keyboard shortcut in your desktop environment"
    echo "   2. Set command: $BRIDGE_SCRIPT"
    echo "   3. Set trigger: Ctrl+Alt+C (or your preference)"
fi

echo ""
echo "🎯 Setup complete! Test the bridge:"
echo "   1. Copy text to clipboard"
echo "   2. Press Ctrl+Alt+C"
echo "   3. Check: $(dirname "$BRIDGE_SCRIPT")/../input.md"