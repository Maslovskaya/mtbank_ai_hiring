from faster_whisper import WhisperModel

from settings import (
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_LANGUAGE,
    WHISPER_MODEL,
)

_model = None  # пока не загружена


def get_model():
    global _model
    if _model is None:          # первый вызов — грузим и запоминаем
        _model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
    return _model                # повторные вызовы — отдаём уже готовую


def transcribe(audio_path, language=WHISPER_LANGUAGE):
    model = get_model()
    segments, info = model.transcribe(audio_path, language=language)
    return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]
