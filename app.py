from flask import Flask, render_template, request, jsonify
import requests
import google.generativeai as genai

# Create a Flask application instance
app = Flask(__name__)

# Configure Google AI API key
api_key = 'AIzaSyBJVnIE_qpHui-FchgOSJC28aBrpfA0Lcg'
generate_content_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + api_key


system_instructions = None
model = None

def read_system_instructions():
    global system_instructions
    if system_instructions is None:
        try:
            with open('system_instructions.txt', 'r', encoding='utf-8') as file:
                system_instructions = file.read()
        except FileNotFoundError:
            # Handle file not found error
            system_instructions = ""
    return system_instructions

def initialize_model():
    global model
    if model is None:
        try:
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
            }
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            system_instr = read_system_instructions()
            if system_instr:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash-latest",
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                    system_instruction=system_instr
                )
        except Exception as e:
            # Handle model initialization error
            model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
initialize_model()  # Ensure model is initialized if not already

def generate_response(user_input):
    
    if model:
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": system_instructions + f"\n\nUser Input: {user_input}"
                        }
                    ]
                }
            ]
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(generate_content_url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return "Error: Model not initialized"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input', '')
    response = generate_response(user_input)
    chat_response_text = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
    return jsonify({'chat_response': chat_response_text})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
