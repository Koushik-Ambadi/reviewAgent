# serve.py

from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "index.html"
DEFAULT_CONFIG = ROOT / "config" / "review_pipeline.yaml"
LATEST_REPORT = ROOT / "review_report.json"

SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(SRC_DIR))

from repo_review.pipeline import build_review_report
from repo_review.reporter import write_report


def _json_response(handler: BaseHTTPRequestHandler, payload: object, status: int = 200) -> None:
    data = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _text_response(handler: BaseHTTPRequestHandler, content: bytes, content_type: str = "text/plain; charset=utf-8", status: int = 200) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(content)))
    handler.end_headers()
    handler.wfile.write(content)


def _serve_file(handler: BaseHTTPRequestHandler, path: Path) -> None:
    if not path.exists():
        _text_response(handler, b"Not found", status=HTTPStatus.NOT_FOUND)
        return

    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    _text_response(handler, path.read_bytes(), content_type=content_type)


class ReviewHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            return _serve_file(self, INDEX_FILE)
        if path == "/api/latest-report":
            if LATEST_REPORT.exists():
                return _serve_file(self, LATEST_REPORT)
            return _json_response(self, {"error": "No report generated yet."}, status=404)
        if path.startswith("/api/"):
            return _json_response(self, {"error": "Unknown endpoint."}, status=404)

        candidate = (ROOT / path.lstrip("/")).resolve()
        if ROOT in candidate.parents or candidate == ROOT:
            return _serve_file(self, candidate)
        return _json_response(self, {"error": "Forbidden."}, status=403)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/run":
            return _json_response(self, {"error": "Unknown endpoint."}, status=404)

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return _json_response(self, {"error": "Invalid JSON body."}, status=400)

        repo_url = body.get("repo_url", "")
        module_name = body.get("module_name", "")
        source_path = body.get("source_path", "soc")
        config_path = body.get("config_path") or DEFAULT_CONFIG
        if not repo_url or not module_name:
            return _json_response(self, {"error": "repo_url and module_name are required."}, status=400)

        pipeline_config_path = Path(config_path)
        if not pipeline_config_path.is_absolute():
            pipeline_config_path = (ROOT / pipeline_config_path).resolve()

        report = build_review_report(
            source_path=ROOT / source_path,
            module_name=module_name,
            repo_url=repo_url,
            pipeline_config_path=pipeline_config_path,
        )

        output_path = write_report(report, report["metadata"]["report_output_path"])
        report["metadata"]["report_output_path"] = str(output_path)
        return _json_response(self, report)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ReviewHandler)
    print("Serving on http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
