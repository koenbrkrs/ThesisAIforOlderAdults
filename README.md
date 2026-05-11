# Tangible Voice Interface for ElevenLabs Agents

This project turns a physical vintage phone into a tangible voice interface for interacting with various AI agents powered by ElevenLabs. It works cross-platform (macOS for simulation and Raspberry Pi/Linux for physical deployment).

## Features
- **Physical Interaction**: Pick up the handset to hear a dial tone, and press buttons to select different AI personalities.
- **Global Interrupt**: Hanging up the phone instantly terminates any active conversation and resets the system state to idle.
- **Multiple Agents**: Supports mapping up to 4 different ElevenLabs agents to physical buttons.
- **Real-time Voice**: Uses ElevenLabs Conversational AI for low-latency, bidirectional audio streaming.

## Hardware Setup (Raspberry Pi)
The application expects the following GPIO layout:
- **Hook Switch**: GPIO 17 (Normally Closed to Ground)
- **Agent Buttons**: GPIO 22, 23, 24, 25 (Pulled up, triggers on press)

## Installation

### 1. Set up a Python Virtual Environment
We use a `requirements.txt` file instead of pushing the whole virtual environment to GitHub. This is standard practice because virtual environments are platform-specific (a macOS `.venv` will break on a Raspberry Pi). 

```bash
# Create the virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Note: The project requires `pynput` for macOS simulation and `gpiozero` for Raspberry Pi physical wiring).*

## Usage
Simply run the main script:
```bash
python main.py
```
Wait for the `--- Phone System Online ---` message, and then you can lift the handset and press a button!
