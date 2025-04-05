from pydub import AudioSegment
import math
import os

def process_binaural(input_path: str, output_path: str, dimensionality: int = 2):
    # Validate file
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    # Load audio
    audio = AudioSegment.from_file(input_path)

    # Convert to stereo if not already
    if audio.channels == 1:
        audio = audio.set_channels(2)

    # Normalize for safety
    audio = audio.normalize()

    # Define cycle length for spatial panning based on dimensionality
    # The higher the dimensionality, the faster and deeper the motion
    cycle_ms = 10000 / dimensionality  # total time of one L-R-L cycle in ms

    processed = AudioSegment.empty()

    for ms in range(0, len(audio), 50):  # process every 50ms
        segment = audio[ms:ms + 50]

        # Calculate panning value using a sine wave to simulate circular motion
        angle = 2 * math.pi * (ms % cycle_ms) / cycle_ms
        pan_value = math.sin(angle)  # range: -1 (left) to +1 (right)

        panned = segment.pan(pan_value)
        processed += panned

    # Export the result
    processed.export(output_path, format="mp3", bitrate="192k")
