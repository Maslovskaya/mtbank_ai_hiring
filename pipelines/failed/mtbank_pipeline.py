"""
title: MTBank Call Analytics
author: Ksenia Maslovskaya
version: 1.0
requirements: openai, faster-whisper, pyannote.audio, python-dotenv, requests

OpenWebUI Pipeline: пользователь присылает в чат ссылку на аудиозапись звонка,
пайплайн скачивает её, прогоняет через pipeline.analyze() и возвращает разбор
в виде markdown.

Почему ссылка, а не вложение: доступ к файлам, прикреплённым в чате, на стороне
OpenWebUI Pipelines на момент разработки не имеет стабильного API (см. открытые
обсуждения в репозитории open-webui). Загрузка файлом при этом доступна через
REST API POST /analyze и через веб-интерфейс.
"""

import re

from pydantic import BaseModel

from audio_input import download_audio, temporary_audio_file
from pipeline import analyze

URL_PATTERN = re.compile(r"https?://\S+")

CHECKLIST_LABELS = {
    "greeting": "Приветствие",
    "need_detection": "Выявление потребности",
    "solution_provided": "Решение предложено",
    "farewell": "Прощание",
}

USAGE_HINT = (
    "Пришлите ссылку (URL) на аудиофайл звонка — я скачаю его и проанализирую.\n\n"
    "Загрузить файл напрямую можно через веб-интерфейс или REST API "
    "`POST /analyze` (multipart/form-data)."
)


class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.name = "MTBank Call Analytics"

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass

    def pipe(self, user_message: str, model_id: str, messages: list, body: dict):
        url_match = URL_PATTERN.search(user_message)
        if not url_match:
            return USAGE_HINT

        try:
            content, suffix = download_audio(url_match.group(0))
        except Exception as error:
            return f"⚠️ Не удалось скачать файл по ссылке: {error}"

        try:
            with temporary_audio_file(content, suffix) as path:
                result = analyze(path)
        except Exception as error:
            return f"⚠️ Ошибка при анализе звонка: {error}"

        return format_markdown(result)


def format_markdown(result):
    """Превращает JSON-результат анализа в читаемый markdown для чата."""
    lines = ["### 📋 Анализ звонка", ""]

    classification = result["classification"]
    lines.append(f"**Тема:** {classification['topic']} | **Приоритет:** {classification['priority']}")
    lines.append(f"**Оценка качества:** {result['quality_score']['total']}/100")

    checklist = result["quality_score"]["checklist"]
    for key, label in CHECKLIST_LABELS.items():
        lines.append(f"- {'✅' if checklist[key] else '❌'} {label}")

    compliance = result["compliance"]
    lines.append("")
    lines.append(f"**Compliance:** {'✅ Без нарушений' if compliance['passed'] else '⚠️ Есть нарушения'}")
    lines.extend(f"- {issue}" for issue in compliance["issues"])

    lines.append("")
    lines.append(f"**Резюме:** {result['summary']}")

    if result["action_items"]:
        lines.append("")
        lines.append("**Что сделать после звонка:**")
        lines.extend(f"- {item}" for item in result["action_items"])

    lines.append("")
    lines.append("**Транскрипт:**")
    for segment in result["transcript"]:
        timing = f"{segment['start']:.1f}–{segment['end']:.1f}"
        lines.append(f"- `[{timing}]` **{segment['speaker']}:** {segment['text']}")

    return "\n".join(lines)
