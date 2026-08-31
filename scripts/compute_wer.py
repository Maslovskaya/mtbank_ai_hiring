"""
Считает WER (Word Error Rate) для каждой пары аудио/эталон в test_data/.
Ожидает файлы вида record1.mp3 + record1.txt (одинаковое имя, разное расширение).
Для эталонов с метками спикера ("Оператор: ...", "Клиент: ...") метки перед
сравнением убираются — иначе WER считал бы саму метку как ошибку распознавания.
"""

import re
from pathlib import Path

import jiwer

from asr.transcriber import transcribe

TEST_DATA = Path("test_data")
AUDIO_EXTENSIONS = (".wav", ".mp3", ".ogg")
LABEL_PATTERN = re.compile(r"^(Оператор|Клиент):\s*")

NORMALIZE = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.RemovePunctuation(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
    jiwer.ReduceToListOfListOfWords(),
])

def clean_reference(text):
    lines = text.strip().splitlines()
    cleaned = [LABEL_PATTERN.sub("", line) for line in lines]
    return " ".join(cleaned)


def find_audio(ref_path):
    for ext in AUDIO_EXTENSIONS:
        candidate = ref_path.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


def main():
    results = []

    for ref_path in sorted(TEST_DATA.glob("*.txt")):
        audio_path = find_audio(ref_path)
        if audio_path is None:
            print(f"Пропускаю {ref_path.name} — не нашла аудио с таким же именем")
            continue

        reference = clean_reference(ref_path.read_text(encoding="utf-8"))

        print(f"Распознаю {audio_path.name}...")
        segments = transcribe(str(audio_path))
        hypothesis = " ".join(seg["text"] for seg in segments)

        error = jiwer.wer(
            reference,
            hypothesis,
            reference_transform=NORMALIZE,
            hypothesis_transform=NORMALIZE,
        )
        results.append((audio_path.name, error))

    print("\n| Файл | WER |")
    print("|---|---|")
    for name, error in results:
        print(f"| {name} | {error:.2%} |")


if __name__ == "__main__":
    main()
