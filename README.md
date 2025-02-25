This project is a simple AI chatbot using OpenAI's API with Flask as the backend. The chatbot supports both text and voice input, allowing users to communicate via typing or speech.
Setup Instructions
1. Clone the Repository
git clone https://github.com/your-repo/ai-chatbot.git
cd ai-chatbot
2. Create a Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. Install Dependencies
pip install flask openai python-dotenv speechrecognition pyaudio
4. Set Up Environment Variables
Create a .env file in the project directory and add your OpenAI API key:
5. Run the Application
python main.py
Visit http://127.0.0.1:5000/ in your browser to interact with the chatbot.
1. Text Chat
Request:
POST /chat
{
  "message": "Hello AI, how can I improve my speaking?"
}
Response:
{
  "response": "Improving your speaking skills involves practice, confidence, and structured articulation. Would you like some exercises?"
}
2. Voice Input
Upload a .wav file to /voice, and the chatbot will convert speech to text before responding.

Response Example:
{
  "response": "Your speech sounds clear! Try slowing down slightly for better articulation."
}
 Design Decisions

1. Why Flask?

Lightweight and easy to deploy.

Simple integration with OpenAI API.

Scalable for future enhancements.

2. Why OpenAI's GPT-3.5 Turbo?

Provides high-quality responses with low latency.

Cost-effective for chat applications.

Supports system role prompts for better context retention.

3. Why Voice Input?

Helps users practice speaking skills.

Speech recognition allows real-time feedback.

Future Enhancements

✅ User authentication.

✅ Database storage for user progress.

🔜 Multilingual support.

🔜 Interactive feedback mechanisms.
