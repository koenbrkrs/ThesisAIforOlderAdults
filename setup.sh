#!/bin/bash
echo "=========================================="
echo "   Thesis Phone App - Automated Setup"
echo "=========================================="
echo ""

# 1. Update and install system requirements
echo "[1/4] Installing system audio libraries (PortAudio & Pavucontrol)..."
sudo apt-get update
sudo apt-get install -y portaudio19-dev libportaudio2 pulseaudio-utils pavucontrol

# 2. Create Virtual Environment
echo "[2/4] Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python Dependencies
echo "[3/4] Installing Python packages (this might take a minute)..."
pip install -r requirements.txt

# 4. Create Desktop Shortcut
echo "[4/4] Creating Desktop Shortcut..."
chmod +x create_shortcut.sh
./create_shortcut.sh

echo ""
echo "=========================================="
echo "   Setup Complete! 🎉"
echo "=========================================="
echo "IMPORTANT AUDIO FIX INSTRUCTIONS:"
echo "If the AI talks to itself, your Raspberry Pi is using internal 'Monitor' as the microphone."
echo "To fix this:"
echo "  1. Open the Raspberry Pi start menu."
echo "  2. Go to 'Sound & Video' -> 'PulseAudio Volume Control' (or type 'pavucontrol' in terminal)."
echo "  3. Go to the 'Input Devices' tab."
echo "  4. Make sure your physical microphone is selected as fallback/default."
echo "  5. NEVER select an input device that starts with 'Monitor of...'."
echo ""
echo "You can now double-click 'Thesis Phone App' on your Raspberry Pi desktop to start!"
