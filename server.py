from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pydub import AudioSegment
from pydub.effects import pan
from io import BytesIO
import math

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS

# ✅ Optimized panning effect
def apply_dimensional_effect(audio: AudioSegment, dimensionality: int) -> AudioSegment:
    duration_ms = len(audio)
    segment_duration = max(100, duration_ms // (dimensionality * 20))
    output = AudioSegment.silent(duration=0)

    for i in range(0, duration_ms, segment_duration):
        segment = audio[i:i+segment_duration]
        t_ratio = i / duration_ms
        angle = 2 * math.pi * t_ratio * dimensionality
        pan_val = math.sin(angle)
        output += pan(segment, pan_val)

    return output.set_channels(2)

@app.route("/api/process", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    audio_file = request.files["audio"]
    dimensionality = int(request.form.get("dimensionality", 4))

    try:
        audio = AudioSegment.from_file(audio_file)

        immersive_audio = apply_dimensional_effect(audio, dimensionality)
        immersive_buffer = BytesIO()
        immersive_audio.export(immersive_buffer, format="mp3")
        immersive_buffer.seek(0)

        return send_file(
            immersive_buffer,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="immersive_output.mp3"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
