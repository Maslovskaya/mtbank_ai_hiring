import json

from dotenv import load_dotenv

from asr.transcriber import transcribe
from asr.diarizer import diarize
from asr.aligner import assign_speakers
from asr.roles import assign_roles

from agents.classifier import classify
from agents.quality import check_quality
from agents.compliance import check_compliance
from agents.summarizer import summarize

def analyze(audio_path):
    """
    Полный анализ звонка: ASR + диаризация + роли + 4 агента.
    Возвращает JSON ровно по формату из ТЗ.
    """
    # TODO: собери segments так же, как в scripts/test_align.py
    #   (transcribe → diarize → assign_speakers → assign_roles)
    
    load_dotenv()

    # print("Транскрибирую...")
    asr_segments = transcribe(audio_path)
    # print("Диаризую...")
    diarization_segments = diarize(audio_path)

    segments = assign_speakers(asr_segments, diarization_segments)
    segments = assign_roles(segments)

    # print(json.dumps(result, ensure_ascii=False, indent=2))

    # TODO: вызови все 4 агента по очереди: classify(segments), check_quality(segments),
    #   check_compliance(segments), summarize(segments) — сохрани каждый результат
    #   в отдельную переменную
    
    classification = classify(segments)
    quality_score = check_quality(segments)
    compliance = check_compliance(segments)
    summary_result = summarize(segments)

    # TODO: собери и верни финальный словарь по схеме выше — обрати внимание,
    #   что summary и action_items нужно "распаковать" из результата summarize()
    
    result = {
        "transcript": segments,
        "classification": classification,
        "quality_score": quality_score,
        "compliance": compliance,
        "summary": summary_result["summary"],
        "action_items": summary_result["action_items"],
    }

    return result

if __name__ == "__main__":
    print(analyze("test_data/dialog_full.wav"))
