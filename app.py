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
            symptom_response = analyze_symptoms(user_message.lower())
            if symptom_response['type'] == 'symptom':
                # Get the appropriate follow-up question based on the symptom
                follow_up_question = get_follow_up_question(symptom_response['name'])
                
                session['conversation_state'] = {
                    'stage': 'asking_details',
                    'symptom': symptom_response['name']
                }
                return jsonify({
                    'response': {
                        'type': 'question',
                        'message': f"I understand you're experiencing {symptom_response['name']}. {follow_up_question}"
                    }
                })
        
        elif conversation_state['stage'] == 'asking_details':
            # Process symptom details and provide response
            symptom = conversation_state['symptom']
            details = user_message
            
            prompt = get_symptom_specific_prompt(symptom, details)
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
            'response': gemini_response  # Now returns {type: 'detailed_advice', message: ...}
        })
        
    except Exception as e:
        return jsonify({
            'response': {
                'type': 'error',
                'message': f"I apologize, but I encountered an error: {str(e)}"
            }
        })

def get_gemini_response(message):
    prompt = f"""As an AI Health Advisor, provide a detailed, structured response for someone experiencing {message}. 
    Format your response exactly as follows:

    **1. ANALYSIS**

    **Main Causes:**
    • List main causes here
    • Each on a new line

    **Contributing Factors:**
    • List factors here
    • Each on a new line

    **Type of Condition:**
    • Acute vs Chronic
    • Severity levels

    **2. IMMEDIATE RELIEF**

    **Medications:**
    • Over-the-counter options:
        - Names and dosages
        - When to take
        - Precautions
    • Prescription medications (if applicable):
        - Names and dosages
        - When to take
        - Precautions

    **Quick Remedies:**
    • At-home treatments:
        - List treatments
        - With instructions
    • Immediate actions:
        - What to do now
        - What to avoid

    **3. NATURAL SOLUTIONS**

    **Herbal Remedies:**
    • Option 1:
        - Preparation method
        - Dosage guideline
    • Option 2:
        - Preparation method
        - Dosage guideline

    **Alternative Therapies:**
    • List therapies
    • With application methods

    **4. LIFESTYLE CHANGES**

    **Daily Habits:**
    • What to do:
        - List good habits
        - With explanations
    • What to avoid:
        - List things to avoid
        - With reasons

    **Prevention Tips:**
    • Short-term:
        - Immediate actions
        - Quick fixes
    • Long-term:
        - Lifestyle changes
        - Ongoing practices

    **5. WHEN TO SEE A DOCTOR**

    **Warning Signs:**
    • Emergency symptoms:
        - List urgent symptoms
        - That need immediate care
    • Serious indicators:
        - List concerning symptoms
        - That need medical attention

    **Risk Factors:**
    • High-risk groups:
        - List vulnerable populations
    • Complications:
        - Potential complications
        - Long-term effects

    Keep each section detailed but concise. Use bullet points consistently.
    If this is a medical emergency, emphasize seeking immediate medical attention first."""
    
    response = model.generate_content(prompt)
    
    # Return in the same format as symptom responses
    return {
        'type': 'detailed_advice',
        'message': response.text
    }

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

def get_follow_up_question(symptom):
    """Generate appropriate follow-up questions based on the symptom."""
    
    symptom_questions = {
        'headache': """To help better, please tell me:
            - How long have you had it?
            - Is it on one side or both sides?
            - Have you experienced any triggers (stress, lack of sleep, bright lights)?""",
            
        'stomach pain': """To help better, please tell me:
            - Where exactly is the pain located?
            - How long have you had it?
            - Have you noticed any connection with food or meals?""",
            
        'fever': """To help better, please tell me:
            - What's your temperature reading?
            - How long have you had the fever?
            - Are you experiencing any other symptoms?""",
            
        'cough': """To help better, please tell me:
            - Is it a dry cough or producing mucus?
            - How long have you had it?
            - Does anything make it better or worse?"""
    }
    
    # Default question if symptom not in dictionary
    default_question = """Please tell me:
        - How long have you had this symptom?
        - Is it constant or does it come and go?
        - Have you noticed any triggers or patterns?"""
    
    return symptom_questions.get(symptom, default_question)

def get_symptom_specific_prompt(symptom, details):
    """Generate a specific prompt based on the symptom and user details."""
    
    base_prompt = f"""As an AI Health Advisor, provide a detailed, structured response for someone experiencing {symptom} 
    with these specific details: {details}
    
    Format your response exactly as follows:

    **1. ANALYSIS**

    **Main Causes:**
    • List main causes here based on the specific details provided
    • Each on a new line

    **Contributing Factors:**
    • List factors here
    • Each on a new line

    **Type of Condition:**
    • Acute vs Chronic
    • Severity levels based on provided details

    **2. IMMEDIATE RELIEF**

    **Medications:**
    • Over-the-counter options:
        - Names and dosages
        - When to take
        - Precautions
    • Prescription medications (if applicable):
        - Names and dosages
        - When to take
        - Precautions

    **Quick Remedies:**
    • At-home treatments:
        - List treatments specific to the described symptoms
        - With instructions
    • Immediate actions:
        - What to do now
        - What to avoid

    **3. NATURAL SOLUTIONS**

    **Herbal Remedies:**
    • Option 1:
        - Preparation method
        - Dosage guideline
    • Option 2:
        - Preparation method
        - Dosage guideline

    **Alternative Therapies:**
    • List therapies
    • With application methods

    **4. LIFESTYLE CHANGES**

    **Daily Habits:**
    • What to do:
        - List good habits
        - With explanations
    • What to avoid:
        - List things to avoid
        - With reasons

    **Prevention Tips:**
    • Short-term:
        - Immediate actions
        - Quick fixes
    • Long-term:
        - Lifestyle changes
        - Ongoing practices

    **5. WHEN TO SEE A DOCTOR**

    **Warning Signs:**
    • Emergency symptoms:
        - List urgent symptoms
        - That need immediate care
    • Serious indicators:
        - List concerning symptoms
        - That need medical attention

    **Risk Factors:**
    • High-risk groups:
        - List vulnerable populations
    • Complications:
        - Potential complications
        - Long-term effects

    Keep each section detailed but concise. Use bullet points consistently.
    If this is a medical emergency, emphasize seeking immediate medical attention first.
    Base your response specifically on the provided symptom details."""

    return base_prompt

if __name__ == '__main__':
    app.run(debug=True)