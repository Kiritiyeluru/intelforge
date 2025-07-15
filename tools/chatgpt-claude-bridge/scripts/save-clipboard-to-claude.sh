#!/bin/bash
# ChatGPT-Claude Bridge: Enhanced clipboard to Claude workflow
# Usage: Run manually or bind to keyboard shortcut (Ctrl+Alt+C)

# Load configuration if available
CONFIG_FILE="$(dirname "$(realpath "$0")")/../configs/bridge-config.env"
[[ -f "$CONFIG_FILE" ]] && source "$CONFIG_FILE"

# Configuration with defaults
BRIDGE_DIR="${CUSTOM_BRIDGE_DIR:-$HOME/alpha_projects/intelforge/tools/chatgpt-claude-bridge}"
TARGET="${CUSTOM_TARGET:-$BRIDGE_DIR/input.md}"
ARCHIVE_DIR="${CUSTOM_ARCHIVE_DIR:-$BRIDGE_DIR/archive}"
ARCHIVE_ENABLED="${ARCHIVE_ENABLED:-false}"
AUTO_RUN_CLAUDE="${AUTO_RUN_CLAUDE:-false}"
ENABLE_NOTIFICATIONS="${ENABLE_NOTIFICATIONS:-true}"
ENABLE_CLEANUP="${ENABLE_CLEANUP:-true}"
ENABLE_SAFETY_CHECK="${ENABLE_SAFETY_CHECK:-true}"

# Ensure directories exist
mkdir -p "$(dirname "$TARGET")" "$ARCHIVE_DIR"

# Get clipboard content
if command -v wl-paste &> /dev/null; then
    # Wayland
    CLIPBOARD_CONTENT=$(wl-paste)
elif command -v xclip &> /dev/null; then
    # X11
    CLIPBOARD_CONTENT=$(xclip -selection clipboard -o)
else
    echo "❌ Error: No clipboard tool found (need wl-paste or xclip)"
    [[ "$ENABLE_NOTIFICATIONS" = "true" ]] && notify-send "Claude Bridge" "❌ No clipboard tool found"
    exit 1
fi

# Check if clipboard has content
if [[ -z "$CLIPBOARD_CONTENT" ]]; then
    echo "❌ Error: Clipboard appears to be empty"
    [[ "$ENABLE_NOTIFICATIONS" = "true" ]] && notify-send "Claude Bridge" "❌ Clipboard is empty"
    exit 1
fi

# Safety check for sensitive data
if [[ "$ENABLE_SAFETY_CHECK" = "true" ]]; then
    if echo "$CLIPBOARD_CONTENT" | grep -Eqi 'api[_-]?key|token|password|secret|private'; then
        echo "❌ Potential sensitive data detected. Aborting save."
        [[ "$ENABLE_NOTIFICATIONS" = "true" ]] && notify-send "Claude Bridge" "❌ Sensitive data detected - save aborted"
        exit 1
    fi
fi

# Save clipboard to target file
echo "$CLIPBOARD_CONTENT" > "$TARGET"

# Auto-cleanup filters
if [[ "$ENABLE_CLEANUP" = "true" ]]; then
    # Remove common ChatGPT preambles
    sed -i '/^Sure, here/d' "$TARGET"
    sed -i '/^Here is/d' "$TARGET"
    sed -i '/^Certainly/d' "$TARGET"
    sed -i '/^Of course/d' "$TARGET"
    # Remove excessive whitespace
    sed -i 's/^\s*//g' "$TARGET"
    # Remove standalone triple backticks (often unnecessary for Claude)
    sed -i '/^```\s*$/d' "$TARGET"
fi

# Add timestamp header
echo -e "## Task @ $(date '+%Y-%m-%d %H:%M')\n" | cat - "$TARGET" > temp && mv temp "$TARGET"

# Detect content type and add metadata
case "$TARGET" in
    *.md)   CONTENT_TYPE="📝 Markdown" ;;
    *.sh)   CONTENT_TYPE="💻 Shell script" ;;
    *)      CONTENT_TYPE="📄 Plain text" ;;
esac

echo "✅ Clipboard saved to $TARGET ($CONTENT_TYPE)"

# Show preview of content
echo "📄 Content preview:"
head -3 "$TARGET" | sed 's/^/   /'

# Archive with daily folders
if [[ "$ARCHIVE_ENABLED" = "true" ]]; then
    ARCHIVE_DATE=$(date '+%Y-%m-%d')
    DAILY_ARCHIVE="$ARCHIVE_DIR/$ARCHIVE_DATE"
    mkdir -p "$DAILY_ARCHIVE"
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    cp "$TARGET" "$DAILY_ARCHIVE/task_$timestamp.md"
    echo "📁 Archived as $ARCHIVE_DATE/task_$timestamp.md"
fi

# Auto-run Claude with proper checks
if [[ "$AUTO_RUN_CLAUDE" = "true" ]]; then
    if ! command -v claude &> /dev/null; then
        echo "❌ Claude command not found. Skipping auto-run."
        echo "🔧 To process with Claude, run: claude run \"$TARGET\""
    else
        echo "🤖 Running Claude Code..."
        claude run "$TARGET"
    fi
else
    echo "🔧 To process with Claude, run:"
    echo "   claude run \"$TARGET\""
fi

# System notification on completion
if [[ "$ENABLE_NOTIFICATIONS" = "true" ]]; then
    if command -v notify-send &> /dev/null; then
        if [[ "$AUTO_RUN_CLAUDE" = "true" ]] && command -v claude &> /dev/null; then
            notify-send "Claude Bridge" "✅ Clipboard saved and Claude executed"
        else
            notify-send "Claude Bridge" "✅ Clipboard saved - ready for Claude"
        fi
    fi
fi