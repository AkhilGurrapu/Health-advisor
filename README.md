# AI Health Advisor 🤖💊

A Flask-based web application that provides personalized health advice using Google's Gemini AI, with conversation state management and structured symptom analysis.

## Features
- Symptom analysis with follow-up questions
- Food intake tracking for better diagnosis
- Structured health advice in 5 categories
- Session-based conversation management
- Error handling and user-friendly interface

## Project Structure
```
your-project/
├── app.py                 # Main application logic (lines 1-140)
├── config.py             # Configuration template (lines 1-2)
├── health_data.json      # Symptom knowledge base
├── templates/
│   └── index.html        # Chat interface (lines 20-105)
├── .env                  # Environment variables (created during setup)
└── requirements.txt      # Dependencies
```


## Local Setup

### Prerequisites
- **Python 3.11+**: Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).
- **Git**: Install Git from [git-scm.com](https://git-scm.com/downloads).
- **Google Gemini API key**: You will need an API key to use the Gemini AI service.

### Obtaining a Google Gemini API Key
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to the **API & Services** section.
4. Click on **Enable APIs and Services**.
5. Search for **Generative Language API** and enable it.
6. Go to **Credentials** in the left sidebar.
7. Click on **Create Credentials** and select **API Key**.
8. Copy the generated API key.

### Installation Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ai-health-advisor.git
   cd ai-health-advisor
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - For **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```
   - For **Windows**:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   - Create a `.env` file in the project root directory:
   ```bash
   touch .env
   ```
   - Open the `.env` file in a text editor and add the following lines:
   ```ini
   GOOGLE_API_KEY=your_actual_gemini_api_key_here  # Replace with your API key
   FLASK_SECRET_KEY=your_secret_key_here  # You can generate a random key
   ```

### Running the Application
1. **Start the Flask application**:
   ```bash
   flask run --port 5000 --debug
   ```
2. **Access the application**: Open your web browser and go to `http://localhost:5000`.

## Key Code Components

### Application Routes
- `/`: Main entry point with session reset.
- `/get_response`: Handles chat interactions and AI processing.

### Conversation Flow
1. Initial symptom detection.
2. Food intake inquiry.
3. Structured AI response generation.

## Deployment Notes
- Use a production WSGI server (e.g., Gunicorn or UWSGI) for deployment.
- Set `FLASK_ENV=production` in production.
- Implement HTTPS for security.
- Rotate API keys regularly.

## Security Best Practices
- Never commit `.env` to version control.
- Use environment variables for secrets.
- Rate limit API endpoints.
- Validate all user inputs.

## Troubleshooting

| Error | Solution |
|-------|----------|
| 400 API_KEY_INVALID | Update `.env` with a valid API key. |
| Port 5000 in use | Use `--port` with a different number. |
| ModuleNotFound | Reinstall dependencies from `requirements.txt`. |

## Environment-Based Configuration
To implement environment-based configuration instead of hardcoded keys:

1. Modify `config.py`:
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()  # Load environment variables from .env file

   GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
   FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
   ```

2. Update `app.py`:
   ```python
   from flask import Flask, render_template, request, jsonify, session
   import google.generativeai as genai
   from config import GOOGLE_API_KEY
   import json

   app = Flask(__name__)
   app.secret_key = FLASK_SECRET_KEY  # Use secret key from config

   # Configure Gemini API
   genai.configure(api_key=GOOGLE_API_KEY)
   model = genai.GenerativeModel('gemini-pro')
   ```

This setup provides proper secret management while maintaining the application's functionality.