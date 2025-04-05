from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pydub import AudioSegment
from pydub.generators import Sine
import io
import zipfile

app = Flask(__name__)

# Allow frontend from localhost:3000 to access the backend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

@app.route('/api/process', methods=['POST'])
def process_audio():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        base_freq = int(request.form.get('baseFreq', 200))
        beat_diff = int(request.form.get('beatDiff', 10))

        print(f"📥 File received: {file.filename}")
        print(f"🎶 Base Frequency: {base_freq}, Beat Difference: {beat_diff}")

        # Load original audio
        audio = AudioSegment.from_file(file)
        duration_ms = len(audio)

        # Generate left/right sine wave tracks
        left_tone = Sine(base_freq).to_audio_segment(duration=duration_ms).pan(-1).apply_gain(-15)
        right_tone = Sine(base_freq + beat_diff).to_audio_segment(duration=duration_ms).pan(1).apply_gain(-15)

        # Fade in/out
        left_tone = left_tone.fade_in(1000).fade_out(1000)
        right_tone = right_tone.fade_in(1000).fade_out(1000)

        # Mix
        binaural_beat = left_tone.overlay(right_tone)
        mixed = audio.overlay(binaural_beat)

        # Export all 3 files to memory
        original_io = io.BytesIO()
        binaural_io = io.BytesIO()
        mixed_io = io.BytesIO()

        audio.export(original_io, format="mp3")
        binaural_beat.export(binaural_io, format="mp3")
        mixed.export(mixed_io, format="mp3")

        # ZIP them
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            zipf.writestr("original.mp3", original_io.getvalue())
            zipf.writestr("binaural.mp3", binaural_io.getvalue())
            zipf.writestr("mixed.mp3", mixed_io.getvalue())

        zip_buffer.seek(0)
        print("✅ All audio files processed and zipped.")
        return send_file(zip_buffer, as_attachment=True, download_name="binaural_pack.zip", mimetype="application/zip")

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
