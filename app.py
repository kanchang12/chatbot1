from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import requests
import google.generativeai as genai


# Create a Flask application instance
app = Flask(__name__)

# Configure Google AI API key
api_key = os.getenv('GOOGLE_API_KEY')
#genai.configure(api_key=GOOGLE_API_KEY)
generate_content_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + api_key


# Read system instructions from external text file
def read_system_instructions():
    with open('system_instructions.txt', 'r', encoding='utf-8') as file:
        return file.read()

# Initialize the generative model with system instructions
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

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
    system_instruction=read_system_instructions()
)


# Define a route for the root URL
@app.route('/')
def index():
    return render_template('index.html')

# Define a route for the 'products' page
@app.route('/products')
def products():
    # Render the 'products.html' template and return it as a response
    return render_template('products.html')

# Define a route for the 'contact' page
@app.route('/contact')
def contact():
    # Render the 'contact.html' template and return it as a response
    return render_template('contact.html')

def read_system_instructions():
    with open('system_instructions.txt', 'r', encoding='utf-8') as file:
        return file.read()

# Define a function to generate response based on user input and system instructions
def generate_response(user_input):
    system_instructions = read_system_instructions()
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
    response = requests.post(generate_content_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}"



@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input', '')
    
    # Call your model to generate a response based on user input and system instructions
    response = generate_response(user_input)

    # Extract the chat response text from the response object
    chat_response_text = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')

    return jsonify({'chat_response': chat_response_text})


# Run the Flask application
if __name__ == "__main__":
    # Use Gunicorn as the production WSGI server
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)

