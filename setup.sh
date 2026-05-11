#!/bin/bash
echo "=========================================="
echo "   Thesis Phone App - Automated Setup"
echo "=========================================="
echo ""

# 1. Update and install system requirements
echo "[1/4] Installing system audio libraries (PortAudio for ElevenLabs)..."
sudo apt-get update
sudo apt-get install -y portaudio19-dev libportaudio2 pulseaudio-utils

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
echo "You can now double-click 'Thesis Phone App' on your Raspberry Pi desktop to start!"
