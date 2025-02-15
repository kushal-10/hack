from flask import Flask, request, jsonify
import vonage
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize Vonage client with your API key and secret from environment variables
client = vonage.Client(key=os.getenv('VONAGE_API_KEY'), secret=os.getenv('VONAGE_API_SECRET'))
voice = vonage.Voice(client)

# Webhook for Vonage to send event when call is received
@app.route('/webhooks/voice/answer', methods=['POST'])
def answer_call():
    data = request.json
    print("Answer webhook received:", data)

    # Instructions for Vonage to answer and record the call
    response = {
        "action": "talk",
        "text": "Hello, you are connected. Please leave a message after the beep.",
        "event_url": [f"{os.getenv('NGROK_URL')}/webhooks/voice/event"]  # Use ngrok URL from .env file
    }
    return jsonify(response), 200

# Webhook for Vonage to send call events (e.g., call recording)
@app.route('/webhooks/voice/event', methods=['POST'])
def event():
    data = request.json
    print("Event webhook received:", data)

    if 'recording_url' in data:
        recording_url = data['recording_url']
        print(f"Recording URL: {recording_url}")

        # Download the recording (optional)
        response = requests.get(recording_url)
        with open("call_recording.mp3", "wb") as file:
            file.write(response.content)
        print("Recording downloaded as call_recording.mp3")

    return jsonify({"status": "received"}), 200

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
