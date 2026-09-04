from agents.llm_client import call_llm_json


def assign_roles(segments):
    """
    segments: список словарей {"start", "end", "text", "speaker"},
    где speaker — метка вида "SPEAKER_00"/"SPEAKER_01".

    Возвращает тот же список, но с speaker, заменённым на "Оператор"/"Клиент".
    """
    dialogue_text = "\n".join(f'{seg["speaker"]}: {seg["text"]}' for seg in segments)

    SYSTEM_PROMPT = """Ты анализируешь транскрипт телефонного звонка в банк.
    Тебе дан диалог, где реплики помечены метками вида SPEAKER_00, SPEAKER_01 —
    это анонимные метки говорящих, кто есть кто заранее неизвестно.
    Определи, какая метка — Оператор (сотрудник банка: здоровается от лица банка,
    предлагает помощь, отвечает на вопросы), а какая — Клиент (обращается с вопросом
    или проблемой).
    Ответь СТРОГО в формате JSON, без пояснений, без markdown-разметки, без ```:
    {"SPEAKER_00": "Оператор", "SPEAKER_01": "Клиент"}
    Ключи должны точно совпадать с метками, которые встретились в диалоге."""

    role_map = call_llm_json(SYSTEM_PROMPT, dialogue_text)

    for seg in segments:
        seg["speaker"] = role_map.get(seg["speaker"], seg["speaker"])

    return segments
