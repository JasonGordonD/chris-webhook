from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/chris_call', methods=['POST'])
def chris_call():
    try:
        # Read KB from file
        kb_path = os.path.join(os.path.dirname(__file__), "chris_kb.txt")
        if not os.path.exists(kb_path):
            return jsonify({"error": "chris_kb.txt not found"}), 500
        with open(kb_path, "r") as file:
            chris_kb = file.read()

        # Grok API call
        xai_key = os.environ.get('XAI_API_KEY')
        if not xai_key:
            return jsonify({"error": "XAI_API_KEY not set"}), 500
        grok_url = "https://api.x.ai/v1/chat/completions"
        grok_headers = {
            "Authorization": f"Bearer {xai_key}",
            "Content-Type": "application/json"
        }
        grok_payload = {
            "model": "grok-4-fast-reasoning",
            "messages": [
                {"role": "system", "content": chris_kb},
                {"role": "user", "content": "Simulate Chris calling Rami."}
            ]
        }
        grok_resp = requests.post(grok_url, json=grok_payload, headers=grok_headers)
        if grok_resp.status_code != 200:
            return jsonify({"error": f"Grok API error: {grok_resp.text}"}), 500
        chris_text = grok_resp.json()["choices"][0]["message"]["content"]

        # Eleven Labs API call
        eleven_key = os.environ.get('ELEVENLABS_API_KEY')
        if not eleven_key:
            return jsonify({"error": "ELEVENLABS_API_KEY not set"}), 500
        eleven_url = "https://api.elevenlabs.io/v1/text-to-speech/wRxsJKZqtYus0sDPSKY3"
        eleven_headers = {"xi-api-key": eleven_key}
        eleven_payload = {
            "text": chris_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }
        eleven_resp = requests.post(eleven_url, json=eleven_payload, headers=eleven_headers)
        if eleven_resp.status_code != 200:
            return jsonify({"error": f"Eleven Labs error: {eleven_resp.text}"}), 500
        audio_file = f"chris_call_{request.json.get('call_id', 'default')}.mp3"
        with open(audio_file, "wb") as f:
            f.write(eleven_resp.content)

        return jsonify({"text": chris_text, "audio": audio_file})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
