"""
AudioTranscriptionPipeline.py

Sanitized hackathon edition.

This module represents the audio-to-text stage of ConversaShield.
The production STT implementation is intentionally omitted.
"""

from pathlib import Path
import pandas as pd


INPUT_DIR = Path("recordings")
OUTPUT_CSV = Path("output/call_transcripts_clean.csv")


def transcribe_audio_file(audio_path: Path) -> str:
    """
    Placeholder for the production open-source STT pipeline.

    The commercial version includes:
    - noisy call-center audio preprocessing
    - speaker separation
    - transcription
    - transcript cleaning

    Not included in this public hackathon edition.
    """
    return "Ομιλητής 1: Καλημέρα σας.\nΟμιλητής 2: Καλημέρα."


def main():
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for index, audio_path in enumerate(INPUT_DIR.glob("*.*"), start=1):
        conversation = transcribe_audio_file(audio_path)

        rows.append({
            "call_sequence": index,
            "filename": audio_path.name,
            "audio_path": str(audio_path),
            "duration_sec": "",
            "speaker_count": "",
            "conversation": conversation,
            "llm_input": f"Αρχείο: {audio_path.name}\n\n{conversation}",
            "plain_transcript": conversation,
            "quality_code": "",
            "class_code": "",
            "review_code": "",
            "processing_time_sec": "",
            "error_message": ""
        })

    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Created sanitized transcript file: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()