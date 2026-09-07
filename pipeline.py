"""
Оркестрация анализа звонка — сердце системы.

analyze() последовательно проводит запись через два слоя:

    ASR-слой        аудио → транскрипт с ролями говорящих
    Multi-agent     транскрипт → классификация, качество, compliance, резюме

и собирает результат в формат, описанный в задании.

Роль супервизора выполняет сама эта функция: агенты независимы друг от друга,
получают один и тот же транскрипт и не обмениваются результатами, поэтому
отдельный фреймворк оркестрации (LangGraph и подобные) здесь не нужен.
"""

import json

from dotenv import load_dotenv

from agents.classifier import classify
from agents.compliance import check_compliance
from agents.quality import check_quality
from agents.summarizer import summarize
from asr.aligner import assign_speakers
from asr.diarizer import diarize
from asr.roles import assign_roles
from asr.transcriber import transcribe
from logger import log_event, run_agent, run_stage, setup_logging

# .env и логирование настраиваются один раз при импорте модуля,
# а не при каждом вызове analyze()
load_dotenv()
setup_logging()


def analyze(audio_path):
    """
    Полный анализ записи звонка.

    audio_path: путь к аудиофайлу (WAV, MP3, OGG)

    Возвращает словарь с ключами transcript, classification, quality_score,
    compliance, summary, action_items.
    """
    log_event("analysis_started", audio_path=audio_path)

    # --- ASR-слой: получаем транскрипт с разметкой по ролям ---
    asr_segments = run_stage("transcribe", transcribe, audio_path)
    diarization_segments = run_stage("diarize", diarize, audio_path)

    # транскрипт и диаризация считаются независимо — здесь они соединяются:
    # каждой реплике присваивается говорящий, а затем его роль
    segments = run_stage("align", assign_speakers, asr_segments, diarization_segments)
    segments = run_stage("assign_roles", assign_roles, segments)

    # --- Multi-agent слой: четыре независимых агента на одном транскрипте ---
    classification = run_agent("classifier", classify, segments)
    quality_score = run_agent("quality", check_quality, segments)
    compliance = run_agent("compliance", check_compliance, segments)
    summary = run_agent("summarizer", summarize, segments)

    log_event("analysis_finished", segments=len(segments))

    return {
        "transcript": segments,
        "classification": classification,
        "quality_score": quality_score,
        "compliance": compliance,
        # суммаризатор отдаёт два поля одним словарём,
        # а в схеме ответа они лежат на верхнем уровне
        "summary": summary["summary"],
        "action_items": summary["action_items"],
    }


if __name__ == "__main__":
    result = analyze("test_data/dialog_full.wav")
    print(json.dumps(result, ensure_ascii=False, indent=2))
