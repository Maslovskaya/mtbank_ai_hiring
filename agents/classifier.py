from agents.llm_client import call_llm_json
from agents.utils import format_transcript

SYSTEM_PROMPT = """Ты — агент-классификатор обращений в контакт-центр банка.
Тебе дан транскрипт телефонного разговора между оператором и клиентом.

Определи:
1. topic — тема обращения, ОБЯЗАТЕЛЬНО одно из значений:
   "кредиты", "карты", "переводы", "жалобы", "другое"
2. priority — приоритет обработки обращения, одно из: "low", "medium", "high"
   Ориентируйся так: жалобы, срочные проблемы, потеря карты — high;
   обычные вопросы по продуктам — medium; простые информационные запросы — low.

Ответь СТРОГО в формате JSON, без пояснений и без markdown-разметки:
{"topic": "...", "priority": "..."}"""


def classify(segments):
    """
    segments: список словарей {"start", "end", "text", "speaker"} — транскрипт с ролями.
    Возвращает {"topic": "...", "priority": "..."}
    """
    transcript_text = format_transcript(segments)
    return call_llm_json(SYSTEM_PROMPT, transcript_text)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    example = [
        {"speaker": "Оператор", "text": "Добрый день, МТБанк, меня зовут Анна, чем могу помочь?"},
        {"speaker": "Клиент", "text": "Здравствуйте. Хочу узнать про условия по кредиту наличными."},
    ]
    print(classify(example))
