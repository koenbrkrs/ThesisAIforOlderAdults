#!/bin/bash
echo "=========================================="
echo "   Thesis Phone App - Autostart Setup"
echo "=========================================="
echo ""

# Get the absolute path to the project directory
PROJECT_DIR=$(pwd)
AUTOSTART_DIR="$HOME/.config/autostart"

echo "Creating unified run_all.sh wrapper..."
# This wrapper ensures both backend and frontend launch together
# and exit together when CTRL+W or Alt+F4 is pressed.
cat << 'EOF' > "$PROJECT_DIR/run_all.sh"
#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Phone Backend..."
cd "$PROJECT_DIR"
source .venv/bin/activate
python main.py &
BACKEND_PID=$!

echo "Starting Fullscreen UI..."
# --password-store=basic disables the annoying keyring unlock prompt!
chromium-browser --kiosk "file://$PROJECT_DIR/ui.html" \
  --password-store=basic \
  --disable-infobars \
  --noerrdialogs \
  --check-for-update-interval=31536000 \
  --disable-component-update

echo "UI closed, shutting down backend..."
kill $BACKEND_PID
wait $BACKEND_PID 2>/dev/null
EOF

chmod +x "$PROJECT_DIR/run_all.sh"

echo "Creating autostart directory at $AUTOSTART_DIR..."
mkdir -p "$AUTOSTART_DIR"

# Clean up old separate autostart files
rm -f "$AUTOSTART_DIR/phone_app.desktop"
rm -f "$AUTOSTART_DIR/kiosk_ui.desktop"

UI_DESKTOP="$AUTOSTART_DIR/thesis_phone.desktop"
echo "Setting up unified autostart..."

cat <<EOF > "$UI_DESKTOP"
[Desktop Entry]
Name=Thesis Phone App
Comment=Starts Backend and UI
Exec=bash "$PROJECT_DIR/run_all.sh"
Type=Application
Terminal=false
EOF

chmod +x "$UI_DESKTOP"

# Update Desktop Shortcut so you can launch it manually
DESKTOP_DIR="$HOME/Desktop"
SHORTCUT_PATH="$DESKTOP_DIR/Start_Phone_App.desktop"
echo "Updating Desktop Shortcut..."

cat <<EOF > "$SHORTCUT_PATH"
[Desktop Entry]
Name=Start Phone App
Comment=Start the ElevenLabs Phone Interface
Exec=bash "$PROJECT_DIR/run_all.sh"
Icon=utilities-terminal
Terminal=false
Type=Application
EOF

chmod +x "$SHORTCUT_PATH"

echo ""
echo "=========================================="
echo "   Setup Complete! 🎉"
echo "=========================================="
echo "Changes made:"
echo "1. Disabled keyring popup via --password-store=basic"
echo "2. 'run_all.sh' links Python and Chromium together"
echo "3. Pressing CTRL+W or Alt+F4 will now close BOTH Chromium and Python."
echo "4. Your desktop 'Start Phone App' icon is updated."
echo ""
echo "To test it right now without rebooting, just double click your desktop icon!"
echo ""
