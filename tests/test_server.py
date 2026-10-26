import json
import pytest
from fastapi.testclient import TestClient
from redflag.api import server

client = TestClient(server.app)


def events(r):
    return [json.loads(l[6:]) for l in r.text.split("\n\n") if l.startswith("data: ")]


@pytest.fixture(autouse=True)
def reset(monkeypatch):
    server._hits.clear(); server._active.clear()
    monkeypatch.setattr(server, "investigate", lambda text, source="text": iter([{"type": "start"}, {"type": "verdict", "verdict": "Scam"}]))


def test_text_stream_ends_with_done():
    ev = events(client.post("/api/investigate", json={"text": "hi"}))
    assert [e["type"] for e in ev] == ["start", "verdict", "done"]


@pytest.mark.parametrize("body", [{}, {"text": ""}, {"text": 5}, {"text": "x" * 4001}])
def test_bad_bodies_are_422(body):
    assert client.post("/api/investigate", json=body).status_code == 422


def test_internal_error_hides_details(monkeypatch):
    def boom(text, source="text"):
        raise RuntimeError("secret internals sk-123")
        yield
    monkeypatch.setattr(server, "investigate", boom)
    ev = events(client.post("/api/investigate", json={"text": "hi"}))
    assert ev[0]["type"] == "error" and "secret" not in ev[0]["message"] and ev[-1]["type"] == "done"


def test_rate_limit(monkeypatch):
    monkeypatch.setattr(server, "PER_IP_PER_MIN", 3)
    msgs = [events(client.post("/api/investigate", json={"text": "hi"}))[0]["type"] for _ in range(5)]
    assert msgs[:3] == ["start"] * 3 and msgs[3:] == ["error", "error"]


def test_concurrency_cap_and_release():
    toks = [server._acquire() for _ in range(server.MAX_CONCURRENT)]
    assert all(toks) and server._acquire() is None
    server._release(toks[0])
    assert server._acquire() is not None


def test_stale_lease_expires(monkeypatch):
    toks = [server._acquire() for _ in range(server.MAX_CONCURRENT)]
    for k in toks:
        server._active[k] -= server.LEASE_S + 1
    assert server._acquire() is not None


@pytest.mark.parametrize("data,expect", [(b"", "not a PNG"), (b"hello", "not a PNG"), (b"\x89PNG\r\n\x1a\n" + b"0" * 9_000_000, "too large")])
def test_image_errors_are_friendly(data, expect):
    ev = events(client.post("/api/investigate/image", files={"file": ("x", data, "image/png")}))
    assert any(expect in e.get("message", "") for e in ev) and ev[-1]["type"] == "done"


@pytest.mark.parametrize("data", [b"", b"ID3" + b"0" * 100, b"RIFF" + b"0" * 100])
def test_audio_errors_are_friendly(data):
    ev = events(client.post("/api/investigate/audio", files={"file": ("x", data, "audio/wav")}))
    assert ev[0]["type"] in ("extracting", "error") and ev[-1]["type"] == "done"
    assert not any("Error" in e.get("message", "") and "Exception" in e.get("message", "") for e in ev)
