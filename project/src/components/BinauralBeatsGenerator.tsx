import React, { useState } from "react";
import axios from "axios";
import JSZip from "jszip";

const BinauralBeatsGenerator: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [baseFreq, setBaseFreq] = useState(200);
  const [beatFreq, setBeatFreq] = useState(10);
  const [loading, setLoading] = useState(false);
  const [audioUrls, setAudioUrls] = useState<{
    original?: string;
    binaural?: string;
    mixed?: string;
  }>({});

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleProcess = async () => {
    if (!file) {
      alert("Please upload a file first.");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("baseFreq", baseFreq.toString());
      formData.append("beatDiff", beatFreq.toString());

      const response = await axios.post("http://localhost:5000/api/process", formData, {
        responseType: "blob",
      });

      const zip = await JSZip.loadAsync(response.data);
      const files = {
        original: await zip.file("original.mp3")?.async("blob"),
        binaural: await zip.file("binaural.mp3")?.async("blob"),
        mixed: await zip.file("mixed.mp3")?.async("blob"),
      };

      setAudioUrls({
        original: files.original ? URL.createObjectURL(files.original) : undefined,
        binaural: files.binaural ? URL.createObjectURL(files.binaural) : undefined,
        mixed: files.mixed ? URL.createObjectURL(files.mixed) : undefined,
      });
    } catch (err) {
      console.error("Processing failed", err);
      alert("Error processing audio.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 min-h-screen flex items-center justify-center bg-gradient-to-r from-purple-700 via-pink-500 to-indigo-700 animate-gradient-shift">
      <div className="w-full max-w-xl text-white bg-black/60 backdrop-blur-md rounded-xl shadow-xl space-y-6 p-6">
        {/* 🎵 Waveform Animation */}
        <div className="flex justify-center h-12 items-end gap-1">
          {[...Array(32)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-purple-400 rounded-full animate-waveform"
              style={{
                height: `${10 + Math.random() * 90}%`,
                animationDelay: `${i * 0.1}s`,
              }}
            />
          ))}
        </div>

        <h1 className="text-3xl font-bold text-center mt-4">🎧 Binaural Beats Generator</h1>

        <input type="file" accept="audio/*" onChange={handleFileChange} className="w-full" />

        <label>Base Frequency: {baseFreq} Hz</label>
        <input
          type="range"
          min="100"
          max="1000"
          value={baseFreq}
          onChange={e => setBaseFreq(Number(e.target.value))}
          className="w-full"
        />

        <label>Beat Frequency: {beatFreq} Hz</label>
        <input
          type="range"
          min="1"
          max="40"
          value={beatFreq}
          onChange={e => setBeatFreq(Number(e.target.value))}
          className="w-full"
        />

        <button
          onClick={handleProcess}
          disabled={loading}
          className="bg-purple-600 hover:bg-purple-700 transition px-6 py-2 rounded-full font-medium disabled:opacity-50"
        >
          {loading ? "Processing..." : "Generate Binaural Pack"}
        </button>

        {audioUrls.original && (
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold">Original</h3>
              <audio controls src={audioUrls.original} className="w-full" />
            </div>
            <div>
              <h3 className="font-semibold">Binaural Beat</h3>
              <audio controls src={audioUrls.binaural} className="w-full" />
            </div>
            <div>
              <h3 className="font-semibold">Final Mix</h3>
              <audio controls src={audioUrls.mixed} className="w-full" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BinauralBeatsGenerator;
