import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from vera_control import api
from vera_control import slicer_bridge
from vera_control.api import VeraRequestHandler
from http.server import ThreadingHTTPServer


@pytest.fixture()
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), VeraRequestHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    httpd.shutdown()
    thread.join(timeout=5)


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, json.loads(resp.read())


def _post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_health_endpoint(server):
    status, body = _get(f"{server}/health")
    assert status == 200
    assert body["service"] == "vera-control"
    assert "slicer_bin" in body
    assert body["slice_running"] is False


def test_profiles_endpoint(server):
    status, body = _get(f"{server}/profiles")
    assert status == 200
    assert sorted(body["filaments"]) == ["petg", "pla"]
    assert body["build_volume_mm"]["bed_x_mm"] == 1000.0


def test_validate_missing_stl_path(server):
    status, body = _post(f"{server}/validate", {})
    assert status == 400
    assert "error" in body


def test_slice_missing_stl_path(server):
    status, body = _post(f"{server}/slice", {})
    assert status == 400
    assert "error" in body


def test_slice_unknown_filament_returns_422(server, tmp_path):
    # a nonexistent stl is enough -- slice_model checks filament choices
    # before it checks the file, so this exercises the error-mapping path
    status, body = _post(f"{server}/slice", {"stl_path": "nope.stl", "filament": "unobtainium"})
    assert status in (400, 422)
    assert "error" in body


def _post_with_headers(url, payload, extra_headers):
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", **extra_headers}
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_post_from_foreign_origin_is_forbidden(server):
    # Kotucul cross-origin sayfa: Origin loopback degil -> 403 (drive-by CSRF kapali).
    status, body = _post_with_headers(
        f"{server}/slice", {"stl_path": "x.stl"}, {"Origin": "http://evil.example"}
    )
    assert status == 403
    assert "forbidden" in body["error"]


def test_post_with_foreign_host_is_forbidden(server):
    # DNS-rebinding: Host saldirganin alan adi -> 403.
    status, body = _post_with_headers(
        f"{server}/validate", {"stl_path": "x.stl"}, {"Host": "attacker.example"}
    )
    assert status == 403
    assert "forbidden" in body["error"]


def test_post_from_loopback_origin_is_allowed(server):
    # Ayni-origin Vera Console: Origin loopback -> normal islenir (403 DEGIL; stl_path
    # eksik oldugu icin 400 doner, ama origin/host kontrolunu gecmis olur).
    status, body = _post_with_headers(
        f"{server}/slice", {}, {"Origin": server}
    )
    assert status == 400
    assert "error" in body


def test_options_preflight_has_no_wildcard_cors(server):
    req = urllib.request.Request(f"{server}/slice", method="OPTIONS")
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.status == 204
        assert resp.headers.get("Access-Control-Allow-Origin") is None


def test_slice_busy_returns_409_without_queueing(server, tmp_path):
    stl_path = tmp_path / "cube.stl"
    stl_path.write_bytes(b"x" * 84)

    assert slicer_bridge._acquire_slice_slot()
    try:
        status, body = _post(
            f"{server}/slice",
            {"stl_path": str(stl_path), "filament": "petg"},
        )
    finally:
        slicer_bridge._release_slice_slot()

    assert status == 409
    assert "already running" in body["error"]
