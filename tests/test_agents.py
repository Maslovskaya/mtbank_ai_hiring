from unittest.mock import patch

from agents.classifier import classify
from agents.quality import check_quality
from agents.compliance import check_compliance, find_forbidden_phrases
from agents.summarizer import summarize

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


@patch("agents.quality.call_llm_json")
def test_check_quality(mock_call):
    mock_call.return_value = {
        "total": 100,
        "checklist": {
            "greeting": True,
            "need_detection": True,
            "solution_provided": True,
            "farewell": True,
        },
    }

    result = check_quality(SAMPLE_SEGMENTS)

    assert result["total"] == 100
    assert result["checklist"]["greeting"] is True
    mock_call.assert_called_once()


@patch("agents.compliance.call_llm_json")
def test_check_compliance_clean(mock_call):
    mock_call.return_value = {"issues": []}

    result = check_compliance(SAMPLE_SEGMENTS)

    assert result["passed"] is True
    assert result["issues"] == []
    mock_call.assert_called_once()


@patch("agents.compliance.call_llm_json")
def test_check_compliance_finds_forbidden_phrase(mock_call):
    mock_call.return_value = {"issues": []}
    bad_segments = [
        {"start": 0.0, "end": 2.0, "speaker": "Оператор", "text": "Мы гарантированно одобрим вам кредит."},
    ]

    result = check_compliance(bad_segments)

    assert result["passed"] is False
    assert "гарантированно одобрим" in result["issues"]


def test_find_forbidden_phrases_detects():
    text = "мы гарантированно одобрим вам кредит без документов"
    found = find_forbidden_phrases(text)

    assert "гарантированно одобрим" in found
    assert "без документов" in found


def test_find_forbidden_phrases_clean():
    text = "спасибо за обращение, хорошего дня"
    assert find_forbidden_phrases(text) == []


@patch("agents.summarizer.call_llm_json")
def test_summarize(mock_call):
    mock_call.return_value = {
        "summary": "Клиент спросил про кредит, оператор поприветствовал.",
        "action_items": ["Перезвонить клиенту завтра"],
    }

    result = summarize(SAMPLE_SEGMENTS)

    assert "кредит" in result["summary"]
    assert result["action_items"] == ["Перезвонить клиенту завтра"]
    mock_call.assert_called_once()
