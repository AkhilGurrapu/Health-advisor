# app.py
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from config import GOOGLE_API_KEY
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Load health knowledge base
with open('health_data.json', 'r') as f:
    health_data = json.load(f)

@app.route('/')
def home():
    session.clear()  # Clear any existing conversation
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json['message']
    conversation_state = session.get('conversation_state', {'stage': 'initial'})
    
    try:
        if conversation_state['stage'] == 'initial':
            # Check if it's a symptom we recognize
            symptom_response = analyze_symptoms(user_message.lower())
            if symptom_response['type'] == 'symptom':
                session['conversation_state'] = {
                    'stage': 'asking_food',
                    'symptom': symptom_response['name']
                }
                return jsonify({
                    'response': {
                        'type': 'question',
                        'message': f"I understand you're experiencing {symptom_response['name']}. What did you eat in the last 24 hours?"
                    }
                })
        
        elif conversation_state['stage'] == 'asking_food':
            # Process food information and provide detailed response
            symptom = conversation_state['symptom']
            food_info = user_message
            
            prompt = f"""As a health advisor, provide a detailed, structured response for someone experiencing {symptom} 
            who ate {food_info} in the last 24 hours. Format the response in these specific sections:

            1. ANALYSIS OF CAUSE:
            - Analyze if any foods mentioned could trigger the symptom
            - Explain acid/base reactions if relevant
            - Other potential triggers

            2. IMMEDIATE RELIEF:
            - Recommended over-the-counter medications with dosage
            - Quick natural remedies
            - What to avoid right now

            3. NATURAL SOLUTIONS:
            - Detailed home remedies
            - Herbal treatments
            - Dietary recommendations

            4. LIFESTYLE CHANGES:
            - Daily habits to develop
            - Foods to avoid
            - Preventive measures

            5. WHEN TO SEE A DOCTOR:
            - Warning signs
            - Emergency symptoms

            Keep each section concise but informative. Include specific recommendations."""
            
            response = model.generate_content(prompt)
            
            # Clear the conversation state
            session.pop('conversation_state', None)
            
            return jsonify({
                'response': {
                    'type': 'detailed_advice',
                    'message': response.text
                }
            })
        
        # Default to Gemini response for unhandled cases
        gemini_response = get_gemini_response(user_message)
        return jsonify({
            'response': {
                'type': 'general',
                'message': gemini_response
            }
        })
        
    except Exception as e:
        return jsonify({
            'response': {
                'type': 'error',
                'message': f"I apologize, but I encountered an error: {str(e)}"
            }
        })

def get_gemini_response(message):
    prompt = f"""As an AI Health Advisor, provide a structured response to this health concern: {message}
    
    Format your response with these sections:
    1. ANALYSIS
    2. IMMEDIATE RELIEF
    3. NATURAL SOLUTIONS
    4. LIFESTYLE CHANGES
    5. WHEN TO SEE A DOCTOR
    
    Keep each section concise but informative. Include specific recommendations.
    If this is a medical emergency, emphasize seeking immediate medical attention."""
    
    response = model.generate_content(prompt)
    return response.text

def analyze_symptoms(message):
    for symptom in health_data['symptoms']:
        if symptom['name'] in message:
            return {
                'type': 'symptom',
                'name': symptom['name'],
                'causes': symptom['causes'],
                'remedies': symptom['remedies'],
                'prevention': symptom['prevention']
            }
    
    return {
        'type': 'general',
        'message': "Let me help you with your health concern."
    }

if __name__ == '__main__':
    app.run(debug=True)