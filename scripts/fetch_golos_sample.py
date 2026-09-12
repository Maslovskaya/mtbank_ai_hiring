"""
Собирает тестовый файл из открытого датасета Golos (SberDevices).

Зачем это нужно: остальные записи в test_data/ либо синтезированы нами,
либо начитаны вручную — в обоих случаях эталонный транскрипт составляли мы
сами. Здесь эталон берётся от авторов датасета, то есть WER считается
относительно полностью независимой разметки.

Датасет целиком весит гигабайты, поэтому качаем не его, а отдельные строки
через API Hugging Face (datasets-server) — это несколько мегабайт.

Запуск:  python -m scripts.fetch_golos_sample
"""

import io

import requests
from pydub import AudioSegment

DATASET = "bond005/sberdevices_golos_10h_crowd"
ROWS_API = "https://datasets-server.huggingface.co/rows"

SAMPLE_COUNT = 20  # хватает примерно на минуту речи
PAUSE_MS = 400  # пауза между фразами, чтобы Whisper их не склеивал

OUTPUT_AUDIO = "test_data/golos_open_dataset.wav"
OUTPUT_REFERENCE = "test_data/golos_open_dataset.txt"


def fetch_rows(count):
    """Забирает строки датасета: ссылку на аудио и эталонный текст."""
    response = requests.get(
        ROWS_API,
        params={
            "dataset": DATASET,
            "config": "default",
            "split": "test",
            "offset": 0,
            "length": count,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["rows"]


def download_audio(url):
    """Скачивает один аудиофрагмент в память (без сохранения на диск)."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return AudioSegment.from_file(io.BytesIO(response.content))


def main():
    print(f"Запрашиваю {SAMPLE_COUNT} фрагментов из {DATASET}...")
    rows = fetch_rows(SAMPLE_COUNT)

    combined = AudioSegment.silent(duration=200)
    pause = AudioSegment.silent(duration=PAUSE_MS)
    transcriptions = []

    for index, row in enumerate(rows, start=1):
        data = row["row"]
        text = data["transcription"].strip()
        url = data["audio"][0]["src"]

        print(f"[{index}/{len(rows)}] {text[:50]}")
        combined += download_audio(url) + pause
        transcriptions.append(text)

    combined.export(OUTPUT_AUDIO, format="wav")

    # эталон — склейка транскриптов в том же порядке, что и аудио
    with open(OUTPUT_REFERENCE, "w", encoding="utf-8") as file:
        file.write(" ".join(transcriptions))

    print(f"\nГотово: {OUTPUT_AUDIO}")
    print(f"Длительность: {len(combined) / 1000:.1f} сек")
    print(f"Эталон: {OUTPUT_REFERENCE} ({len(' '.join(transcriptions).split())} слов)")


if __name__ == "__main__":
    main()
