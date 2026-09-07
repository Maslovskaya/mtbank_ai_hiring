import json
import time

from dotenv import load_dotenv

from asr.transcriber import transcribe
from asr.diarizer import diarize
from asr.aligner import assign_speakers
from asr.roles import assign_roles

from agents.classifier import classify
from agents.quality import check_quality
from agents.compliance import check_compliance
from agents.summarizer import summarize

from logger import run_agent, setup_logging

setup_logging()

def analyze(audio_path):
    load_dotenv()

    t0 = time.time()
    asr_segments = transcribe(audio_path)
    t1 = time.time()
    print(f"transcribe: {t1 - t0:.1f} сек")

    diarization_segments = diarize(audio_path)
    t2 = time.time()
    print(f"diarize: {t2 - t1:.1f} сек")

    segments = assign_speakers(asr_segments, diarization_segments)
    segments = assign_roles(segments)
    t3 = time.time()
    print(f"assign_speakers+roles: {t3 - t2:.1f} сек")

    classification = run_agent("classifier", classify, segments)
    quality_score = run_agent("quality", check_quality, segments)
    compliance = run_agent("compliance", check_compliance, segments)
    summary_result = run_agent("summarizer", summarize, segments)

    t4 = time.time()
    print(f"4 агента (последовательно): {t4 - t3:.1f} сек")

    result = {
        "transcript": segments,
        "classification": classification,
        "quality_score": quality_score,
        "compliance": compliance,
        "summary": summary_result["summary"],
        "action_items": summary_result["action_items"],
    }

    print(f"ИТОГО: {time.time() - t0:.1f} сек")
    return result

if __name__ == "__main__":
    print(analyze("test_data/dialog_full.wav"))
