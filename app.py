from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import asyncio

app = Flask(__name__)

# Configure Google API key
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

# Initialize global variables
model = None
system_instructions = None

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

async def initialize_model_async():
    global model
    try:
        if model is None:
            generation_config = {
                "temperature": 1,
                "top_p": 0.5,
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

@app.route('/chat', methods=['POST'])
async def chat():
    try:
        user_input = request.json.get('user_input', '')
        if not user_input:
            return jsonify({'error': 'Invalid user input'}), 400
        
        # Initialize model asynchronously if not already initialized
        await initialize_model_async()

        # Send user input to the model for response generation
        async with model.session() as session:
            response = await session.query(user_input)

        # Extract response text
        chat_response_text = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')

        return jsonify({'chat_response': chat_response_text}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Run the Flask application using an async event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(initialize_model_async()))
    
    # Use Gunicorn as the production WSGI server
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)
