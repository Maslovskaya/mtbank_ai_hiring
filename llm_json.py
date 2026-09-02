import json
import re


def parse_json_response(content):
    """
    Достаёт JSON-объект из ответа LLM, даже если модель обернула его
    в markdown (```json ... ```) или добавила лишний текст вокруг.
    Ищет первую { и последнюю } в ответе и парсит то, что между ними.
    """
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        content = match.group(0)
    return json.loads(content)
