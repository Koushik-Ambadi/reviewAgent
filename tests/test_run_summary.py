import json

from code_intelligence.run_summary import build_run_summary


def test_analysis_summary_keeps_flow_status_and_review_signals_separate(tmp_path):
    analysis = tmp_path / "analysis"
    (analysis / "flow").mkdir(parents=True)
    (analysis / "code-intelligence.json").write_text(json.dumps({
        "nodes": [{"id":"f","name":"calculate","kind":"function","attributes":{"complexity":8}}],
        "edges": []}))
    (analysis / "flow/summary.json").write_text(json.dumps({
        "status":"partial","sources":[{"status":"completed"},{"status":"failed"}]}))
    result = build_run_summary(analysis)
    assert result["flow_status"] == "partial"
    assert (result["flow_completed_sources"],result["flow_failed_sources"]) == (1,1)
    assert result["top_functions"][0]["name"] == "calculate"
    assert "not defects" in result["boundary"]
