import os
from dotenv import load_dotenv
def main ():
    load_dotenv()
    api_value = os.getenv("OPENAI_API_KEY")
    print (api_value)
main ()

import os  
from flask import Flask, request, jsonify, render_template  
from dotenv import load_dotenv  
import openai  
import sqlite3  
import speech_recognition as sr  
import logging  

# Load environment variables securely  
load_dotenv()  
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  

# Check if API key is loaded properly  
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key not found. Set it in .env or as an environment variable.")

# Initialize Flask app and OpenAI  
app = Flask(__name__)  
openai.api_key = OPENAI_API_KEY  

# Configure logging  
logging.basicConfig(level=logging.DEBUG)  

# Database setup  
def init_db():  
    conn = sqlite3.connect('progress.db')  
    cursor = conn.cursor()  
    cursor.execute('''  
        CREATE TABLE IF NOT EXISTS user_progress (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            user_id TEXT NOT NULL,  
            activity_type TEXT NOT NULL,  
            feedback TEXT  
        )  
    ''')  
    conn.commit()  
    conn.close()  

# Initialize the database  
init_db()  

# Home Route  
@app.route('/')  
def home():  
    return render_template('index.html')  

# Chat Interface  
@app.route('/chat', methods=['POST'])  
def chat():  
    try:  
        if not request.is_json:
            return jsonify({'error': 'Invalid request format. Must be JSON.'}), 415

        data = request.get_json()
        user_message = data.get('message')  

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        response = openai.ChatCompletion.create(  
            model="gpt-3.5-turbo",  
            messages=[  
                {"role": "system", "content": "You are a supportive coach helping improve verbal clarity."},  
                {"role": "user", "content": user_message}  
            ]  
        )  
        return jsonify({'response': response['choices'][0]['message']['content']})  
    except Exception as e:  
        logging.error(f'Error in chat: {e}')  
        return jsonify({'error': 'An error occurred during the chat. Please try again.'}), 500  

# Voice Input Handling  
@app.route('/voice', methods=['POST'])  
def voice_input():  
    try:  
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        # Check if the uploaded file is in WAV format  
        if not audio_file.filename.lower().endswith('.wav'):
            return jsonify({'error': 'Invalid audio format. Please upload a WAV file.'}), 400

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            user_message = recognizer.recognize_google(audio_data)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive coach helping improve verbal clarity."},
                {"role": "user", "content": user_message}
            ]
        )
        return jsonify({'user_message': user_message, 'response': response['choices'][0]['message']['content']})
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand the audio. Please try again.'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Speech recognition service error: {e}'}), 500
    except Exception as e:
        logging.error(f'Error in voice input: {e}')
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500  

# Store Progress Function  
def store_progress(user_id, activity_type, feedback):  
    conn = sqlite3.connect('progress.db')  
    cursor = conn.cursor()  
    cursor.execute('INSERT INTO user_progress (user_id, activity_type, feedback) VALUES (?, ?, ?)',  
                   (user_id, activity_type, feedback))  
    conn.commit()  
    conn.close()  

# Impromptu Speaking Route  
@app.route('/impromptu', methods=['POST'])  
def impromptu():  
    try:  
        data = request.get_json()
        user_response = data.get('response')  

        evaluation = openai.ChatCompletion.create(  
            model="gpt-3.5-turbo",  
            messages=[  
                {"role": "system", "content": "Evaluate this response for structure, clarity, and engagement."},  
                {"role": "user", "content": user_response}  
            ]  
        )  

        store_progress(user_id='some_user_id', activity_type='Impromptu Speaking', feedback=evaluation['choices'][0]['message']['content'])  
        return jsonify({'evaluation': evaluation['choices'][0]['message']['content']})  
    except Exception as e:  
        logging.error(f'Error in impromptu: {e}')  
        return jsonify({'error': 'An error occurred during the impromptu evaluation. Please try again.'}), 500  

# Start Flask Server  
if __name__ == '__main__':  
    app.run(debug=True)
