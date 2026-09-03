import os
import tempfile

from fastapi import FastAPI, UploadFile, File

from pipeline import analyze

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok", "service": "mtbank-ai-hiring"}


@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]  # например ".mp3"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    result = analyze(tmp_path)
    os.remove(tmp_path)
    return result
