"""
Все настраиваемые параметры системы в одном месте.

Каждое значение можно переопределить через переменную окружения (.env),
не трогая код — это то, что позволяет переносить проект между окружениями
(локально / сервер / другой LLM-провайдер) и переиспользовать под другие задачи.
"""

import os

# LLM (любой OpenAI-совместимый провайдер)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")

# ASR (faster-whisper)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "ru")

# Диаризация (pyannote.audio)
DIARIZATION_MODEL = os.getenv("DIARIZATION_MODEL", "pyannote/speaker-diarization-3.1")
