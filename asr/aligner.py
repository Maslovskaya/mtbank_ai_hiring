def assign_speakers(asr_segments, diarization_segments):
    """
    asr_segments: список словарей {"start": float, "end": float, "text": str}
    diarization_segments: список словарей {"start": float, "end": float, "speaker": str}

    Возвращает список словарей {"start", "end", "text", "speaker"} —
    каждому сегменту текста присвоен спикер с наибольшим пересечением по времени.
    """
    result = []
    for asr_seg in asr_segments:
        best_speaker = None
        best_overlap = 0.0

        for dia_seg in diarization_segments:
            overlap_start = max(asr_seg["start"], dia_seg["start"])
            overlap_end = min(asr_seg["end"], dia_seg["end"])
            overlap = max(0.0, overlap_end - overlap_start)

            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = dia_seg["speaker"]

        result.append({
            "start": asr_seg["start"],
            "end": asr_seg["end"],
            "text": asr_seg["text"],
            "speaker": best_speaker,
        })

    return result
