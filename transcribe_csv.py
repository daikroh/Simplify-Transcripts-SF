# transcribe_csv.py
"""
This script transcribes audio segments from a CSV file containing agenda items,
aligns the transcriptions with the audio, and saves the results back to a new CSV file.
"""

import whisperx
import torch
import torchaudio
from pyannote.audio import Pipeline
from pyannote.core import Segment
from datetime import timedelta
import subprocess
import copy
import time
import csv
import os

# CONFIG
AUDIO_FILE = "sanfrancisco_4f57e5cf-334b-48c4-9f3c-f3bd434850a2.mp3"
AGENDA_FILE = "agendas.csv"
OUTPUT_CSV = "agendas_with_transcripts.csv"
MODEL_SIZE = "small"
HF_TOKEN = os.environ.get("HF_KEY")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TORCH_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Helper Functions
# Helper function to format timestamps
def format_timestamp(seconds: float) -> str:
    """Convert seconds into HH:MM:SS format"""
    td = timedelta(seconds=int(seconds))
    return str(td)

# Helper function to manually assign speakers to words
def manual_assign_word_speakers(diarization, aligned_result):
    """Assign speaker labels to words and segments"""
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
            speaker = max(overlaps, key=lambda x: x[1])[0] if overlaps else "Unknown"
            word["speaker"] = speaker
        speakers = [w.get("speaker", "Unknown") for w in segment.get("words", []) if "speaker" in w]
        segment["speaker"] = max(set(speakers), key=speakers.count) if speakers else "Unknown"
    return result

# Helper function to trim audio using ffmpeg
def trim_audio(input_file, output_file, start_sec, end_sec=None):
    """Trim audio file using ffmpeg"""
    command = ["ffmpeg", "-y", "-i", input_file, "-ss", str(start_sec)]
    if end_sec is not None:
        duration = end_sec - start_sec
        command += ["-t", str(duration)]
    command += ["-c", "copy", output_file]
    subprocess.run(command, check=True)

# Helper function to get audio duration
def get_audio_duration(file_path: str) -> float:
    """Get duration of audio file in seconds"""
    info = torchaudio.info(file_path)
    return info.num_frames / info.sample_rate

# Helper function to load agenda segments from CSV and convert times
def load_agenda_segments(csv_path: str, audio_duration: float) -> list:
    """Read agenda segments from CSV and convert times"""
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start = float(row["start_time"])
            end = float(row["end_time"])
            if end >= 999999:
                row["end_time"] = str(audio_duration)
            rows.append(row)
    return rows

# Helper function to process a single agenda segment
def process_segment(
    agenda_id: str,
    start: float,
    end: float,
    audio_file: str,
    model,
    align_model,
    align_metadata,
    diarization_pipeline,
) -> str:
    """Transcribe and diarize a single audio segment"""
    trimmed_file = f"temp_segment_{agenda_id}.mp3"
    trim_audio(audio_file, trimmed_file, start, end)

    # Transcribe
    audio = whisperx.load_audio(trimmed_file)
    result = model.transcribe(audio)

    # Align
    aligned = whisperx.align(result["segments"], align_model, align_metadata, audio, DEVICE)

    # Diarize
    diarization = diarization_pipeline(trimmed_file)
    final_result = manual_assign_word_speakers(diarization, aligned)

    # Format transcript
    lines = []
    for segment in final_result["segments"]:
        seg_start = format_timestamp(segment["start"] + start)
        speaker = segment.get("speaker", "Unknown")
        text = segment["text"].strip()
        lines.append(f"({seg_start}) {speaker}: {text}")

    os.remove(trimmed_file)
    return "\n".join(lines)

# Helper function to save agenda rows with transcripts to CSV
def save_agenda_with_transcripts(rows: list, out_csv: str):
    """Write updated rows to output CSV"""
    fieldnames = list(rows[0].keys())
    with open(out_csv, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# Main function to process all agenda segments
def main():
    print(f">>> Using device: {DEVICE}")

    # Load WhisperX model
    print(">>> Loading WhisperX model...")
    model = whisperx.load_model(MODEL_SIZE, DEVICE, compute_type="float32")

    # Lazy-load align model
    model_a = None
    metadata = None

    # Load diarization model
    print(">>> Loading pyannote diarization model...")
    diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=HF_TOKEN).to(TORCH_DEVICE)

    # Get duration of full audio
    audio_duration = get_audio_duration(AUDIO_FILE)

    # Load and normalize agenda rows
    agenda_rows = load_agenda_segments(AGENDA_FILE, audio_duration)

    # Process each agenda segment
    for row in agenda_rows:
        agenda_id = row["agenda_id"]
        start = float(row["start_time"])
        end = float(row["end_time"])
        print(f">>> Processing agenda_id={agenda_id} from {start} to {end} seconds...")

        # Lazy load align model after first language detection
        if model_a is None:
            audio = whisperx.load_audio(AUDIO_FILE)
            lang_result = model.transcribe(audio)
            model_a, metadata = whisperx.load_align_model(language_code=lang_result["language"], device=DEVICE)

        # Process segment and store transcript
        transcript = process_segment(agenda_id, start, end, AUDIO_FILE, model, model_a, metadata, diarization_pipeline)
        row["transcript"] = transcript

    # Save updated CSV
    print(">>> Writing output to:", OUTPUT_CSV)
    save_agenda_with_transcripts(agenda_rows, OUTPUT_CSV)
    print(">>> Done.")

if __name__ == "__main__":
    main()
