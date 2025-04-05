from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pydub import AudioSegment
from io import BytesIO
import os

app = Flask(__name__)

# Enable CORS for local and production frontend URLs
CORS(app, origins=["http://localhost:3000", "https://your-frontend-domain.com"])

@app.route('/')
def index():
    return "Binaural Beats Backend Running"

@app.route('/api/process', methods=['POST'])
def process_audio():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        base_freq = float(request.form.get('baseFreq', 440))
        beat_freq = float(request.form.get('beatFreq', 10))
        original_volume = float(request.form.get('originalVolume', 1.0))
        beat_volume = float(request.form.get('beatVolume', 0.5))

        # Load uploaded audio file
        audio = AudioSegment.from_file(uploaded_file)
        audio = audio.set_channels(2)

        # Simulate binaural beat by shifting frequency of right channel
        left = audio.split_to_mono()[0]
        right = left

        # Apply phase difference simulation by panning (as a placeholder)
        left = left.pan(-0.5) - (1 - original_volume) * 30
        right = right.pan(0.5) - (1 - original_volume) * 30

        combined = AudioSegment.from_mono_audiosegments(left, right)

        # Export to memory
        output_buffer = BytesIO()
        combined.export(output_buffer, format="mp3")
        output_buffer.seek(0)

        return send_file(output_buffer, mimetype="audio/mpeg", as_attachment=True, download_name="binaural_output.mp3")

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({'error': 'Processing failed', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
