"""
title: MTBank Call Analytics
author: Ksenia
version: 1.0
requirements: openai, faster-whisper, pyannote.audio, python-dotenv, requests
"""

import os
import re
import tempfile

import requests
from pydantic import BaseModel

from pipeline import analyze


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
        url_match = re.search(r"https?://\S+", user_message)

        if not url_match:
            return (
                "Пришлите ссылку (URL) на аудиофайл звонка в сообщении — я скачаю "
                "его и проанализирую.\n\n"
                "Также доступен REST API: `POST /analyze` (multipart/form-data) "
                "для прямой загрузки файла без чата."
            )

        audio_url = url_match.group(0)

        try:
            response = requests.get(audio_url, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            return f"⚠️ Не удалось скачать файл по ссылке: {error}"

        suffix = os.path.splitext(audio_url.split("?")[0])[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        try:
            result = analyze(tmp_path)
        except Exception as error:
            return f"⚠️ Ошибка при анализе звонка: {error}"
        finally:
            os.remove(tmp_path)

        return self._format_markdown(result)

    def _format_markdown(self, result):
        checklist = result["quality_score"]["checklist"]
        checklist_labels = {
            "greeting": "Приветствие",
            "need_detection": "Выявление потребности",
            "solution_provided": "Решение предложено",
            "farewell": "Прощание",
        }

        lines = ["### 📋 Анализ звонка", ""]
        lines.append(
            f"**Тема:** {result['classification']['topic']} | "
            f"**Приоритет:** {result['classification']['priority']}"
        )
        lines.append(f"**Оценка качества:** {result['quality_score']['total']}/100")
        for key, label in checklist_labels.items():
            mark = "✅" if checklist[key] else "❌"
            lines.append(f"- {mark} {label}")

        lines.append("")
        compliance = result["compliance"]
        status = "✅ Без нарушений" if compliance["passed"] else "⚠️ Есть нарушения"
        lines.append(f"**Compliance:** {status}")
        for issue in compliance["issues"]:
            lines.append(f"- {issue}")

        lines.append("")
        lines.append(f"**Резюме:** {result['summary']}")
        lines.append("")
        lines.append("**Action items:**")
        for item in result["action_items"]:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("**Транскрипт:**")
        for seg in result["transcript"]:
            lines.append(f"- `[{seg['start']:.1f}-{seg['end']:.1f}]` **{seg['speaker']}:** {seg['text']}")

        return "\n".join(lines)
