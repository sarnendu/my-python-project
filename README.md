Verbal Communication Skills Trainer
This project is an AI-powered Verbal Communication Skills Trainer that enables users to improve their communication skills through text chat, voice input, and image analysis. It uses OpenAI’s GPT-4 Turbo for chat responses, speech recognition for voice processing, and OCR (Optical Character Recognition) for extracting text from images.

Features
✅ Chat with AI - Users can communicate with AI via text.
✅ Voice Input Processing - Users can record their voice and get a transcription.
✅ Image Analysis - Users can upload images for AI-based analysis.
✅ Voice + Image Processing - Users can upload images and provide voice input for combined analysis.

Tech Stack
Frontend:
HTML, CSS, JavaScript (AJAX and jQuery)
Backend:
Python (Flask Framework)
OpenAI API (GPT-4 Turbo and Vision)
SpeechRecognition (Google Speech API)
Pydub (for audio processing)
OpenCV & Tesseract OCR (for image preprocessing and text extraction)
Installation & Setup
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-repo-name.git
cd your-repo-name
2. Create a Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Set Up Environment Variables
Create a .env file in the project directory and add:

ini
Copy
Edit
OPENAI_API_KEY=your_openai_api_key_here
5. Configure Tesseract OCR & FFmpeg
Download & Install Tesseract OCR from here.
Set its path in pytesseract.pytesseract.tesseract_cmd inside app.py.
Install FFmpeg and set its path in AudioSegment.converter in app.py.
6. Run the Flask App
bash
Copy
Edit
python app.py
Visit http://127.0.0.1:5000/ in your browser.

Project Structure
bash
Copy
Edit
📂 Verbal-Communication-Skills-Trainer
│── 📂 static                 # Static files (CSS, JS)
│── 📂 templates              # HTML Templates
│── ├── index.html            # Frontend UI
│── 📂 uploads                # Uploaded files (images/audio)
│── 📂 processed              # Processed images
│── .env                      # Environment variables (API Keys)
│── app.py                    # Flask Backend
│── requirements.txt           # Python Dependencies
│── README.md                 # Project Documentation
API Endpoints
Endpoint	Method	Description
/	GET	Load the homepage
/chat	POST	Send a text message to the AI
/voice	POST	Upload and process voice input
/image	POST	Upload an image for analysis
/voice_image	POST	Upload voice and image for combined analysis
Frontend Code (index.html)
Located in templates/index.html.

Users can send chat messages to the AI.
Voice recording is implemented using the navigator.mediaDevices.getUserMedia API.
Image previews are displayed before sending for analysis.
AJAX calls are used to interact with the backend without page reloads.
Backend Code (main.py)
Located in main.py.

Uses Flask to create API routes.
Processes text chat using OpenAI GPT-4 Turbo.
Handles voice input using Google Speech-to-Text API.
Performs image analysis using OpenCV + Tesseract OCR.
Supports voice + image input processing with OpenAI’s multimodal capabilities.
Future Improvements
🚀 Real-time Speech Feedback
🚀 Multilingual Support
🚀 Mobile-Friendly UI
🚀 Database Integration

License
MIT License © 2025
🔜 Interactive feedback mechanisms.
