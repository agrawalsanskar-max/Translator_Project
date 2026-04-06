from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import re

# --- WINDOWS PATH CONFIGURATION ---
# This ensures Flask knows where templates are on your D: drive
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Ensure the static folder exists
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

@app.route('/')
def index():
    # Renders the HTML frontend
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang')

    if not text or not target_lang:
        return jsonify({'error': 'Missing text or language.'}), 400

    try:
        # 1. Automatic Detection & Translation
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated_text = translator.translate(text)

        # 2. Advanced Audio Synthesis
        # Create a safe filename (remove non-alphanumeric chars for file safety)
        safe_lang = re.sub(r'[^a-zA-Z0-9]', '', target_lang)
        audio_filename = f"out_{safe_lang}.mp3"
        audio_path = os.path.join(static_dir, audio_filename)
        
        # Clean up old audio to save space on your drive
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass # Avoid crashes if the file is currently being played
            
        # Generate new speech
        tts = gTTS(text=translated_text, lang=target_lang)
        tts.save(audio_path)

        # Return the translated text and the audio link to the browser
        return jsonify({
            'translated_text': translated_text,
            'audio_url': f'/static/{audio_filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' is required for Render to access the app
    app.run(host='0.0.0.0', port=port)