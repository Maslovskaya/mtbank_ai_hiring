"""
Приём аудио из разных источников: загруженный файл или ссылка.

Whisper и pyannote работают с путём к файлу на диске, а к нам аудио приходит
либо байтами (загрузка через форму), либо по URL. Этот модуль сводит оба
случая к одному: «дай мне путь к временному файлу и убери его за собой».
"""

import os
import tempfile
from contextlib import contextmanager

import requests

DOWNLOAD_TIMEOUT_SEC = 60


def download_audio(url):
    """
    Скачивает аудио по ссылке.
    Возвращает пару (содержимое файла в байтах, расширение вида ".mp3").
    """
    response = requests.get(url, timeout=DOWNLOAD_TIMEOUT_SEC)
    response.raise_for_status()

    # ссылка может быть с параметрами (?token=...) — отрезаем их перед
    # определением расширения, иначе получим мусор вместо ".mp3"
    path_without_query = url.split("?")[0]
    suffix = os.path.splitext(path_without_query)[1] or ".wav"

    return response.content, suffix


@contextmanager
def temporary_audio_file(content, suffix):
    """
    Кладёт байты во временный файл и гарантированно удаляет его после работы.

    Используется как:
        with temporary_audio_file(content, ".mp3") as path:
            analyze(path)

    Блок finally срабатывает даже если внутри произошла ошибка — файл
    не останется мусором на диске.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        path = tmp.name

    try:
        yield path
    finally:
        os.remove(path)
