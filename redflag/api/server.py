"""FastAPI app: streams investigation events to the browser as Server-Sent Events.
User content is processed in memory only and never written to disk."""
import json
import logging
import os
import threading
import time
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


class TextIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


log = logging.getLogger("redflag")
MAX_CONCURRENT = 4          # investigations running at once (protects API credits)
PER_IP_PER_MIN = int(os.getenv("PER_IP_PER_MIN", "12"))
_slots = threading.BoundedSemaphore(MAX_CONCURRENT)
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


def _sse(events, request: Request):
    """Stream events. User-facing errors are plain sentences; internal details go to the server log only."""
    ip = request.client.host if request.client else "?"
    if _limited(ip):
        yield from _one({"type": "error", "message": "Too many checks in a minute. Wait a moment and try again."})
        return
    if not _slots.acquire(blocking=False):
        yield from _one({"type": "error", "message": "Red Flag is busy right now. Try again in a few seconds."})
        return
    try:
        for ev in events:
            yield f"data: {json.dumps(ev, default=str)}\n\n"
    except ValueError as e:  # expected, user-fixable problems raised with a readable message
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    except Exception:
        log.exception("investigation failed")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Something went wrong on our side. Please try again.'})}\n\n"
    finally:
        _slots.release()
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


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/static", StaticFiles(directory=WEB), name="static")
