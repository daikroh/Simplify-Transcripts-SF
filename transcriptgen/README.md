# Transcript Processing Pipeline

A modular Python-based pipeline for scraping video content, transcribing audio, summarizing speech, and merging outputs into CSVs.

Main Technologies: WhisperX, pyannote, Cerebras, CUDA

---

## Project Structure

```
.
├── requirements.txt         # Python dependencies (May include unnecrssary dependencies)
├── webscrape.py             # Scrapes agenda, timestamp, and metadata from web pages
├── transcribe.py            # Transcribes a single audio file
├── transcribe_csv.py        # Transcribes an audio file with segments according to the agenda
├── summarize.py             # Summarizes transcriptions using a language model
├── merge_csvs.py            # Merges transcript and summary CSVs
```

---

## 🛠 Tips

- Use GPU (CUDA) for faster transcription and summarization.
- Make sure you’re not exceeding API rate limits for online models.
- Ensure proper installation of system dependencies for Whisper, pyannote, and etc.(like `ffmpeg`).