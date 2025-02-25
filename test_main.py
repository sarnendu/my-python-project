import unittest  
import sqlite3  
import os  
from your_module import init_db  # Replace your_module with the name of your file  

DATABASE_NAME = 'progress.db'  # Define the database name  

class TestInitDB(unittest.TestCase):  

    def setUp(self):  
        """Setup: Ensure the database file doesn't exist before each test."""  
        # Remove the database file if it exists  
        try:  
            os.remove(DATABASE_NAME)  
        except FileNotFoundError:  
            pass  # It's ok if the file doesn't exist  

    def tearDown(self):  
        """TearDown: Remove the database file after each test."""  
        # Remove the database file if it exists  
        try:  
            os.remove(DATABASE_NAME)  
        except FileNotFoundError:  
            pass  

    def test_init_db_creates_database_and_table(self):  
        """Test that init_db creates the database file and the user_progress table."""  
        init_db()  
        self.assertTrue(os.path.exists(DATABASE_NAME))  

        # Check if the table exists  
        conn = sqlite3.connect(DATABASE_NAME)  
        cursor = conn.cursor()  

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_progress';")  
        result = cursor.fetchone()  

        conn.close()  
        self.assertIsNotNone(result, "The 'user_progress' table was not created.")  

    def test_init_db_idempotent(self):  
        """Test that running init_db multiple times doesn't cause an error."""  
        init_db()  
        init_db()  

        # Verify the database still exists and the table is still there.  
        self.assertTrue(os.path.exists(DATABASE_NAME))  
        conn = sqlite3.connect(DATABASE_NAME)  
        cursor = conn.cursor()  
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_progress';")  
        result = cursor.fetchone()  
        conn.close()  
        self.assertIsNotNone(result)  

if __name__ == '__main__':  
    unittest.main()

import unittest  
from flask import Flask, render_template  
from your_module import home  # Replace your_module  

class TestHome(unittest.TestCase):  

    def setUp(self):  
        """Set up a Flask app for testing."""  
        self.app = Flask(__name__)  
        self.app.config['TESTING'] = True  # Enable testing mode  
        self.client = self.app.test_client()  # Create a test client  
        self.app_context = self.app.app_context()  
        self.app_context.push()  

    def tearDown(self):  
        """Clean up after the test."""  
        self.app_context.pop()  

    def test_home_returns_index_html(self):  
        """Test that the home function returns the index.html template."""  
        with self.app.test_request_context():  # Push a request context  
            response = home()  
            self.assertIn(b"<!DOCTYPE html>", response.data) #Check for basic HTML structure.  More specific checks are better.  
            self.assertEqual(response.status_code, 200) # Check HTTP status code  

    def test_home_renders_template(self):  
        """Test that the home function actually renders a template (more robust)."""  

        # Create a simple index.html for testing.  Ideally, you'd have a separate  
        # directory for test templates.  

        @self.app.route('/test_route')  
        def test_route():  
            return render_template('test_index.html', message="Hello, Test!")  

        # Create a test template  
        with open("test_index.html", "w") as f:  
            f.write("<h1>{{ message }}</h1>")  

        with self.app.test_request_context('/test_route'):  
            response = test_route() #Call the test route  
            self.assertEqual(response.status_code, 200)  
            self.assertIn(b"<h1>Hello, Test!</h1>", response.data)  #Look for the rendered content  
            os.remove("test_index.html") #Clean up the test template  

if __name__ == '__main__':  
    unittest.main()

import unittest  
from unittest.mock import patch  
from flask import Flask, request, jsonify  
import openai  
import logging  # Import logging  
from your_module import chat  # Replace your_module  

