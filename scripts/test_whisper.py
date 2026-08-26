import sys
from faster_whisper import WhisperModel

audio_path = sys.argv[1] if len(sys.argv) > 1 else "test_data/Record1.mp3"

model = WhisperModel("medium", device="cpu", compute_type="int8")

segments, info = model.transcribe(audio_path, language="ru")

print(f"Detected language: {info.language} (probability {info.language_probability:.2f})")
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
