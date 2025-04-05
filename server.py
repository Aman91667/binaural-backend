from flask import Flask, request, jsonify
from pydub import AudioSegment
from pydub.effects import pan
from io import BytesIO
from flask_cors import CORS
import base64

app = Flask(__name__)

# Allow CORS from specific origins with credentials if required
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:3000",
    "https://binaural-backend.onrender.com"
], "supports_credentials": True}})

# Utility function to simulate dimensional panning effect
def apply_dimensional_effect(audio: AudioSegment, dimensionality: int) -> AudioSegment:
    duration_ms = len(audio)
    segment_duration = max(500, duration_ms // (dimensionality * 2))
    
    output = AudioSegment.silent(duration=0)
    direction = 1
    
    for i in range(0, duration_ms, segment_duration):
        segment = audio[i:i+segment_duration]
        pan_position = -1.0 if direction < 0 else 1.0
        panned_segment = pan(segment, pan_position)
        output += panned_segment
        direction *= -1

    return output.set_channels(2)

@app.route("/api/process", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    audio_file = request.files["audio"]
    dimensionality = int(request.form.get("dimensionality", 4))

    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_file)

        # Original audio to base64
        original_buffer = BytesIO()
        audio.export(original_buffer, format="mp3")
        original_base64 = base64.b64encode(original_buffer.getvalue()).decode("utf-8")

        # Apply immersive dimensional effect
        immersive_audio = apply_dimensional_effect(audio, dimensionality)
        immersive_buffer = BytesIO()
        immersive_audio.export(immersive_buffer, format="mp3")
        immersive_base64 = base64.b64encode(immersive_buffer.getvalue()).decode("utf-8")

        return jsonify({
            "original": original_base64,
            "processed": immersive_base64
        })

    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Error processing audio: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
