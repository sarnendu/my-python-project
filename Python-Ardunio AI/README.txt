Table of Contents
Overview
Prerequisites
Project Structure
Setup Instructions
Arduino Setup
Python Environment
Hardware & Microphone / Headset
Usage & Commands
Wake Word / Activation
Active Mode Commands
Notable Commands
Command Reference
LED Control
Paint & Drawing
Image & Document Processing
Web & Information
Notepad & Applications
Sleep & Exit
Files & Components
Configuration & Customization
Troubleshooting
FAQ
Contributing
License
Overview
This repository implements a voice-activated desktop assistant with the following capabilities:

Recognizes spoken commands via a microphone (Google Speech Recognition)
Text-to-speech responses via pyttsx3
Serial control of an Arduino LED on pin 13
Launch and draw in MSPaint
Basic image processing (blur, sharpen)
Basic document processing (uppercase)
Web searches, YouTube searches
Wikipedia summaries
Simple Notepad automation via GUI
Wake-word based activation and sleep mode
The system is Python-based and relies on multiple third-party libraries for speech, serial communication, GUI automation, image/doc processing, and audio playback.

Prerequisites
Python 3.8+ installed
An Arduino board with a LED connected to pin 13 (or modify accordingly)
USB cable to connect Arduino to your PC
Administrative privileges to install system dependencies
Project Structure
arduino/ – Arduino sketch for LED control
python/ – Python-based voice assistant
main.py (or equivalent entry point)
Modules for:
Serial communication with Arduino
Speech recognition (speech_recognition)
Text-to-speech (pyttsx3)
Sound I/O (sounddevice, soundfile)
Image processing (Pillow)
Document processing (python-docx)
GUI automation (pyautogui)
File dialogs (tkinter)
Web interactions (webbrowser, wikipedia)
Note: The exact file names may vary if you clone or restructure. This README assumes the structure described above.

Setup Instructions
Arduino Setup
Upload the provided Arduino sketch to your board.

Find the serial port that your Arduino uses:

Windows: e.g., COM3
Linux/macOS: e.g., /dev/ttyACM0 or /dev/ttyUSB0
In the Python script, update the port if necessary:

python
arduino = serial.Serial('COM5', 9600)  # Change to your port
Python Environment
(Optional) Create a virtual environment:

Windows:
python -m venv venv
venv\Scripts\activate
macOS/Linux:
bash
python3 -m venv venv
source venv/bin/activate
Install dependencies:

pip install pyserial speechrecognition pyttsx3 sounddevice pillow python-docx wikipedia pyautogui tkinter soundfile
If you encounter issues with pyaudio (a common dependency for speech_recognition), install it separately:
pip install pyaudio
Ensure microphone and speakers are configured correctly on your system.
Hardware & Peripherals
USB microphone (recommended)
USB headset for playback (optional, but used in the script to detect a USB device)
A PC with USB ports for Arduino
Display for file dialogs (Tkinter)
Usage & Commands
Wake Word Activation
The assistant starts in a “sleep” mode.
Activate with phrases such as:
“wake up assistant”
“hey assistant”
When activated, the assistant will respond with a prompt such as:

“Yes, how can I help?”
Active Mode Commands
In active mode, you can issue commands like:

LED control
Open Paint
Draw shapes
Edit images or documents
Web searches or YouTube searches
Read information from Wikipedia
Open Notepad
Sleep or exit
Command Reference
LED Control
Trigger phrases:

Containing both “turn on” and “led” (e.g., “turn on the LED”)
Containing both “turn off” and “led” (e.g., “turn off the LED”)
Actions:

LED ON sent to Arduino over serial
LED OFF sent to Arduino over serial
Feedback:

“Turning on the LED”
“Turning off the LED”
Note: This relies on the exact strings in the Arduino sketch and the Python command mapper.

Paint & Drawing
open paint

Launch MSPaint (Windows)
Feedback: “Paint is ready. You can give me drawing commands now.”
draw square

