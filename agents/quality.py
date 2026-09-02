from agents.llm_client import DEFAULT_MODEL, get_client
from agents.utils import format_transcript
from llm_json import parse_json_response

SYSTEM_PROMPT = """Ты оцениваешь общениен обращений в контакт-центр банка. Ты агент контроля качества обслуживания.
Тебе дан транскрипт телефонного разговора между оператором и клиентом.

Определи:
1. greeting — здесь нужно определить насколько вежливое было общение, поздоровался ли оператор, общался ли вежливо и добропорядочно.
2. need_detection — выяснил ли оператор то, что необходимо клиенту, что он спрашивал, о чем просил.
3. solution_provided — предложил ли оператор клиенту решение, нашел ли способ решения его проблемы.
4. farewell — попрощался ли корректно.
5. total - пусть за каждый пункт начисляется по 25 баллов, в total вывести обще набранное количество баллов за разговор.

Ответь СТРОГО в формате JSON, без пояснений и без markdown-разметки:
пример одвета {
  "total": 78,
  "checklist": {
    "greeting": true,
    "need_detection": true,
    "solution_provided": true,
    "farewell": false
  }
}"""

def check_quality(segments):
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

'''if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    example = [
        {"speaker": "Оператор", "text": "Добрый день, МТБанк, меня зовут Анна, чем могу помочь?"},
        {"speaker": "Клиент", "text": "Здравствуйте. Хочу узнать про условия по вложений под проценты наличными и их вывод, вклады"},
    ]
    print(check_quality(example))'''
    
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

    print(check_quality(segments))


