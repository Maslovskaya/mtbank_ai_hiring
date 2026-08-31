import json

from dotenv import load_dotenv

from asr.aligner import assign_speakers
from asr.diarizer import diarize
from asr.roles import assign_roles
from asr.transcriber import transcribe

load_dotenv()

AUDIO = "test_data/Record3.mp3"

print("Транскрибирую...")
asr_segments = transcribe(AUDIO)

print("Диаризую...")
diarization_segments = diarize(AUDIO)

result = assign_speakers(asr_segments, diarization_segments)
result = assign_roles(result)

print(json.dumps(result, ensure_ascii=False, indent=2))
