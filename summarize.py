import csv
import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

# Initialize Cerebras client
load_dotenv()
client = Cerebras(api_key=os.environ.get("CEREBRAS_KEY"))

def summarize_with_cerebras(transcript: str, model="qwen-3-coder-480b") -> str:
    """Summarize a meeting transcript using Cerebras Cloud API"""

    if not transcript.strip():
        return ""

    # More instructive prompt, avoids the model echoing "Summary:"
    system_message = (
        "You are a professional meeting assistant. Your task is to read transcripts of city council meetings "
        "and summarize the key points, decisions, speakers, and topics discussed. Be concise but complete."
        "Each transcript are grabbed from the start, middle or towards the end of the meeting, so try to make"
        " the summary as complete as possible without repeating the transcript text or without any introduction to the meeting."
    )

    user_prompt = (
        "Please summarize the following meeting transcript. Do not include the words 'Summary:' or 'Meeting Summary'. Do not repeat the transcript text."
        "Do not mention anything about the existence of a transcript and provide a plain language paragraph summarizing what happened during the transcript:\n\n"
        f"{transcript.strip()}"
    )

    try:
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            model=model,
            stream=True,
            max_completion_tokens=1024,
            temperature=0.7,
            top_p=0.8
        )

        summary = ""
        for chunk in stream:
            summary += chunk.choices[0].delta.content or ""
        return summary.strip()

    except Exception as e:
        return f"[Error during summarization: {e}]"

def summarize_csv(input_csv: str, output_csv: str):
    with open(input_csv, newline='', encoding='utf-8') as infile, \
         open(output_csv, "w", newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = [f if f != "transcript" else "summary_transcript" for f in reader.fieldnames]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            transcript = row.get("transcript", "")
            print(f">>> Summarizing transcript {i} (agenda_id={row.get('agenda_id', 'N/A')})...")

            try:
                summary = summarize_with_cerebras(transcript)
                row["summary_transcript"] = summary
            except Exception as e:
                print(f"!!! Error summarizing row {i}: {e}")
                row["summary_transcript"] = "[Error during summarization]"

            row.pop("transcript", None)  # Remove original transcript
            writer.writerow(row)

        print(">>> All summaries complete.")

# Example usage
summarize_csv("agendas_with_transcripts.csv", "agendas_with_summary.csv")
