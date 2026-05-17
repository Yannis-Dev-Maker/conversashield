"""
RunConversaShield.py

Runs the sanitized ConversaShield hackathon pipeline:
1. AudioTranscriptionPipeline.py
2. AnalyzeCallsGemma.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, title):
    print("=" * 80)
    print(title)
    print("=" * 80)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"{title} failed with exit code {result.returncode}")


def main():
    root = Path.cwd()

    transcription_script = root / "AudioTranscriptionPipeline.py"
    gemma_script = root / "AnalyzeCallsGemma.py"

    if not transcription_script.exists():
        raise FileNotFoundError(f"Missing file: {transcription_script}")

    if not gemma_script.exists():
        raise FileNotFoundError(f"Missing file: {gemma_script}")

    Path("recordings").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)

    run_command(
        [sys.executable, str(transcription_script)],
        "STEP 1/2 - ConversaShield transcript preparation"
    )

    run_command(
        [sys.executable, str(gemma_script)],
        "STEP 2/2 - Gemma QA analysis"
    )

    print("DONE")
    print("Clean transcripts: output/call_transcripts_clean.csv")
    print("Gemma QA analysis: output/call_llm_analysis.csv")


if __name__ == "__main__":
    main()