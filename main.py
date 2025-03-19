import os
from dotenv import load_dotenv
def main ():
    load_dotenv()
    api_value = os.getenv("OPENAI_API_KEY")
    print (api_value)
main ()

import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template
import openai
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
from PIL import Image
import pytesseract

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Check API Key
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key is missing. Set it in the .env file.")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Initialize Flask App
app = Flask(__name__)

# Ensure FFmpeg is set up properly
AudioSegment.converter = "C:/ffmg/ffmpeg-2025-03-17-git-5b9356f18e-full_build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/ffmg/ffmpeg-2025-03-17-git-5b9356f18e-full_build/bin/ffprobe.exe"

# Set Tesseract OCR path (Update this path if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Chat Route
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": user_message}]
        )

        return jsonify({'response': response['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Voice Input Route
@app.route('/voice', methods=['POST'])
def voice():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file uploaded'}), 400

        audio_file = request.files['audio']
        temp_audio_path = "temp_audio.wav"
        audio_file.save(temp_audio_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        return jsonify({'response': text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Image Upload Route (With Preprocessing)
@app.route('/image', methods=['POST'])
def image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        image_file = request.files['image']
        image_path = "uploaded_image.png"
        image_file.save(image_path)

        # Open image using OpenCV
        img = cv2.imread(image_path)

        # Convert to Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian Blur (optional)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge Detection (Canny)
        edges = cv2.Canny(blurred, 50, 150)

        # OCR (Extract text from image)
        extracted_text = pytesseract.image_to_string(gray)

        # Save processed image
        processed_path = "processed_image.png"
        cv2.imwrite(processed_path, edges)

        # Send to OpenAI with extracted text
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-vision",
            messages=[
                {"role": "system", "content": "You are an AI that analyzes images."},
                {"role": "user", "content": f"Extracted text from image: {extracted_text}. What do you see in this image?"}
            ],
            files=[{"type": "image", "image_path": processed_path}]
        )

        return jsonify({
            'response': response['choices'][0]['message']['content'],
            'extracted_text': extracted_text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Combined Voice & Image Processing
@app.route('/voice_image', methods=['POST'])
def voice_image():
    try:
        if 'audio' not in request.files or 'image' not in request.files:
            return jsonify({'error': 'Both audio and image are required'}), 400

        # Process Audio
        audio_file = request.files['audio']
        temp_audio_path = "temp_audio.wav"
        audio_file.save(temp_audio_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Process Image
        image_file = request.files['image']
        image_path = "uploaded_image.png"
        image_file.save(image_path)

        # OpenAI request
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-vision",
            messages=[
                {"role": "system", "content": "You analyze both speech and images."},
                {"role": "user", "content": f"The user said: {text}. What do you see in this image?"}
            ],
            files=[{"type": "image", "image_path": image_path}]
        )

        return jsonify({'response': response['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run Flask Server
if __name__ == '__main__':
    app.run(debug=True)
