from agents.llm_client import DEFAULT_MODEL, get_client
from agents.utils import format_transcript
from llm_json import parse_json_response

SYSTEM_PROMPT = """Ты — агент-суммаризатор в контакт-центре банка.
Тебе дан транскрипт телефонного разговора между оператором и клиентом.

Составь:
1. summary — краткое резюме разговора, 3-5 предложений: с чем обратился клиент,
   что ответил/предложил оператор, чем закончился разговор.
2. action_items — список КОНКРЕТНЫХ выполнимых действий, которые нужно сделать
   после звонка (например, "Отправить инструкцию на email клиента",
   "Перезвонить клиенту через 3 дня"). Не пиши общие фразы вроде "помочь клиенту" —
   только конкретные, проверяемые пункты. Если действий не требуется — верни пустой список.

Ответь СТРОГО в формате JSON, без пояснений и без markdown-разметки:
{"summary": "...", "action_items": ["...", "..."]}"""


def summarize(segments):
    """
    segments: список словарей {"start", "end", "text", "speaker"} — транскрипт с ролями.
    Возвращает {"summary": "...", "action_items": [...]}
    """
    client = get_client()
    transcript_text = format_transcript(segments)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript_text},
        ],
    )

    result = parse_json_response(response.choices[0].message.content)
    return result


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    from asr.transcriber import transcribe
    from asr.diarizer import diarize
    from asr.aligner import assign_speakers
    from asr.roles import assign_roles

    audio = "test_data/dialog_full.wav"
    asr_segments = transcribe(audio)
    diarization_segments = diarize(audio)
    segments = assign_speakers(asr_segments, diarization_segments)
    segments = assign_roles(segments)

    print(summarize(segments))
