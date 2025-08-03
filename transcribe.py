print(">>> Importing...")

import whisperx
import torch
import torchaudio
from pyannote.audio import Pipeline
from pyannote.core import Segment
from datetime import timedelta
import subprocess
import copy
from datetime import timedelta
import time
import os
from dotenv import load_dotenv

print(">>> Imports complete.")

# Helper function to format timestamps
def format_timestamp(seconds: float) -> str:
    # Format seconds as HH:MM:SS (drop microseconds)
    td = timedelta(seconds=int(seconds))
    return str(td)

# Helper function to manually assign speakers to words
def manual_assign_word_speakers(diarization, aligned_result):
    result = copy.deepcopy(aligned_result)

    for segment in result["segments"]:
        for word in segment.get("words", []):
            word_start = word["start"]
            word_end = word["end"]
            word_segment = Segment(word_start, word_end)

            overlaps = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                overlap_duration = max(0, min(word_segment.end, turn.end) - max(word_segment.start, turn.start))
                if overlap_duration > 0:
                    overlaps.append((speaker, overlap_duration))

            if overlaps:
                speaker = max(overlaps, key=lambda x: x[1])[0]
            else:
                speaker = "Unknown"

            word["speaker"] = speaker

        speakers = [w.get("speaker", "Unknown") for w in segment.get("words", []) if "speaker" in w]
        if speakers:
            segment["speaker"] = max(set(speakers), key=speakers.count)
        else:
            segment["speaker"] = "Unknown"

    return result

# Helper function to trim audio using ffmpeg
def trim_audio(input_file, output_file, duration_seconds=300):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-t", str(duration_seconds),
        "-c", "copy",
        output_file
    ]
    subprocess.run(command, check=True)

# CONFIG
AUDIO_FILE = "sanfrancisco_27e3a9ca-ed35-4520-a5c2-ccfee41a7671.mp3"
MODEL_SIZE = "small"  # Options: tiny, base, small, medium, large
HF_TOKEN = os.environ.get("HF_KEY")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f">>> DEVICE: {DEVICE}")

# # Trim audio if necessary
# print(">>> Trimming...")
# trim_audio(AUDIO_FILE, "trimmed.mp3", 600) # Adjust trim here if needed
# AUDIO_FILE = "trimmed.mp3"

# Starting benchmark
bm_start_time = time.time()
print(">>> Starting benchmark timer.")

# Load and transcribe
print(">>> Loading WhisperX model...")
model = whisperx.load_model(MODEL_SIZE, DEVICE, compute_type="float32")
print(">>> Loading and transcribing audio...")
audio = whisperx.load_audio(AUDIO_FILE)
transcription_result = model.transcribe(audio)
print(">>> Performing alignment...")
model_a, metadata = whisperx.load_align_model(language_code=transcription_result["language"], device=DEVICE)
aligned_result = whisperx.align(transcription_result["segments"], model_a, metadata, audio, DEVICE)

# Benchmarking transcription as variable
print(">>> Transcription complete.")
transcript_time = time.time() - bm_start_time

# Speaker Diarization with pyannote
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(">>> Loading pyannote diarization model...")
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=HF_TOKEN).to(DEVICE)
print(">>> Running speaker diarization...")
diarization = pipeline(AUDIO_FILE)
print(">>> Assigning speakers to transcription...")
transcription = manual_assign_word_speakers(diarization, aligned_result)

output_file = "transcript.txt"
print(">>> Writing transcript...")
with open(output_file, "w", encoding="utf-8") as f:
    for segment in transcription["segments"]:
        start_time = format_timestamp(segment["start"])
        speaker = segment.get("speaker", "Unknown")
        text = segment["text"].strip()
        f.write(f"({start_time}) {speaker}: {text}\n")

print(">>> Transcription written.")

# Printing time taken
bm_end_time = time.time()
elapsed_time = bm_end_time - bm_start_time
print(f">>> Total time taken: {elapsed_time:.2f} seconds")
print(f">>> Transcription time: {transcript_time:.2f} seconds")
print(f">>> Diarization time: {(elapsed_time - transcript_time):.2f} seconds")