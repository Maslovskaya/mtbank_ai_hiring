import json
import os
from openai import OpenAI


def assign_roles(segments):
    """
    segments: список словарей {"start", "end", "text", "speaker"},
    где speaker — метка вида "SPEAKER_00"/"SPEAKER_01".

    Возвращает тот же список, но с speaker, заменённым на "Оператор"/"Клиент".
    """
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )

    dialogue_text = "\n".join(f'{seg["speaker"]}: {seg["text"]}' for seg in segments)

    # TODO 1: напиши system-промпт — объясни модели задачу: перед ней диалог
    #   оператора банка и клиента с метками SPEAKER_00/SPEAKER_01, нужно определить,
    #   какая метка — Оператор, какая — Клиент, и вернуть СТРОГО JSON вида
    #   {"SPEAKER_00": "Оператор", "SPEAKER_01": "Клиент"}, без пояснений вокруг
    
    SYSTEM_PROMPT = """Ты анализируешь транскрипт телефонного звонка в банк.
    Тебе дан диалог, где реплики помечены метками вида SPEAKER_00, SPEAKER_01 —
    это анонимные метки говорящих, кто есть кто заранее неизвестно.
    Определи, какая метка — Оператор (сотрудник банка: здоровается от лица банка,
    предлагает помощь, отвечает на вопросы), а какая — Клиент (обращается с вопросом
    или проблемой).
    Ответь СТРОГО в формате JSON, без пояснений, без markdown-разметки, без ```:
    {"SPEAKER_00": "Оператор", "SPEAKER_01": "Клиент"}
    Ключи должны точно совпадать с метками, которые встретились в диалоге."""

    # TODO 2: вызови client.chat.completions.create(model=..., messages=[
    #   {"role": "system", "content": твой промпт из TODO 1},
    #   {"role": "user", "content": dialogue_text},
    # ]) — model возьми ту же, что уже использовала раньше ("qwen/qwen3.8-27b")
    
    response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": dialogue_text},
    ],)

    # TODO 3: распарси JSON из ответа: role_map = json.loads(response.choices[0].message.content)
    
    role_map = json.loads(response.choices[0].message.content)

    # TODO 4: пройдись циклом по segments, для каждого seg замени
    #   seg["speaker"] = role_map[seg["speaker"]]
    for seg in segments:
        seg["speaker"] = role_map[seg["speaker"]]

    return segments