Draws a square using mouse automation in MSPaint
Feedback: “Square drawn.”
draw circle

Draws a circle using mouse automation
Feedback: “Circle drawn.”
Other shapes:

If unrecognized, the assistant says it can only draw square or circle for now.
Image & Document Processing
edit image

Opens a file picker to select an image (PNG/JPG/JPEG)
Asks for an edit command (e.g., blur, sharpen)
Applies the edit and saves as output.png
Feedback: “Image processed and saved as output.png”
edit document

Opens a file picker to select a Word document (.docx)
Asks for an edit command (e.g., uppercase)
Applies edits and saves as output.docx
Feedback: “Document processed and saved as output.docx”
Web & Information
notepad

Opens Notepad (Windows) via a GUI automation approach
Feedback: “Opening Notepad”
search

Prompts for a query, then opens Google search
Feedback: “Searching for …”
youtube

Prompts for a query, then opens YouTube search results
Feedback: “Playing … on YouTube”
tell me about [topic]

Fetches a short summary from Wikipedia and speaks it
If not found: “Sorry, I couldn't find information.”
Sleep & Exit
sleep or go to sleep

Returns to sleep mode
Feedback: “Okay, I will sleep now.”
exit or quit

Exits the program gracefully
Feedback: “Goodbye!”
Files & Components
Arduino Sketch: arduino_LED_control.ino (or similar)
Python Script: main entry point (e.g., assistant.py)
Handles:
Serial connection: arduino = serial.Serial('<port>', 9600)
Speech recognition: speech_recognition
TTS: pyttsx3
Audio I/O: sounddevice, soundfile
Painting automation: pyautogui
File dialogs: tkinter
Image processing: Pillow (ImageFilter)
Document processing: python-docx
Wikipedia access: wikipedia
Web access: webbrowser
Configuration & Customization
LED port/pin:

Update the Arduino sketch if you change the LED pin.
Update the Python command strings accordingly if necessary.
Wake words:

Modify the condition in the main loop to include more phrases, e.g.:
if "wake up assistant" in command or "hey assistant" in command
Sound device:

The Python script detects a USB headset automatically. If needed, adjust the logic or specify a device index.
File processing:

Extend process_image and process_doc to support more operations (e.g., rotate, resize, lowercase).
Error handling:

Add try-except blocks around I/O operations to handle disconnections gracefully.
Troubleshooting
Serial Port Issues

Ensure Arduino is connected and the port in arduino = serial.Serial('<port>', 9600) matches
Use Device Manager (Windows) or ls /dev (macOS/Linux) to identify the correct port
Microphone / Recognition

Ensure microphone access is granted
Check network connectivity for Google Speech Recognition
Adjust ambient noise handling in listen()
TTS Issues

Install appropriate voices for pyttsx3 depending on OS
Change voice at runtime via engine.setProperty('voice', <voice_id>)
Painting Automation

Windows-only: mspaint is used; adapt for other OS or editor
Notepad Automation

Windows-specific using pyautogui to trigger Start menu and Notepad
For other OS, modify the launcher accordingly
FAQ
Q: Can I customize wake words?

A: Yes. Modify the wake word checks in the main loop and process_command.
Q: How do I add more drawing shapes?

A: Extend draw_shape(shape) with new branches and implement mouse actions with pyautogui.
Q: How can I change the LED pin?

A: Change the pin in the Arduino sketch and corresponding serial commands in the Python code.
Contributing
Welcome improvements and fixes. Typical contribution steps:

Fork the repo
Create a new branch for your feature/bugfix
Commit with a descriptive message
Open a Pull Request
Please add tests or at least run instructions if you add new features.

License
This project is provided as an example for educational purposes. Use at your own risk. Include your preferred license here (e.g., MIT).
If you’d like, I can provide:

A ready-to-commit GitHub repository layout with a sample folder tree
A unified entry script suggestion (e.g., assistant.py) and an accompanying requirements.txt
A minimal CI workflow (GitHub Actions) to verify dependencies
