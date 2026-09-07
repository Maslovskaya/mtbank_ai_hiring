"""
REST API и веб-интерфейс системы.

Два способа обратиться к анализу звонка:
  GET  /         — веб-страница с загрузкой аудио
  POST /analyze  — программный доступ: загрузка файла или ссылка на аудио

Оба используют одну и ту же функцию pipeline.analyze().
"""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from audio_input import download_audio, temporary_audio_file
from logger import setup_logging
from pipeline import analyze

load_dotenv()
setup_logging()

app = FastAPI(
    title="MTBank Call Analytics",
    description="Транскрибация, диаризация и multi-agent анализ звонков контакт-центра",
)

INDEX_PAGE = Path(__file__).resolve().parent.parent / "web" / "index.html"


@app.get("/", include_in_schema=False)
def index():
    """Отдаёт страницу веб-интерфейса."""
    return FileResponse(INDEX_PAGE)


@app.get("/health")
def health():
    """Проверка живости сервиса — используется мониторингом и при деплое."""
    return {"status": "ok", "service": "mtbank-call-analytics"}


@app.post("/analyze")
async def analyze_endpoint(
    file: UploadFile = File(None, description="Аудиофайл: WAV, MP3 или OGG"),
    url: str = Form(None, description="Ссылка на аудиофайл (альтернатива загрузке)"),
):
    """
    Анализирует запись звонка и возвращает транскрипт с разметкой по говорящим,
    классификацию, оценку качества, результат compliance-проверки и резюме.

    Нужно передать ровно один источник аудио: либо файл, либо ссылку.
    """
    if file is None and url is None:
        raise HTTPException(status_code=400, detail="Передайте аудиофайл или ссылку на него")

    if file is not None:
        content = await file.read()
        suffix = Path(file.filename or "").suffix or ".wav"
    else:
        try:
            content, suffix = download_audio(url)
        except Exception as error:
            raise HTTPException(status_code=400, detail=f"Не удалось скачать аудио: {error}")

    with temporary_audio_file(content, suffix) as path:
        return analyze(path)
