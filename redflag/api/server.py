"""FastAPI app: streams investigation events to the browser as Server-Sent Events.
User content is processed in memory only and never written to disk."""
import json
import logging
import os
import threading
from contextlib import asynccontextmanager
import time

import anyio
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from redflag.agent.loop import investigate
from redflag.inputs import MAX_AUDIO_BYTES, MAX_IMAGE_BYTES, transcribe_audio, transcribe_image

WEB = Path(__file__).resolve().parent.parent.parent / "web"
app = FastAPI(title="Red Flag")


@asynccontextmanager
async def _lifespan(_):
    """Fetch the phishing feed once at boot so the first user does not wait for it."""
    from redflag.tools.blocklists import _load_openphish
    threading.Thread(target=_load_openphish, daemon=True).start()
    yield


app.router.lifespan_context = _lifespan


class TextIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


log = logging.getLogger("redflag")
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "6"))          # investigations running at once (protects API credits)
PER_IP_PER_MIN = int(os.getenv("PER_IP_PER_MIN", "12"))
LEASE_S = 240               # a slot frees itself after this long, even if a client vanished mid-stream
_active: dict[object, float] = {}
_lock = threading.Lock()


def _acquire():
    now = time.time()
    with _lock:
        for k in [k for k, t in _active.items() if now - t > LEASE_S]:
            del _active[k]
        if len(_active) >= MAX_CONCURRENT:
            return None
        tok = object()
        _active[tok] = now
        return tok


def _release(tok):
    with _lock:
        _active.pop(tok, None)
_hits: dict[str, deque] = defaultdict(deque)


def _limited(ip: str) -> bool:
    now, q = time.time(), _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    q.append(now)
    return len(q) > PER_IP_PER_MIN


def _one(ev):
    yield f"data: {json.dumps(ev)}\n\n"
    yield 'data: {"type": "done"}\n\n'


_END = object()


def _next(it):
    try:
        return next(it)
    except StopIteration:
        return _END


async def _sse(events, request: Request):
    """Stream events. User-facing errors are plain sentences; internal details go to the server log only.
    Async so that a client that disconnects cancels this generator and frees its slot at once."""
    ip = request.client.host if request.client else "?"
    if _limited(ip):
        for chunk in _one({"type": "error", "message": "Too many checks in a minute. Wait a moment and try again."}):
            yield chunk
        return
    tok = _acquire()
    for _ in range(50):  # queue for up to 25 s instead of turning people away
        if tok is not None:
            break
        await anyio.sleep(0.5)
        tok = _acquire()
    if tok is None:
        for chunk in _one({"type": "error", "message": "Red Flag is busy right now. Try again in a few seconds."}):
            yield chunk
        return
    try:
        it = iter(events)
        while True:
            ev = await anyio.to_thread.run_sync(_next, it, abandon_on_cancel=True)
            if ev is _END:
                break
            yield f"data: {json.dumps(ev, default=str)}\n\n"
    except ValueError as e:  # expected, user-fixable problems raised with a readable message
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    except Exception:
        log.exception("investigation failed")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Something went wrong on our side. Please try again.'})}\n\n"
    finally:
        _release(tok)
    yield 'data: {"type": "done"}\n\n'


@app.post("/api/investigate")
def investigate_text(body: TextIn, request: Request):
    return StreamingResponse(_sse(investigate(body.text.replace("\x00", "")), request), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _extract_then_investigate(source, extract):
    yield {"type": "extracting", "source": source}
    try:
        text = extract()
    except ValueError as e:
        yield {"type": "error", "message": str(e)}
        return
    yield {"type": "extracted", "source": source, "text": text}
    yield from investigate(text, source=source)


@app.post("/api/investigate/image")
async def investigate_image(request: Request, file: UploadFile = File(...)):
    data = await file.read(MAX_IMAGE_BYTES + 1)
    mime = file.content_type or ""
    return StreamingResponse(_sse(_extract_then_investigate("screenshot", lambda: transcribe_image(data, mime)), request),
                             media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.post("/api/investigate/audio")
async def investigate_audio(request: Request, file: UploadFile = File(...)):
    data = await file.read(MAX_AUDIO_BYTES + 1)
    return StreamingResponse(_sse(_extract_then_investigate("voicemail", lambda: transcribe_audio(data)), request),
                             media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


CSP = ("default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
       "connect-src 'self'; media-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.update({
        "Content-Security-Policy": CSP,
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "X-Frame-Options": "DENY",
        "Permissions-Policy": "microphone=(self), camera=(), geolocation=(), payment=()",
        "Cross-Origin-Opener-Policy": "same-origin",
    })
    if request.url.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/static", StaticFiles(directory=WEB), name="static")
