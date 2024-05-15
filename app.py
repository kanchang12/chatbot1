from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
#from google.generativeai import ClientManager

# Create a Flask application instance
app = Flask(__name__)

# Configure Google AI API key
#api_key = os.getenv("API_KEY")
api_key = {
  "type": "service_account",
  "project_id": "gen-lang-client-0366631731",
  "private_key_id": "7c8b1dad2c564f93f678b03428fe8f0ea784820f",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7/+V4AOdwVKdA\n0QPSNEGO6QXPwdgCo0J1GIw0mbdqaCCF1niakO/ECm03oR44luXu1n93Ic8Y/kEZ\nLEW4FUF8bgd+cOX+GUvO4rtsK9fn9pi11q4t1LSMK5w6RA/JpOb6fxVBXub6vrjM\neZgRRrqTfw0gCNaYjk8daB3YTE42kvtUB3N4QTqEPoW/bEQsWSH3yhVe706m4jrR\nXaJHZnGiWDiSUWjTUl6APaypZJiKO4s3XRNdk4hFGtL9y5T6Z2CveSuD4TbZWaG2\nM6z+XUfgznb3VlY8w8BcsUYTgUVDC6SLjmfpxF6+IaYfw7yLULPe//uXnXYEgEcV\ng64xofDvAgMBAAECggEAHh5QTDoThJgrS2Ow8bDUJ+mxDVMIIN64O5Dj4AbDBFW2\nOtAx9iFDfZa7X0QoAUzmKANOhxlwLO2JeazxZnJmpraXQMHO4Yx6lqRq/ljFItu2\nJLubSqsJrxh1fj1/11WHI5kkde/sSpOE1k1MosfqsCKUnw3gw1lZLLmMvnr1tMxE\n5FwHOpnhBt/U5hKBHt/aAyIVZXOBZ2Dbs7cV15aF+3Fr08zQ6+b9Uyoc1TE/3KKU\nvHW+ZF7PaKRCM2gwoloNOb2njJzMaU3ZfquV+cg/kE0u3Dz7j7ulTyUrdLbXBXQm\nc7WmvF3zJJhImw+0W/DtKgjrFkvMVkDYUIWvbkK1QQKBgQDryk6Pb9giA3+afCc0\nJuyU+HS/AV0cvaNiiUVTFVrN1neHVndV+5X6xwMe2sq47CLxUMgwJPNRSPJxyeQH\nfxfafe8gNg4/zC+BxVWua5tCvsqU0SD4XOVGcRT9nQwgKmCiuTXKXlppdDOh2Ypb\n2Qeh4QsBNH96sMi80uN887eXvwKBgQDMHPhYFAWoHR08bSQVqRq75s1eHT6KycT4\nlSQGFJD1IyIBpmdo1JWoDknh6T2yvYXAqOX+2hcHKO6fE9LoZiFBquCrCQ6UZbcm\nYaaIajI6Xu/chdtRoh6PgQPHvgFA0fqcMuX5atrLyvGDxzuFcP2Bn8oq5R6JBUYl\nyYrRc9Ry0QKBgQDZkxKu9OuhZ00GBm4+h3RjemhwIBgFf1AWish3hAsISVB+h+ES\nbFbW03EjtYy+2tbbiklPc6k6Zm+hZESQTkx6hx5ywK6hXA6yVp9blVvtWRSiAd/E\njiPavlo6NAKOY8xMG09xb2NKT7mdLZmoaznJvFllQUYotpxk8MyN7m6JDQKBgH2E\n+zu+5FOjw8zbGSuw2F3g6z4LIeDbf6OWo5aRoyr8tfbpzAHtaTL1xn2En4qBffUi\naH22xB6FD2kIGdUMqTrmyE6lvS+I9X5G4tBU7hpzM3IbZunmloCNSDPXJpIkDsdr\njX06Nt7IKIlvRa0j9OF30C1cxNBiS+cE77cqUeVhAoGASBH50nhWhD8rAXESNzGM\nS6YrDjJqFgCD7l9QH2gVT3b/JXEI35DMnGF726B9AHT3A3OiCGK8auGINFhe2yzP\nmPC5091l5CQdYGjBfmo55bbBO5OYJZ1InmWxqqip4Sx+YvzUkVTAgGFi5xsnM6Rj\nKz0pX/fZApdPiJ3o2hBGCq8=\n-----END PRIVATE KEY-----\n",
  "client_email": "754288717289-compute@developer.gserviceaccount.com",
  "client_id": "103707579639379488799",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/754288717289-compute%40developer.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
#genai.configure(api_key=os.environ["API_KEY"])
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

