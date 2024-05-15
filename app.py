from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
#from google.generativeai import ClientManager

# Create a Flask application instance
app = Flask(__name__)

# Configure Google AI API key
#api_key = os.getenv("API_KEY")
genai.configure(api_key=os.environ["API_KEY"])
#print(api_key)
#client_manager = ClientManager(api_key=api_key)
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

# Define a route for handling chatbot interactions
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input', '')

    # Generate response using the chatbot model
    response = model.generate_content([user_input])
    chat_response = response.text

    return jsonify({'chat_response': chat_response})

# Run the Flask application
if __name__ == "__main__":
    # Use Gunicorn as the production WSGI server
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)

