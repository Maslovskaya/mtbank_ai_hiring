def format_transcript(segments):
    """
    segments: список словарей {"start", "end", "text", "speaker"} (speaker уже
    "Оператор"/"Клиент", после assign_roles).

    Возвращает читаемый текст диалога вида:
    Оператор: Добрый день...
    Клиент: Здравствуйте...
    — то, что будем отправлять агентам как контекст разговора.
    """
    return "\n".join(f'{seg["speaker"]}: {seg["text"]}' for seg in segments)
