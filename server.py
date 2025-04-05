from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import os
import io
import zipfile
import tempfile

app = Flask(__name__)
CORS(app)  # ✅ Enables CORS for all origins

@app.route("/")
def home():
    return jsonify({"status": "Server running successfully."})

@app.route("/api/process", methods=["POST"])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    audio_file = request.files['audio']
    dimensionality = int(request.form.get('dimensionality', 4))

    # Load uploaded audio
    audio = AudioSegment.from_file(audio_file)

    # Apply basic fake 8D/16D effect by panning left and right
    segments = []
    for i in range(dimensionality):
        pan = -1.0 + 2.0 * (i / (dimensionality - 1))  # Pans from -1.0 to +1.0
        segment = audio.pan(pan)
        segments.append(segment)

    # Concatenate processed segments for effect
    final_mix = AudioSegment.empty()
    for seg in segments:
        final_mix += seg

    # Save both original and processed audio to memory
    original_io = io.BytesIO()
    processed_io = io.BytesIO()
    audio.export(original_io, format="mp3")
    final_mix.export(processed_io, format="mp3")
    original_io.seek(0)
    processed_io.seek(0)

    # Create a ZIP containing both files
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('original.mp3', original_io.read())
        zip_file.writestr('mixed.mp3', processed_io.read())
    zip_buffer.seek(0)

    return send_file(zip_buffer, mimetype='application/zip', as_attachment=False, download_name="binaural_mix.zip")

if __name__ == "__main__":
    app.run(debug=True)
