#!/bin/bash

# Get the absolute path to the project directory
PROJECT_DIR=$(pwd)
DESKTOP_DIR="$HOME/Desktop"
SHORTCUT_PATH="$DESKTOP_DIR/Start_Phone_App.desktop"

echo "Creating desktop shortcut at $SHORTCUT_PATH..."

# Create a Linux .desktop file
cat <<EOF > "$SHORTCUT_PATH"
[Desktop Entry]
Name=Thesis Phone App
Comment=Start the ElevenLabs Phone Interface
Exec=bash -c 'cd "$PROJECT_DIR" && source .venv/bin/activate && python main.py; echo "Press Enter to exit..."; read'
Icon=utilities-terminal
Terminal=true
Type=Application
EOF

# Make the shortcut executable
chmod +x "$SHORTCUT_PATH"

echo "Done! You should now see 'Start_Phone_App' on your Raspberry Pi desktop."
