import os
from dotenv import load_dotenv
def main ():
    load_dotenv()
    api_value = os.getenv("OPENAI_API_KEY")
    print (api_value)
main ()

import os
import time
import logging
import random
import openai
import sqlite3
import speech_recognition as sr
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pydub import AudioSegment  # Added for audio conversion
from pydub.utils import which
# Manually specify the FFmpeg path
FFMPEG_PATH = r"C:\ffmg\ffmpeg-2025-03-17-git-5b9356f18e-full_build\bin\ffmpeg.exe"  # Update with your actual path
FFPROBE_PATH = r"C:\ffmg\ffmpeg-2025-03-17-git-5b9356f18e-full_build\bin\ffprobe.exe"  # Update with your actual path
# Set the path to ffmpeg and ffprobe explicitly
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key not found. Set it in .env or as an environment variable.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# ---------------------- Exponential Backoff Function ----------------------
def retry_with_backoff(api_call, max_retries=3, base_delay=1, max_delay=16):
    """Retries the OpenAI API call with exponential backoff in case of failure."""
    retries = 0
    while retries < max_retries:
        try:
            return api_call()
        except openai.error.RateLimitError as e:  # Corrected exception
            wait_time = min(base_delay * (2 ** retries) + random.uniform(0, 1), max_delay)
            logging.warning(f"Rate limit exceeded. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            retries += 1
        except openai.OpenAIError as e:
            logging.error(f"OpenAI API error: {e}")
            break  # Don't retry other OpenAI API errors
    return None  # If all retries fail

# ---------------------- Chat API ----------------------
@app.route('/chat', methods=['POST'])
def chat():
    """Handles text-based chat requests with OpenAI."""
    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        logging.info(f"User message: {user_message}")

        # API call wrapped in retry mechanism
        response = retry_with_backoff(lambda: client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive coach helping improve verbal clarity."},
                {"role": "user", "content": user_message}
            ]
        ))

        if response:
            return jsonify({'response': response.choices[0].message.content})
        else:
            return jsonify({'error': 'Failed after multiple retries'}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

# ---------------------- Voice Input API ----------------------
@app.route('/voice', methods=['POST'])
def voice_input():
    """Handles voice input, converts it to text, and generates an AI response."""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        if not audio_file.filename.lower().endswith('.wav'):
            return jsonify({'error': 'Invalid audio format. Only WAV files are supported.'}), 400

        # Convert file to PCM WAV (if necessary)
        temp_audio_path = "temp_audio.wav"
        audio_file.save(temp_audio_path)

        audio = AudioSegment.from_file(temp_audio_path)
        audio.export(temp_audio_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            user_message = recognizer.recognize_google(audio_data)

        # API call wrapped in retry mechanism
        response = retry_with_backoff(lambda: client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive coach helping improve verbal clarity."},
                {"role": "user", "content": user_message}
            ]
        ))

        if response:
            return jsonify({'user_message': user_message, 'response': response.choices[0].message.content})
        else:
            return jsonify({'error': 'Failed after multiple retries'}), 500

    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand the audio. Please try again.'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Speech recognition service error: {e}'}), 500
    except Exception as e:
        logging.error(f'Error in voice input: {e}')
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

# ---------------------- Home Route ----------------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------------- Run Flask App ----------------------
if __name__ == '__main__':
    app.run(debug=True)
