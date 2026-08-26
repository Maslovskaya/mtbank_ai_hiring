"""
title: Groq Test Pipeline
author: Ksenia
version: 0.1
requirements: openai
"""

import os
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
from openai import OpenAI


class Pipeline:
    class Valves(BaseModel):
        LLM_MODEL: str = "qwen/qwen3.8-27b"

    def __init__(self):
        self.name = "Groq Test"
        self.valves = self.Valves()
        self.client = None

    async def on_startup(self):
        self.client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )

    async def on_shutdown(self):
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        response = self.client.chat.completions.create(
            model=self.valves.LLM_MODEL,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.choices[0].message.content
