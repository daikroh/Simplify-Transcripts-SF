print(">>> Importing...")

import whisperx
import os
import torch

# Check cuda version
print(torch.cuda.get_device_name(0))
print(torch.version.cuda)

import torchaudio
from pyannote.audio import Pipeline
from datetime import timedelta
import subprocess

def trim_audio(input_file, output_file, duration_seconds=300):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-t", str(duration_seconds),
        "-c", "copy",
        output_file
    ]
    subprocess.run(command, check=True)


print(">>> Imports complete.")

# CONFIG
AUDIO_FILE = "sanfrancisco_27e3a9ca-ed35-4520-a5c2-ccfee41a7671.mp3"
MODEL_SIZE = "small"  # Options: tiny, base, small, medium, large
HF_TOKEN = "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"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f">>> DEVICE: {DEVICE}")

print(">>> Trimming...")
trim_audio(AUDIO_FILE, "trimmed.mp3")
AUDIO_FILE = "trimmed.mp3"

# Load and transcribe
print(">>> Loading WhisperX model...")
model = whisperx.load_model(MODEL_SIZE, DEVICE, compute_type="float32")
print(">>> Loading and transcribing audio...")
audio = whisperx.load_audio(AUDIO_FILE)
transcription_result = model.transcribe(audio)
print(">>> Performing alignment...")
model_a, metadata = whisperx.load_align_model(language_code=transcription_result["language"], device=DEVICE)
aligned_result = whisperx.align(transcription_result["segments"], model_a, metadata, audio, DEVICE)

# Speaker Diarization with pyannote
print(">>> Loading pyannote diarization model...")
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=HF_TOKEN)
print(">>> Running speaker diarization...")
diarization = pipeline(AUDIO_FILE)

# Assign speaker labels to transcript segments
print(">>> Combining transcript with speaker labels...")
segments = aligned_result["segments"]
speaker_segments = []
for segment in segments:
    segment_start = segment["start"]
    segment_end = segment["end"]
    text = segment["text"]

    # Match with speaker using diarization annotation
    matched_speakers = diarization.crop(segment_start, segment_end)

    speakers = list(set(label for _, _, label in matched_speakers.itertracks(yield_label=True)))
    speaker = speakers[0] if speakers else "Unknown"

    speaker_segments.append({
        "start": segment_start,
        "end": segment_end,
        "speaker": speaker,
        "text": text.strip()
    })

# Save Output
print(">>> Writing transcript to transcript.txt...")
with open("transcript.txt", "w", encoding="utf-8") as f:
    for seg in speaker_segments:
        start = str(timedelta(seconds=int(seg["start"])))
        end = str(timedelta(seconds=int(seg["end"])))
        f.write(f"[{start} - {end}] {seg['speaker']}: {seg['text']}\n")

print(">>> Transcription complete.")
