from asr.aligner import assign_speakers


def test_assign_speakers_picks_max_overlap():
    asr_segments = [
        {"start": 4.0, "end": 11.0, "text": "Я клиент вашего банка."},
    ]
    diarization_segments = [
        {"start": 1.48, "end": 2.12, "speaker": "SPEAKER_00"},
        {"start": 2.66, "end": 3.83, "speaker": "SPEAKER_01"},
        {"start": 4.37, "end": 11.07, "speaker": "SPEAKER_00"},
        {"start": 11.59, "end": 16.05, "speaker": "SPEAKER_01"},
    ]

    result = assign_speakers(asr_segments, diarization_segments)

    assert result[0]["speaker"] == "SPEAKER_00"
    assert result[0]["text"] == "Я клиент вашего банка."


def test_assign_speakers_no_overlap_gives_none():
    asr_segments = [{"start": 100.0, "end": 105.0, "text": "далеко от всех"}]
    diarization_segments = [{"start": 0.0, "end": 1.0, "speaker": "SPEAKER_00"}]

    result = assign_speakers(asr_segments, diarization_segments)

    assert result[0]["speaker"] is None
