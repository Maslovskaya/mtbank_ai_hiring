# Образ основного сервиса: REST API + веб-интерфейс + ASR + агенты.
#
# Python 3.11 (а не 3.13) выбран намеренно: часть ML-библиотек ещё не полностью
# поддерживает 3.13 — например, pydub требует модуль audioop, убранный из
# стандартной библиотеки в 3.13.
FROM python:3.11-slim

# ffmpeg нужен faster-whisper и pyannote, чтобы читать аудиофайлы.
# rm -rf /var/lib/apt/lists/* в конце — чистим кэш пакетов, иначе он
# остаётся внутри образа и раздувает его на сотни мегабайт.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Зависимости копируем и ставим ДО кода — это важно для скорости пересборки.
# Docker кэширует каждый шаг: пока requirements.txt не менялся, тяжёлая
# установка torch/whisper берётся из кэша, даже если код правился сто раз.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# --host 0.0.0.0 обязателен: по умолчанию uvicorn слушает только localhost
# внутри контейнера, и снаружи до него не достучаться.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
