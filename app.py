from flask import Flask, render_template, request, jsonify
import openai
import json
import os

app = Flask(__name__)


api_key = os.getenv('GOOGLE_API_KEY')
openai.api_key = api_key

# System instructions for chat
system_instructions = (
    "You are the customer interface of Fakesoap.com.\n"
    "You will be polite and provide accurate information to customers.\n"
    "If a customer says abusive things, you can close the chat.\n"
    "If someone asks irrelevant things, bring the topic back to our soap business.\n"
    "Be formal and professional.\n\n"
    "For your chat, you will load the entire data below first and give an answer.\n\n\n"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input', '')

    if not user_input:
        return jsonify({'chat_response': 'Error: No user input provided'})

    try:
        # Create chat completion request to OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150  # Adjust max_tokens as needed
        )

        # Extract chat response from OpenAI API response
        chat_response = response['choices'][0]['message']['content']

        return jsonify({'chat_response': chat_response})

    except Exception as e:
        return jsonify({'chat_response': f"Error: {str(e)}"})

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    # Use Gunicorn as the production WSGI server
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)
