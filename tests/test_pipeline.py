from pipeline import analyze


def test_analyze_full_pipeline():
    result = analyze("test_data/record1.mp3")

    assert "transcript" in result
    assert "classification" in result
    assert "quality_score" in result
    assert "compliance" in result
    assert "summary" in result
    assert "action_items" in result
    assert len(result["transcript"]) > 0
