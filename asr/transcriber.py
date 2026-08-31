from faster_whisper import WhisperModel

_model = None  # пока не загружена


def get_model():
    global _model
    if _model is None:          # первый вызов — грузим и запоминаем
        _model = WhisperModel("medium", device="cpu", compute_type="int8")
    return _model                # повторные вызовы — отдаём уже готовую


def transcribe(audio_path, language="ru"):
    model = get_model()
    segments, info = model.transcribe(audio_path, language=language)
    return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]
