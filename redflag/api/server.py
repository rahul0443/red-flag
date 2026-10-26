"""FastAPI app: streams investigation events to the browser as Server-Sent Events.
User content is processed in memory only and never written to disk."""
import json
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from redflag.agent.loop import investigate
from redflag.inputs import MAX_AUDIO_BYTES, MAX_IMAGE_BYTES, transcribe_audio, transcribe_image

WEB = Path(__file__).resolve().parent.parent.parent / "web"
app = FastAPI(title="Red Flag")


class TextIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


def _sse(events):
    try:
        for ev in events:
            yield f"data: {json.dumps(ev, default=str)}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'{type(e).__name__}: {e}'})}\n\n"
    yield "data: {\"type\": \"done\"}\n\n"


@app.post("/api/investigate")
def investigate_text(body: TextIn):
    return StreamingResponse(_sse(investigate(body.text)), media_type="text/event-stream",
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
async def investigate_image(file: UploadFile = File(...)):
    data = await file.read(MAX_IMAGE_BYTES + 1)
    mime = file.content_type or ""
    return StreamingResponse(_sse(_extract_then_investigate("screenshot", lambda: transcribe_image(data, mime))),
                             media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.post("/api/investigate/audio")
async def investigate_audio(file: UploadFile = File(...)):
    data = await file.read(MAX_AUDIO_BYTES + 1)
    return StreamingResponse(_sse(_extract_then_investigate("voicemail", lambda: transcribe_audio(data))),
                             media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/static", StaticFiles(directory=WEB), name="static")
