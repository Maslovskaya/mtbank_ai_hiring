import json
import os

from openai import OpenAI

from settings import LLM_BASE_URL, LLM_MODEL
from llm_json import parse_json_response

DEFAULT_MODEL = LLM_MODEL

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url=LLM_BASE_URL,
        )
    return _client


def call_llm_json(system_prompt, user_content, model=DEFAULT_MODEL, max_retries=2, validate=None):
    """
    Вызывает LLM с system+user сообщениями и разбирает ответ как JSON.

    Повторяет запрос (до max_retries раз), если:
    - ответ не разобрался как JSON (синтаксическая проблема), либо
    - ответ не прошёл проверку validate (смысловая проблема).

    validate: необязательная функция, принимает разобранный результат
    и возвращает True/False — годится ли такой ответ.
    """
    client = get_client()
    last_error = None

    for attempt in range(max_retries + 1):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )

        try:
            result = parse_json_response(response.choices[0].message.content)
        except json.JSONDecodeError as error:
            last_error = error
            continue

        if validate is not None and not validate(result):
            last_error = ValueError(f"Ответ LLM не прошёл проверку: {result}")
            continue

        return result

    raise last_error

