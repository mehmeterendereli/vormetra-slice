"""Local HTTP control API for VORMETRA Slice -- stdlib only (no FastAPI/
uvicorn dependency, matching the rest of this repo's tooling conventions).

Endpoints (all JSON in/out unless noted):
  GET  /health              -> {"ok": bool, "slicer_bin": str, "exists": bool}
  GET  /profiles            -> {"filaments": [...], "machine": "..."}
  POST /validate            -> {"stl_path": "..."} => bounding-box fit check
  POST /slice                -> {"stl_path": "...", "filament": "petg"} => stats + gcode_3mf_path
  GET  /                     -> Vera Console (static HTML/JS)

This is the layer any AI agent (Claude Code, another LLM, or the embedded
Vera chat panel once it exists in the GUI) can drive over plain HTTP. See
mcp_server.py for the same capabilities exposed as native MCP tools.
"""
from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import config, slicer_bridge

CONSOLE_DIR = Path(__file__).parent / "console"


class VeraRequestHandler(BaseHTTPRequestHandler):
    server_version = "VeraControl/0.1"

    def log_message(self, fmt, *args):  # quieter default logging
        pass

    # -- helpers -----------------------------------------------------
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _serve_static(self, rel_path: str) -> None:
        rel_path = rel_path.lstrip("/") or "index.html"
        file_path = (CONSOLE_DIR / rel_path).resolve()
        if CONSOLE_DIR.resolve() not in file_path.parents and file_path != CONSOLE_DIR.resolve():
            self.send_error(403)
            return
        if not file_path.exists():
            self.send_error(404)
            return
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # -- routing -------------------------------------------------------
    def do_OPTIONS(self) -> None:  # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json({
                "ok": config.SLICER_BIN.exists(),
                "slicer_bin": str(config.SLICER_BIN),
                "exists": config.SLICER_BIN.exists(),
                "slice_running": slicer_bridge.is_slice_running(),
                "service": "vera-control",
                "version": "0.1.0",
            })
        elif self.path == "/profiles":
            self._send_json({
                "machine": "VORMETRA G1000 (5.0mm nozzle)",
                "filaments": slicer_bridge.list_filaments(),
                "build_volume_mm": config.MACHINE_LIMITS,
            })
        else:
            self._serve_static(self.path)

    def do_POST(self) -> None:
        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "invalid JSON body"}, status=400)
            return

        if self.path == "/validate":
            self._handle_validate(body)
        elif self.path == "/slice":
            self._handle_slice(body)
        else:
            self._send_json({"error": f"unknown endpoint {self.path}"}, status=404)

    def _handle_validate(self, body: dict) -> None:
        stl_path = body.get("stl_path")
        if not stl_path:
            self._send_json({"error": "stl_path required"}, status=400)
            return
        try:
            result = slicer_bridge.validate_model(stl_path)
        except (OSError, ValueError) as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        self._send_json(result)

    def _handle_slice(self, body: dict) -> None:
        stl_path = body.get("stl_path")
        filament = body.get("filament", "petg")
        if not stl_path:
            self._send_json({"error": "stl_path required"}, status=400)
            return
        try:
            result = slicer_bridge.slice_model(stl_path, filament=filament)
        except slicer_bridge.VeraSlicerBusy as exc:
            self._send_json({"error": str(exc)}, status=409)
            return
        except slicer_bridge.VeraSlicerError as exc:
            self._send_json({"error": str(exc)}, status=422)
            return
        self._send_json({
            "gcode_3mf_path": str(result.gcode_3mf_path),
            "stats": result.stats,
            "gcode_preview": "\n".join(result.gcode_text.splitlines()[:20]),
        })


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    httpd = ThreadingHTTPServer((host, port), VeraRequestHandler)
    print(f"Vera Control API listening on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve()
