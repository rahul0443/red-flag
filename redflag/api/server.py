"""FastAPI app: streams investigation events to the browser as Server-Sent Events.
User content is processed in memory only and never written to disk."""
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from redflag.agent.loop import investigate

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


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/static", StaticFiles(directory=WEB), name="static")
