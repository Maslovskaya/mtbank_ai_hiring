"""
JSON-логирование: одна строка вывода = одно событие в формате JSON.

Зачем именно JSON, а не обычный текст: такие логи легко читаются машинами —
их можно складывать в системы хранения логов (Grafana Loki, ELK, CloudWatch)
и потом искать/фильтровать по полям, например "покажи все вызовы агента
compliance, где обработка заняла больше 5 секунд".
"""

import json
import logging
import sys
import time

logger = logging.getLogger("mtbank")


class JsonFormatter(logging.Formatter):
    """Превращает запись лога в одну строку JSON."""

    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        # поля, переданные через logger.info(..., extra={"extra_fields": {...}})
        payload.update(getattr(record, "extra_fields", {}))
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level=logging.INFO):
    """Вызывается один раз при старте приложения."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.setLevel(level)
    logger.propagate = False  # не дублировать записи в корневой логгер


def log_event(event, **fields):
    """Записать произвольное событие с любыми дополнительными полями."""
    logger.info(event, extra={"extra_fields": fields})


def run_stage(name, stage_func, *args):
    """
    Выполняет этап конвейера (распознавание, диаризация...) и логирует,
    сколько времени он занял.

    Отличие от run_agent: у этапов не логируются вход и выход — транскрипт
    и аудио слишком объёмные, а польза в основном в тайминге.
    """
    started = time.time()
    result = stage_func(*args)

    log_event("stage_completed", stage=name, duration_sec=round(time.time() - started, 2))

    return result


def run_agent(name, agent_func, segments):
    """
    Вызывает агента и логирует его вход/выход + время работы.

    name: имя агента для логов, например "classifier"
    agent_func: сама функция агента (classify, check_quality, ...)
    segments: транскрипт, который уходит агенту на вход
    """
    started = time.time()
    result = agent_func(segments)
    duration = time.time() - started

    input_text = " ".join(seg["text"] for seg in segments)

    log_event(
        "agent_call",
        agent=name,
        input_segments=len(segments),
        # полный транскрипт может быть длинным — в лог пишем начало,
        # чтобы события оставались читаемыми
        input_preview=input_text[:300],
        output=result,
        duration_sec=round(duration, 2),
    )

    return result
