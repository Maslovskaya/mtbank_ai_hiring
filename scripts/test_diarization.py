import os
from dotenv import load_dotenv
from pyannote.audio import Pipeline

load_dotenv()

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.environ["HF_TOKEN"],
)

diarization = pipeline("test_data/Record2.mp3")

for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):
    print(f"[{turn.start:.2f}s -> {turn.end:.2f}s] {speaker}")
