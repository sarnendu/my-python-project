import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import tempfile
import os
import pyautogui
import wikipedia
import serial
import time
import webbrowser
import soundfile as sf
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageFilter
from docx import Document
import subprocess

# ---------------- Arduino Setup ----------------
arduino = serial.Serial('COM5', 9600)  # Replace COM5 with your Arduino port
time.sleep(2)

# ---------------- TTS Setup ----------------
engine = pyttsx3.init()

# Detect USB headset automatically
usb_device_index = None
devices = sd.query_devices()
for i, dev in enumerate(devices):
    if "usb" in dev['name'].lower() and dev['max_output_channels'] > 0:
        usb_device_index = i
        print(f"🎧 Found USB headset: {dev['name']} (index {i})")
        break
if usb_device_index is None:
    print("⚠️ No USB headset found. Using default output device.")

def speak(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        filename = f.name
    engine.save_to_file(text, filename)
    engine.runAndWait()
    data, fs = sf.read(filename, dtype='float32')
    if usb_device_index is not None:
        sd.play(data, fs, device=usb_device_index)
    else:
        sd.play(data, fs)
    sd.wait()
    os.remove(filename)

# ---------------- Speech Recognition ----------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio)
            print(f"✅ Recognized: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return ""
        except sr.RequestError:
            print("⚠️ Could not connect to Google Speech Recognition service")
            return ""

# ---------------- Paint Drawing ----------------
def open_paint():
    subprocess.Popen('mspaint')
    time.sleep(2)
    speak("Paint is ready. You can give me drawing commands now.")

def draw_shape(shape):
    if shape == "square":
        pyautogui.moveTo(300, 300)
        pyautogui.mouseDown()
        for _ in range(4):
            pyautogui.move(100, 0, duration=0.3)
            pyautogui.move(0, 100, duration=0.3)
        pyautogui.mouseUp()
        speak("Square drawn.")
    elif shape == "circle":
        pyautogui.moveTo(400, 400)
        pyautogui.mouseDown()
        pyautogui.dragRel(100, 0, duration=0.3)
        pyautogui.dragRel(0, 100, duration=0.3)
        pyautogui.mouseUp()
        speak("Circle drawn.")
    else:
        speak("Sorry, I can only draw square or circle for now.")

# ---------------- File Selection ----------------
def select_file(file_type="image"):
    Tk().withdraw()
    if file_type == "image":
        filename = askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    else:
        filename = askopenfilename(filetypes=[("Documents", "*.pdf;*.docx;*.txt")])
    return filename

# ---------------- Image Processing ----------------
def process_image(filename, command):
    img = Image.open(filename)
    if "blur" in command:
        img = img.filter(ImageFilter.BLUR)
    elif "sharpen" in command:
        img = img.filter(ImageFilter.SHARPEN)
    img.save("output.png")
    speak("Image processed and saved as output.png")

# ---------------- Document Processing ----------------
def process_doc(filename, command):
    doc = Document(filename)
    if "uppercase" in command:
        for para in doc.paragraphs:
            para.text = para.text.upper()
    doc.save("output.docx")
    speak("Document processed and saved as output.docx")

# ---------------- Command Processing ----------------
def process_command(command):
    if "notepad" in command:
        pyautogui.press("win")
        time.sleep(1)
        pyautogui.write("notepad")
        pyautogui.press("enter")
        speak("Opening Notepad")

    elif "search" in command:
        speak("What should I search?")
        query = listen()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"Searching for {query}")

    elif "youtube" in command:
        speak("What should I play on YouTube?")
        query = listen()
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            speak(f"Playing {query} on YouTube")

    elif "tell me about" in command:
        topic = command.replace("tell me about", "").strip()
        if topic:
            try:
                summary = wikipedia.summary(topic, sentences=2)
                speak(summary)
            except:
                speak("Sorry, I couldn't find information.")

    elif "turn on" in command and "led" in command:
        arduino.write(b"LED ON\n")
        speak("Turning on the LED")

    elif "turn off" in command and "led" in command:
        arduino.write(b"LED OFF\n")
        speak("Turning off the LED")

    elif "open paint" in command:
        open_paint()

    elif "draw" in command:
        shape = command.replace("draw", "").strip()
        draw_shape(shape)

    elif "edit image" in command:
        file = select_file("image")
        speak("What edit should I perform?")
        edit_cmd = listen()
        process_image(file, edit_cmd)

    elif "edit document" in command:
        file = select_file("document")
        speak("What edit should I perform?")
        edit_cmd = listen()
        process_doc(file, edit_cmd)

    elif "sleep" in command or "go to sleep" in command:
        speak("Okay, I will sleep now. Say wake up, assistant, or hey assistant to activate me again.")
        return "sleep"

    elif "exit" in command or "quit" in command:
        speak("Goodbye!")
        exit()

    else:
        speak("I did not understand that command.")

    return "active"

# ---------------- Main Loop ----------------
mode = "sleep"
speak("Assistant is online. Say wake up, assistant, or hey assistant to start.")

while True:
    command = listen()
    if not command:
        continue

    if "wake up assistant" in command or "hey assistant" in command:
        speak("Yes, how can I help?")
        mode = "active"
        command = listen()
        if command:
            result = process_command(command)
            if result == "sleep":
                mode = "sleep"
    elif mode == "active":
        result = process_command(command)
        if result == "sleep":
            mode = "sleep"
