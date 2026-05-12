#!/bin/bash
echo "=========================================="
echo "   Thesis Phone App - Autostart Setup"
echo "=========================================="
echo ""

# Get the absolute path to the project directory
PROJECT_DIR=$(pwd)
AUTOSTART_DIR="$HOME/.config/autostart"

echo "Creating autostart directory at $AUTOSTART_DIR..."
mkdir -p "$AUTOSTART_DIR"

# 1. Autostart the Phone App (Background Python process)
PHONE_DESKTOP="$AUTOSTART_DIR/phone_app.desktop"
echo "Setting up Phone App to run on boot..."

cat <<EOF > "$PHONE_DESKTOP"
[Desktop Entry]
Name=Thesis Phone App Background
Comment=Starts the ElevenLabs Phone Interface
Exec=bash -c 'cd "$PROJECT_DIR" && source .venv/bin/activate && python main.py'
Type=Application
Terminal=false
EOF

# 2. Autostart Chromium in Kiosk mode (Fullscreen UI)
UI_DESKTOP="$AUTOSTART_DIR/kiosk_ui.desktop"
echo "Setting up Fullscreen UI to open on boot..."

cat <<EOF > "$UI_DESKTOP"
[Desktop Entry]
Name=Phone App UI
Comment=Starts the UI in Fullscreen
Exec=chromium-browser --kiosk "file://$PROJECT_DIR/ui.html" --disable-infobars --noerrdialogs --check-for-update-interval=31536000 --disable-component-update
Type=Application
Terminal=false
EOF

# Make sure they have execute permissions
chmod +x "$PHONE_DESKTOP"
chmod +x "$UI_DESKTOP"

echo ""
echo "=========================================="
echo "   Autostart Configured! 🎉"
echo "=========================================="
echo "Next time you reboot the Raspberry Pi:"
echo "  1. The Python backend will start automatically in the background."
echo "  2. Chromium will open in full-screen kiosk mode showing the text."
echo ""
echo "To exit the full-screen kiosk mode at any time, press Alt+F4 or Ctrl+W."
echo ""
