import json
import os

from openai import OpenAI

from llm_json import parse_json_response

DEFAULT_MODEL = "qwen/qwen3.8-27b"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )
    return _client


def call_llm_json(system_prompt, user_content, model=DEFAULT_MODEL, max_retries=2):
    """
    Вызывает LLM с system+user сообщениями и разбирает ответ как JSON.
    Если модель вернула невалидный JSON — пробует ещё раз (до max_retries раз):
    это обычно случайная опечатка модели в формате, а не системная проблема,
    повторный запрос почти всегда проходит.
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
            return parse_json_response(response.choices[0].message.content)
        except json.JSONDecodeError as error:
            last_error = error

    raise last_error
