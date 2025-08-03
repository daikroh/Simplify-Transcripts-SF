import pandas as pd
import numpy as np
import csv

def merge_transcript_and_summary(transcript_csv, summary_csv, output_csv):
    # Load both CSVs
    df_transcript = pd.read_csv(transcript_csv)
    df_summary = pd.read_csv(summary_csv)

    # Round down start_time and end_time
    for df in [df_transcript, df_summary]:
        df['start_time'] = np.floor(df['start_time']).astype(int)
        df['end_time'] = np.floor(df['end_time']).astype(int)
        df.replace("Summary not available.", "", inplace=True)
        df.fillna("", inplace=True)

    # Merge on shared columns
    merged = pd.merge(
        df_transcript,
        df_summary,
        on=["agenda_id", "record_id", "title", "start_time", "end_time"],
        how="inner"
    )
   
    # Rename summary_transcript to summary if needed
    if 'summary_transcript' in merged.columns:
        merged.rename(columns={'summary_transcript': 'summary'}, inplace=True)

    # Drop rows where transcript OR summary is missing/empty/invalid
    merged = merged[
        (merged['transcript'].notna()) &
        (merged['summary'].notna()) &
        (~merged['transcript'].isin(["", "nan", "None", "Summary not available."])) &
        (~merged['summary'].isin(["", "nan", "None", "Summary not available."]))
    ]

    # Save output
    merged.to_csv(output_csv, index=False)
    print(f"Merged file saved to {output_csv}")


def combine_merged_files(file_list, output_csv):
    # Load and concatenate all merged CSVs
    dfs = [pd.read_csv(file) for file in file_list]
    combined = pd.concat(dfs, ignore_index=True)

    # Optional: remove duplicates based on all columns
    combined.drop_duplicates(inplace=True)

    # Save combined result
    combined.to_csv(output_csv, index=False)
    print(f"Combined file saved to {output_csv}")

def main():
    merge_transcript_and_summary("agendas_with_transcripts.csv", "agendas_with_summary.csv", "merged_1.csv")
    merge_transcript_and_summary("agendas_with_transcripts_meeting2.csv", "agendas_with_summary_meeting2.csv", "merged_2.csv")
    combine_merged_files(["merged_1.csv", "merged_2.csv"], "final_combined.csv")

if __name__ == "__main__":
    main()
