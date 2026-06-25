#!/usr/bin/env python3
"""Transcribe audio using Vosk offline speech recognition."""
import sys
import os
import json
import subprocess

# Default model path
DEFAULT_MODEL_PATH = os.path.expanduser("~/.vosk/models/vosk-model-small-ru-0.22")
MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", DEFAULT_MODEL_PATH)

def transcribe(audio_path):
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)
    
    # Convert to 16kHz mono WAV using ffmpeg
    wav_path = "/tmp/vosk_input.wav"
    cmd = [
        "ffmpeg", "-y", "-i", audio_path,
        "-ar", "16000", "-ac", "1", "-f", "wav", wav_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    from vosk import Model, KaldiRecognizer
    
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}", file=sys.stderr)
        print("Download a model from https://alphacephei.com/vosk/models", file=sys.stderr)
        sys.exit(1)
    
    model = Model(MODEL_PATH)
    
    with open(wav_path, "rb") as wf:
        rec = KaldiRecognizer(model, 16000)
        rec.SetWords(True)
        
        results = []
        while True:
            data = wf.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part = json.loads(rec.Result())
                if part.get("text"):
                    results.append(part["text"])
        
        final = json.loads(rec.FinalResult())
        if final.get("text"):
            results.append(final["text"])
    
    # Cleanup
    if os.path.exists(wav_path):
        os.remove(wav_path)
    
    return " ".join(results)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe.py <audio_file>", file=sys.stderr)
        print("Set VOSK_MODEL_PATH env var to use a specific model.", file=sys.stderr)
        sys.exit(1)
    
    text = transcribe(sys.argv[1])
    print(text)
