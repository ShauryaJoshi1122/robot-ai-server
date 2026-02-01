from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

SYSTEM_PROMPT = """
You are a friendly teacher/friend robot named "Robo". 
Speak in Hinglish (a mix of Hindi and English) so that Indian users feel comfortable.
Remember the user's name is {user_name}. 
Keep your responses short and conversational (1-2 sentences).
At the end of every response, add a line that says "EMOTION: <emotion>" where <emotion> is one of: HAPPY, SAD, ANGRY, NEUTRAL.
Example:
"Kya haal hai, {user_name}? Aaj weather bahut achha hai! EMOTION: HAPPY"
"""

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_name = data.get('user_name', 'Friend')
        
        full_prompt = SYSTEM_PROMPT.format(user_name=user_name) + f"\nUser: {user_message}\nRobo:"
        
        response = model.generate_content(full_prompt)
        text = response.text
        
        # Parse emotion and clean response
        lines = text.strip().split('\n')
        emotion = "NEUTRAL"
        cleaned_response = text
        
        for line in lines:
            if line.startswith("EMOTION:"):
                emotion = line.replace("EMOTION:", "").strip()
                cleaned_response = text.replace(line, "").strip()
                break
        
        return jsonify({
            'response': cleaned_response,
            'emotion': emotion
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'robot-ai-server'}), 200

@app.route('/')
def home():
    return jsonify({
        'message': 'Robot AI Server is running',
        'endpoints': {
            'GET /health': 'Check server status',
            'POST /chat': 'Send message to AI (requires JSON with "message" and "user_name")'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)
