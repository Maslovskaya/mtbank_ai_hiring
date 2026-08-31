"""
Синтезирует test_data/dialog_full.wav — полный диалог оператор/клиент
из docs/sample-dialog.md — двумя разными голосами через edge-tts,
плюс test_data/dialog_full.txt — точный эталонный транскрипт (для WER).
"""

import asyncio
from pathlib import Path

import edge_tts
from pydub import AudioSegment

TEST_DATA = Path("test_data")

VOICES = {
    "Оператор": "ru-RU-SvetlanaNeural",
    "Клиент": "ru-RU-DmitryNeural",
}

DIALOGUE = [
    ("Оператор", "Добрый день, МТБанк, меня зовут Анна, чем могу помочь?"),
    ("Клиент", "Здравствуйте. Хочу узнать про условия по кредиту наличными."),
    ("Оператор", "Конечно, подскажите, пожалуйста, какая сумма вас интересует и на какой срок?"),
    ("Клиент", "Примерно десять тысяч рублей, на год."),
    ("Оператор", "Отлично. На данный момент ставка от четырнадцати и девяти процентов годовых, решение за пятнадцать минут. Вы уже являетесь клиентом МТБанка?"),
    ("Клиент", "Да, у меня есть карточка ваша."),
    ("Оператор", "Прекрасно, тогда для вас действуют специальные условия. Ежемесячный платёж составит около девятисот рублей. Вам удобно подать заявку онлайн через приложение или предпочитаете приехать в отделение?"),
    ("Клиент", "Лучше онлайн. Но у меня вопрос — если я захочу досрочно погасить, есть штрафы?"),
    ("Оператор", "Нет, досрочное погашение без штрафов и комиссий, в любое время и в любом объёме."),
    ("Клиент", "Хорошо, а страховка обязательна?"),
    ("Оператор", "Страхование жизни подключается по вашему желанию, это не обязательное условие получения кредита. Однако при подключении страховки ставка может быть немного снижена."),
    ("Клиент", "Понятно. Тогда я попробую подать через приложение."),
    ("Оператор", "Отлично. Если возникнут вопросы в процессе заполнения — звоните, мы поможем. Также могу отправить вам краткую инструкцию на email, если хотите."),
    ("Клиент", "Да, пожалуйста, отправьте."),
    ("Оператор", "Хорошо, подскажите ваш email."),
    ("Клиент", "Михаил-собака-пример-точка-бай."),
    ("Оператор", "Записала. В течение нескольких минут получите письмо с инструкцией и ссылкой на заявку. Есть ещё вопросы?"),
    ("Клиент", "Нет, всё понятно, спасибо."),
    ("Оператор", "Спасибо за обращение в МТБанк, хорошего дня!"),
    ("Клиент", "И вам, до свидания."),
]


async def synth_line(text, voice, out_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out_path))


async def main():
    tmp_dir = TEST_DATA / "_tmp_lines"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    pause = AudioSegment.silent(duration=500)  # 0.5 сек тишины между репликами
    combined = AudioSegment.silent(duration=300)

    for i, (speaker, text) in enumerate(DIALOGUE):
        print(f"[{i + 1}/{len(DIALOGUE)}] {speaker}: {text[:40]}...")
        line_path = tmp_dir / f"{i:02d}_{speaker}.mp3"
        await synth_line(text, VOICES[speaker], line_path)
        clip = AudioSegment.from_file(line_path)
        combined += clip + pause

    out_audio = TEST_DATA / "dialog_full.wav"
    combined.export(out_audio, format="wav")

    reference_lines = [f"{speaker}: {text}" for speaker, text in DIALOGUE]
    (TEST_DATA / "dialog_full.txt").write_text("\n".join(reference_lines), encoding="utf-8")

    for f in tmp_dir.glob("*.mp3"):
        f.unlink()
    tmp_dir.rmdir()

    print(f"\nГотово: {out_audio} + dialog_full.txt")
    print(f"Длительность: {len(combined) / 1000:.1f} сек")


if __name__ == "__main__":
    asyncio.run(main())
