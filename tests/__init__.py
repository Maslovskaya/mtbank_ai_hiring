from unittest.mock import patch

from agents.classifier import classify

SAMPLE_SEGMENTS = [
    {"start": 0.0, "end": 2.0, "speaker": "Оператор", "text": "Добрый день!"},
    {"start": 2.0, "end": 4.0, "speaker": "Клиент", "text": "Хочу узнать про кредит."},
]


@patch("agents.classifier.call_llm_json")
def test_classify(mock_call):
    mock_call.return_value = {"topic": "кредиты", "priority": "medium"}

    result = classify(SAMPLE_SEGMENTS)

    assert result["topic"] == "кредиты"
    assert result["priority"] == "medium"
    mock_call.assert_called_once()
