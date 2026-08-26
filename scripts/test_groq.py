import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # читает .env и кладёт переменные в os.environ

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",  # ключевая строка: шлём запросы не в OpenAI, а в Groq
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Привет! Ответь одним словом: работаешь?"}],
)

print(response.choices[0].message.content)
