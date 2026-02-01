# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
# OR import openai for ChatGPT
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)  # Allow requests from your mobile web app

# ========== Configuration ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Set in Render.com environment
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # If using ChatGPT

# Initialize Gemini client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# System prompt that instructs the AI about its role and output format
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
    data = request.get_json()
    user_message = data.get('message', '')
    user_name = data.get('user_name', 'Friend')

    # Build the full prompt
    full_prompt = SYSTEM_PROMPT.format(user_name=user_name) + f"\nUser: {user_message}\nRobo:"

    try:
        # Call Gemini API
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

if __name__ == '__main__':
    app.run(debug=True)
