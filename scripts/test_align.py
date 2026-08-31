import json
import os

from dotenv import load_dotenv
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline

from asr.aligner import assign_speakers
from asr.roles import assign_roles


load_dotenv()

AUDIO = "test_data/Record2.mp3"

print("Транскрибирую...")
whisper_model = WhisperModel("medium", device="cpu", compute_type="int8")
segments, _ = whisper_model.transcribe(AUDIO, language="ru")
asr_segments = [
    {"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments
]

print("Диаризую...")
dia_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.environ["HF_TOKEN"],
)
diarization = dia_pipeline(AUDIO)
diarization_segments = [
    {"start": turn.start, "end": turn.end, "speaker": speaker}
    for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True)
]

result = assign_speakers(asr_segments, diarization_segments)
result = assign_roles(result)

print(json.dumps(result, ensure_ascii=False, indent=2))
