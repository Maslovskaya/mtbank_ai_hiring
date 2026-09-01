import os

from openai import OpenAI

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