class TestChat(unittest.TestCase):  

    def setUp(self):  
        """Set up a Flask app for testing."""  
        self.app = Flask(__name__)  
        self.app.config['TESTING'] = True  
        self.client = self.app.test_client()  

        # Define a route for the chat function within the test app  
        self.app.add_url_rule('/chat', 'chat', chat, methods=['POST'])  
        self.app_context = self.app.app_context()  
        self.app_context.push()  
        logging.disable(logging.CRITICAL)  # Disable logging during tests.  

    def tearDown(self):  
        """Clean up after the test."""  
        self.app_context.pop()  
        logging.disable(logging.NOTSET)  # Re-enable logging after tests  

    @patch('openai.ChatCompletion.create')  
    def test_chat_success(self, mock_openai_create):  
        """Test successful chat completion."""  
        mock_openai_create.return_value = {  
            'choices': [{'message': {'content': 'Test response from OpenAI'}}]  
        }  

        data = {'message': 'Test user message'}  
        response = self.client.post('/chat', json=data)  
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(response.json['response'], 'Test response from OpenAI')  
        mock_openai_create.assert_called_once()  # Verify OpenAI was called.  

    def test_chat_invalid_request_format(self):  
        """Test chat with invalid (non-JSON) request format."""  
        response = self.client.post('/chat', data='This is not JSON')  
        self.assertEqual(response.status_code, 415)  
        self.assertEqual(response.json['error'], 'Invalid request format. Must be JSON.')  

    def test_chat_missing_message(self):  
        """Test chat with missing message in the request."""  
        response = self.client.post('/chat', json={})  
        self.assertEqual(response.status_code, 400)  
        self.assertEqual(response.json['error'], 'Message is required')  

    @patch('openai.ChatCompletion.create')  
    def test_chat_openai_error(self, mock_openai_create):  
        """Test chat when OpenAI API returns an error."""  
        mock_openai_create.side_effect = Exception("OpenAI API Error")  

        data = {'message': 'Test user message'}  
        response = self.client.post('/chat', json=data)  
        self.assertEqual(response.status_code, 500)  
        self.assertEqual(response.json['error'], 'An error occurred during the chat. Please try again.')  
        mock_openai_create.assert_called_once()  

    def test_chat_logging(self):  
      """Test that errors are logged."""  
      with self.assertLogs(level='ERROR') as cm:  
          with patch('openai.ChatCompletion.create', side_effect=Exception("Test Error")):  
              data = {'message': 'Test message'}  
              self.client.post('/chat', json=data)  
              self.assertIn("Error in chat: Test Error", cm.output[0])

import unittest  
from flask import Flask, jsonify, request  
from unittest.mock import patch, MagicMock  
from app import app  # Import your Flask app  

class VoiceInputTestCase(unittest.TestCase):  

    def setUp(self):  
        # Create a test client  
        self.app = app.test_client()  
        self.app.testing = True  

    @patch('app.sr.Recognizer')  
    @patch('app.openai.ChatCompletion.create')  
    def test_voice_input_success(self, mock_openai, mock_recognizer):  
        # Mock audio file and recognizer  
        mock_recognizer_instance = mock_recognizer.return_value  
        mock_audio_file = MagicMock()  
        mock_audio_file.filename = 'test.wav'  

        # Mock the methods of speech_recognition  
        with patch('app.sr.AudioFile', return_value=mock_audio_file):  
            mock_recognizer_instance.record.return_value = None  
            mock_recognizer_instance.recognize_google.return_value = "Hello, this is a test."  

            # Mock the OpenAI API response  
            mock_openai.return_value = {  
                'choices': [{'message': {'content': 'This is a response to your input.'}}]  
            }  

            # Send a POST request with the audio file  
            response = self.app.post('/voice', content_type='multipart/form-data', data={  
                'audio': (BytesIO(b'some audio data'), 'test.wav')  
            })  

            # Check the response  
            self.assertEqual(response.status_code, 200)  
            data = response.get_json()  
            self.assertEqual(data['user_message'], "Hello, this is a test.")  
            self.assertEqual(data['response'], 'This is a response to your input.')  

    def test_voice_input_no_audio(self):  
        # Test case for no audio file provided  
        response = self.app.post('/voice')  
        self.assertEqual(response.status_code, 400)  
        self.assertIn('No audio file provided', response.get_json()['error'])  

    def test_voice_input_invalid_format(self):  
        # Test case for invalid audio format  
        response = self.app.post('/voice', content_type='multipart/form-data', data={  
            'audio': (BytesIO(b'some audio data'), 'test.txt')  # Fake .txt file  
        })  
        self.assertEqual(response.status_code, 400)  
        self.assertIn('Invalid audio format. Please upload a WAV file.', response.get_json()['error'])  

    @patch('app.sr.Recognizer')  
    def test_voice_input_recognition_error(self, mock_recognizer):  
        # Test case for recognition error  
        mock_recognizer_instance = mock_recognizer.return_value  
        with patch('app.sr.AudioFile', return_value=None):  
            mock_recognizer_instance.recognize_google.side_effect = sr.UnknownValueError  

            # Send the request  
            response = self.app.post('/voice', content_type='multipart/form-data', data={  
                'audio': (BytesIO(b'some audio data'), 'test.wav')  
            })  
            self.assertEqual(response.status_code, 400)  
            self.assertIn('Could not understand the audio. Please try again.', response.get_json()['error'])  

    @patch('app.sr.Recognizer')  
    def test_voice_input_service_error(self, mock_recognizer):  
        # Test case for service error  
        mock_recognizer_instance = mock_recognizer.return_value  
        with patch('app.sr.AudioFile', return_value=None):  
            mock_recognizer_instance.recognize_google.side_effect = sr.RequestError("Service unavailable")  

            # Send the request  
            response = self.app.post('/voice', content_type='multipart/form-data', data={  
                'audio': (BytesIO(b'some audio data'), 'test.wav')  
            })  
            self.assertEqual(response.status_code, 500)  
            self.assertIn('Speech recognition service error:', response.get_json()['error'])  

