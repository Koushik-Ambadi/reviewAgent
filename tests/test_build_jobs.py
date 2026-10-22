from concurrent.futures import ThreadPoolExecutor
import json

from orchestrator import build_jobs


def test_progress_updates_are_serialized_per_run(tmp_path, monkeypatch):
    run_id = "concurrent-progress"
    run_path = tmp_path / run_id
    run_path.mkdir()
    progress_path = run_path / "build-progress.json"
    progress_path.write_text(
        json.dumps({"run_id": run_id, "state": "running", "stdout": [], "stderr": []}),
        encoding="utf-8",
    )
    monkeypatch.setattr(build_jobs, "get_run_path", lambda _: run_path)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda index: build_jobs._append_output(run_id, "stdout", f"line-{index}"), range(80)))

    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    assert progress["state"] == "running"
    assert len(progress["stdout"]) == 80
    assert set(progress["stdout"]) == {f"line-{index}" for index in range(80)}
