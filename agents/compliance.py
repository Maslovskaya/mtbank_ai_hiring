from agents.llm_client import DEFAULT_MODEL, get_client
from agents.utils import format_transcript
from llm_json import parse_json_response

FORBIDDEN_PHRASES = [
    "гарантированно одобрим",
    "100% одобрение",
    "точно одобрят",
    "без проверки",
    "без документов",
]


def find_forbidden_phrases(operator_text):
    """
    operator_text: весь текст реплик оператора одной строкой.
    Возвращает список найденных запрещённых фраз (пустой, если ничего не найдено).
    """
    operator_text = operator_text.lower()
    found = []

    for phrase in FORBIDDEN_PHRASES:
        if phrase in operator_text:
            found.append(phrase)

    return found


COMPLIANCE_SYSTEM_PROMPT = """Ты — агент compliance-контроля в контакт-центре банка.
Тебе дан транскрипт разговора оператора и клиента.

Проверь речь ОПЕРАТОРА на:
- некорректные/вводящие в заблуждение обещания (гарантии одобрения, нереалистичные условия)
- отсутствие обязательных пояснений там, где они нужны (например, если упоминается
  страховка — должно быть явно сказано, что она не обязательна)

Ответь СТРОГО в формате JSON:
{"issues": ["описание нарушения 1", "описание нарушения 2"]}
Если нарушений нет — {"issues": []}"""


def check_compliance(segments):
    operator_text = " ".join(seg["text"] for seg in segments if seg["speaker"] == "Оператор")
    found_by_regex = find_forbidden_phrases(operator_text)

    client = get_client()
    transcript_text = format_transcript(segments)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": COMPLIANCE_SYSTEM_PROMPT},
            {"role": "user", "content": transcript_text},
        ],
    )

    llm_result = parse_json_response(response.choices[0].message.content)

    all_issues = found_by_regex + llm_result["issues"]

    return {"passed": len(all_issues) == 0, "issues": all_issues}


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

    print(check_compliance(segments))


    bad_segments = [
        {"speaker": "Оператор", "text": "Добрый день! Мы гарантированно одобрим вам кредит без документов."},
        {"speaker": "Клиент", "text": "Отлично, спасибо."},
    ]
    print(check_compliance(bad_segments))