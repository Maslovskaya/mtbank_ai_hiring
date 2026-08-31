import os

from pyannote.audio import Pipeline

_pipeline = None  # пока не загружена


def get_pipeline():
    global _pipeline
    if _pipeline is None:  # первый вызов — грузим и запоминаем
        _pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=os.environ["HF_TOKEN"],
        )
    return _pipeline  # повторные вызовы — отдаём уже готовую


def diarize(audio_path):
    pipeline = get_pipeline()
    result = pipeline(audio_path)
    return [
        {"start": turn.start, "end": turn.end, "speaker": speaker}
        for turn, _, speaker in result.speaker_diarization.itertracks(yield_label=True)
    ]