if __name__ == '__main__':  
    unittest.main()

import unittest  
import sqlite3  
import os  # Import the 'os' module  
from your_module import store_progress  # Replace your_module  

DATABASE_NAME = 'test_progress.db' # Separate DB for testing.  

class TestStoreProgress(unittest.TestCase):  

    def setUp(self):  
        """Set up a test database."""  
        # Use a separate test database  
        self.conn = sqlite3.connect(DATABASE_NAME)  
        self.cursor = self.conn.cursor()  
        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS user_progress (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                user_id INTEGER,  
                activity_type TEXT,  
                feedback TEXT  
            )  
        ''')  
        self.conn.commit()  

    def tearDown(self):  
        """Clean up the test database."""  
        self.conn.close()  
        # Remove the test database file  
        os.remove(DATABASE_NAME)  

    def test_store_progress_success(self):  
        """Test successful storage of progress data."""  
        user_id = 123  
        activity_type = 'reading'  
        feedback = 'Completed chapter 1'  

        store_progress(user_id, activity_type, feedback)  

        # Verify data was inserted correctly  
        self.cursor.execute('SELECT user_id, activity_type, feedback FROM user_progress WHERE user_id = ?', (user_id,))  
        result = self.cursor.fetchone()  

        self.assertIsNotNone(result)  
        self.assertEqual(result[0], user_id)  
        self.assertEqual(result[1], activity_type)  
        self.assertEqual(result[2], feedback)  

    def test_store_progress_multiple_entries(self):  
        """Test storing multiple progress entries for the same user."""  
        user_id = 456  
        activity_type_1 = 'exercise'  
        feedback_1 = '30 minutes of cardio'  
        activity_type_2 = 'writing'  
        feedback_2 = 'Wrote 500 words'  

        store_progress(user_id, activity_type_1, feedback_1)  
        store_progress(user_id, activity_type_2, feedback_2)  

        # Verify both entries were stored  
        self.cursor.execute('SELECT activity_type, feedback FROM user_progress WHERE user_id = ?', (user_id,))  
        results = self.cursor.fetchall()  

        self.assertEqual(len(results), 2)  
        self.assertIn((activity_type_1, feedback_1), results)  
        self.assertIn((activity_type_2, feedback_2), results)  

    def test_store_progress_different_users(self):  
        """Test storing progress for different users."""  
        user_id_1 = 789  
        activity_type_1 = 'coding'  
        feedback_1 = 'Completed a coding challenge'  
        user_id_2 = 987  
        activity_type_2 = 'meditation'  
        feedback_2 = '15 minutes of mindfulness'  

        store_progress(user_id_1, activity_type_1, feedback_1)  
        store_progress(user_id_2, activity_type_2, feedback_2)  

        # Verify data for both users was stored correctly  
        self.cursor.execute('SELECT user_id, activity_type, feedback FROM user_progress WHERE user_id = ?', (user_id_1,))  
        result_1 = self.cursor.fetchone()  
        self.assertEqual(result_1[0], user_id_1)  
        self.assertEqual(result_1[1], activity_type_1)  
        self.assertEqual(result_1[2], feedback_1)  

        self.cursor.execute('SELECT user_id, activity_type, feedback FROM user_progress WHERE user_id = ?', (user_id_2,))  
        result_2 = self.cursor.fetchone()  
        self.assertEqual(result_2[0], user_id_2)  
        self.assertEqual(result_2[1], activity_type_2)  
        self.assertEqual(result_2[2], feedback_2)  

if __name__ == '__main__':  
    unittest.main()

import unittest  
from unittest.mock import patch, call  
from flask import Flask, request, jsonify  
import openai  
import logging  
from your_module import impromptu, store_progress  # Replace your_module  

class TestImpromptu(unittest.TestCase):  

    def setUp(self):  
        self.app = Flask(__name__)  
        self.app.config['TESTING'] = True  
        self.client = self.app.test_client()  
        self.app.add_url_rule('/impromptu', 'impromptu', impromptu, methods=['POST'])  
        self.app_context = self.app.app_context()  
        self.app_context.push()  
        logging.disable(logging.CRITICAL)  

    def tearDown(self):  
        self.app_context.pop()  
        logging.disable(logging.NOTSET)  

    @patch('openai.ChatCompletion.create')  
    @patch('your_module.store_progress')  
    def test_impromptu_success(self, mock_store_progress, mock_openai_create):  
        """Test successful impromptu evaluation."""  
        mock_openai_create.return_value = {  
            'choices': [{'message': {'content': 'Test evaluation from OpenAI'}}]  
        }  

        data = {'response': 'Test user response'}  
        response = self.client.post('/impromptu', json=data)  

        self.assertEqual(response.status_code, 200)  
        self.assertEqual(response.json['evaluation'], 'Test evaluation from OpenAI')  

        mock_openai_create.assert_called_once()  
        mock_store_progress.assert_called_once_with(user_id='some_user_id', activity_type='Impromptu Speaking', feedback='Test evaluation from OpenAI')  

    @patch('openai.ChatCompletion.create')  
    def test_impromptu_openai_error(self, mock_openai_create):  
        """Test impromptu when OpenAI API returns an error."""  
        mock_openai_create.side_effect = Exception("OpenAI API Error")  

        data = {'response': 'Test user response'}  
        response = self.client.post('/impromptu', json=data)  

        self.assertEqual(response.status_code, 500)  
        self.assertEqual(response.json['error'], 'An error occurred during the impromptu evaluation. Please try again.')  
        mock_openai_create.assert_called_once()  

    def test_impromptu_missing_response(self):  
        """Test impromptu with missing response in the request."""  
        response = self.client.post('/impromptu', json={})  

        self.assertEqual(response.status_code, 500) #Or should this be a 400? Consider! The code doesn't check explicitly. It will error in get_json  
        self.assertEqual(response.json['error'], 'An error occurred during the impromptu evaluation. Please try again.')  

    @patch('openai.ChatCompletion.create')  
    @patch('your_module.store_progress')  
    def test_impromptu_store_progress_called(self, mock_store_progress, mock_openai_create):  
        """Test that store_progress is called with the correct arguments."""  
        mock_openai_create.return_value = {  
            'choices': [{'message': {'content': 'Test evaluation'}}]  
        }  
        data = {'response': 'Test response'}  
        self.client.post('/impromptu', json=data)  
        mock_store_progress.assert_called_once_with(user_id='some_user_id', activity_type='Impromptu Speaking', feedback='Test evaluation')  

    def test_impromptu_logging(self):  
        """Test that errors are logged."""  
        with self.assertLogs(level='ERROR') as cm:  
            with patch('openai.ChatCompletion.create', side_effect=Exception("Test Error")):  
                data = {'response': 'Test response'}  
                self.client.post('/impromptu', json=data)  
                self.assertIn("Error in impromptu: Test Error", cm.output[0])
                