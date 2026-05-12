import platform
import asyncio
import os
import signal
import subprocess
import json
import websockets
from enum import Enum

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

class State(Enum):
    IDLE = 1
    READY = 2
    ACTIVE = 3

class PhoneAgentApp:
    def __init__(self):
        self.state = State.IDLE
        self.hook_pressed = True  # True means handset is ON the cradle (put down)
        self.current_button = None
        
        self.dial_tone_process = None
        self.dial_tone_task = None
        self.conversation = None
        
        self.connected_clients = set()
        self.loop = None
        
        # Agent map
        self.agents = {
            1: "agent_3601kqc7s3sff85skcatnbr4ve23",
            2: "agent_1701kqc8cy2ee9drqehk4sjpjxnh",
            3: "agent_6701kqc9d10tem7vpq4dcdmkdz2k",
            4: "agent_8001kqc9pkx7etktw39nkrxx13em",
        }
        
        # ElevenLabs client
        api_key = "sk_1071d90e40f579c366c715eaee4f59e2d7b953affeedc264"
        self.client = ElevenLabs(api_key=api_key)
        self.requires_auth = bool(api_key)

    def setup_hardware(self):
        """Initializes the correct hardware abstraction based on the OS."""
        os_name = platform.system()
        if os_name == "Darwin":
            self._setup_mac_hardware()
        elif os_name == "Linux":
            self._setup_pi_hardware()
        else:
            print(f"Warning: Unsupported OS {os_name}. Hardware inputs may not work.")

    def _setup_mac_hardware(self):
        print("Setting up macOS hardware simulation (pynput)...")
        try:
            from pynput import keyboard
        except ImportError:
            print("Error: 'pynput' library not found. Please run 'pip install pynput'.")
            return

        def on_press(key):
            try:
                if key == keyboard.Key.space:
                    self.hook_pressed = not self.hook_pressed
                    status = "DOWN (IDLE)" if self.hook_pressed else "LIFTED (READY)"
                    print(f"[HW] Hook switch toggled to: {status}")
                elif hasattr(key, 'char') and key.char in ['1', '2', '3', '4']:
                    self.current_button = int(key.char)
                    print(f"[HW] Button {self.current_button} pressed")
            except Exception as e:
                pass

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def _setup_pi_hardware(self):
        print("Setting up Raspberry Pi hardware (gpiozero)...")
        try:
            from gpiozero import Button
        except ImportError:
            print("Error: 'gpiozero' library not found. Please run 'pip install gpiozero'.")
            return

        # Hook switch is normally closed (NC). GPIO 17.
        # Assuming closed circuit connects to ground (reads False/0). 
        # When pressed down (on cradle), switch is pressed.
        self.hook_switch = Button(17, pull_up=True, bounce_time=0.05)
        
        # Buttons: 22, 23, 24, 25
        self.btn1 = Button(22, pull_up=True, bounce_time=0.05)
        self.btn2 = Button(23, pull_up=True, bounce_time=0.05)
        self.btn3 = Button(24, pull_up=True, bounce_time=0.05)
        self.btn4 = Button(25, pull_up=True, bounce_time=0.05)

        def on_hook_pressed():
            # Handset replaced on cradle
            self.hook_pressed = True
            print("[HW] Hook switch pressed DOWN (IDLE)")

        def on_hook_released():
            # Handset lifted
            self.hook_pressed = False
            print("[HW] Hook switch RELEASED (LIFTED)")

        self.hook_switch.when_pressed = on_hook_pressed
        self.hook_switch.when_released = on_hook_released

        # Initialize current state from physical pin
        self.hook_pressed = self.hook_switch.is_pressed

        def btn_pressed(btn_num):
            self.current_button = btn_num
            print(f"[HW] Button {btn_num} pressed")

        self.btn1.when_pressed = lambda: btn_pressed(1)
        self.btn2.when_pressed = lambda: btn_pressed(2)
        self.btn3.when_pressed = lambda: btn_pressed(3)
        self.btn4.when_pressed = lambda: btn_pressed(4)

    async def _play_dial_tone_loop(self):   
        """Asynchronously plays the dial tone in a loop until cancelled."""
        audio_file = "dial_tone.wav"
        if not os.path.exists(audio_file):
            print(f"Warning: {audio_file} not found. Silence will be played instead.")
            while True:
                await asyncio.sleep(1)
                
        # Use afplay on Mac, aplay on Linux
        cmd = ["afplay", audio_file] if platform.system() == "Darwin" else ["aplay", "-q", audio_file]
         
        try:
            while self.state == State.READY:
                self.dial_tone_process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                await self.dial_tone_process.wait()
                self.dial_tone_process = None
        except asyncio.CancelledError:
            self.stop_dial_tone()
            raise

    def stop_dial_tone(self):
        if self.dial_tone_process:
            try:
                self.dial_tone_process.kill()
            except ProcessLookupError:
                pass
            self.dial_tone_process = None

    async def ws_handler(self, websocket):
        self.connected_clients.add(websocket)
        try:
            await websocket.wait_closed()
        except Exception:
            pass
        finally:
            self.connected_clients.remove(websocket)

    def broadcast_message(self, msg_dict):
        if not self.loop or not self.connected_clients:
            return
        
        async def send():
            msg_str = json.dumps(msg_dict)
            for client in list(self.connected_clients):
                try:
                    await client.send(msg_str)
                except Exception:
                    pass
        
        asyncio.run_coroutine_threadsafe(send(), self.loop)

    def start_conversation(self, button_num):
        agent_id = self.agents.get(button_num)
        if not agent_id:
            print(f"No agent mapped to button {button_num}")
            return

        print(f"Initiating ElevenLabs AI session with agent {agent_id}...")
        
        def on_agent_response(response):
            print(f"Agent: {response}")
            self.broadcast_message({"type": "transcript", "speaker": "Agent", "text": response})
            
        def on_user_transcript(transcript):
            print(f"User: {transcript}")
            self.broadcast_message({"type": "transcript", "speaker": "User", "text": transcript})

        self.conversation = Conversation(
            self.client,
            agent_id,
            requires_auth=self.requires_auth,
            audio_interface=DefaultAudioInterface(),
            callback_agent_response=on_agent_response,
            callback_user_transcript=on_user_transcript,
        )
        self.conversation.start_session()
        print("Conversation active. Streaming bidirectionally...")
        self.broadcast_message({"type": "status", "message": "Conversation Active - Speak Now"})

    def stop_conversation(self):
        if self.conversation:
            print("Terminating ElevenLabs connection...")
            self.conversation.end_session()
            self.conversation = None

    async def run(self):
        self.loop = asyncio.get_running_loop()
        
        try:
            await websockets.serve(self.ws_handler, "0.0.0.0", 8765)
            print("WebSocket server running on ws://0.0.0.0:8765")
        except Exception as e:
            print(f"Failed to start WebSocket server: {e}")

        self.setup_hardware()
        print("\n--- Phone System Online ---")
        print("Awaiting interaction. State: IDLE")
        self.broadcast_message({"type": "status", "message": "System Online - Waiting for handset"})

        while True:
            # ----------------------------------------------------
            # GLOBAL INTERRUPT
            # ----------------------------------------------------
            if self.hook_pressed and self.state != State.IDLE:
                print("\n[!] Global Interrupt: Handset replaced.")
                if self.dial_tone_task:
                    self.dial_tone_task.cancel()
                    self.dial_tone_task = None
                self.stop_dial_tone()
                self.stop_conversation()
                self.state = State.IDLE
                self.current_button = None
                print("State -> IDLE. System is silent.")
                self.broadcast_message({"type": "status", "message": "Phone Put Down - Idle"})

            # ----------------------------------------------------
            # STATE MACHINE LOGIC
            # ----------------------------------------------------
            if self.state == State.IDLE:
                # System is completely silent and ignores buttons
                if not self.hook_pressed:
                    print("\nState -> READY. Handset lifted, playing dial tone...")
                    self.state = State.READY
                    self.current_button = None  # Clear any buffer from IDLE
                    self.broadcast_message({"type": "status", "message": "Handset Lifted - Dial an Agent..."})
                    # Spawn the dial tone playback asynchronously
                    self.dial_tone_task = asyncio.create_task(self._play_dial_tone_loop())
                
            elif self.state == State.READY:
                # Listening for agent button presses
                if self.current_button is not None:
                    print(f"\nState -> ACTIVE. Button {self.current_button} pressed.")
                    self.state = State.ACTIVE
                    self.broadcast_message({"type": "status", "message": f"Connecting to Agent {self.current_button}..."})
                    
                    # Stop dial tone immediately
                    if self.dial_tone_task:
                        self.dial_tone_task.cancel()
                        self.dial_tone_task = None
                    self.stop_dial_tone()
                    
                    # Boot the AI
                    self.start_conversation(self.current_button)
                    self.current_button = None

            elif self.state == State.ACTIVE:
                # The conversation streams in the background. 
                # We just yield and wait for the global interrupt to hang up.
                pass

            # Minimal sleep yields execution, ensuring zero blocking and low latency.
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    app = PhoneAgentApp()
    try:
        # Prevent keyboard interrupt from breaking the terminal too poorly
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nExiting application...")
        app.stop_dial_tone()
        app.stop_conversation()
