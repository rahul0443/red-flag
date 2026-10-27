import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SHOTS = Path(os.getenv("UI_SHOTS", ROOT / "tests" / "ui" / "shots"))


def sse(events):
    return "".join(f"data: {json.dumps(e)}\n\n" for e in events + [{"type": "done"}])


TINY_JPEG = ("/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/"
             "2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgA/9k=")

SCAM = [
    {"type": "start", "source": "text", "urls_found": ["http://usps-redelivery-help.top/pay"]},
    {"type": "tool_call", "step": 0, "tool": "inspect_link_sandbox", "args": {"url": "http://usps-redelivery-help.top/pay"}},
    {"type": "thought", "step": 1, "text": "I'll check where this link really goes."},
    {"type": "tool_call", "step": 1, "tool": "expand_url", "args": {"url": "http://usps-redelivery-help.top/pay"}},
    {"type": "tool_call", "step": 1, "tool": "rdap_lookup", "args": {"domain": "usps-redelivery-help.top"}},
    {"type": "tool_call", "step": 1, "tool": "check_blocklists", "args": {"url": "http://usps-redelivery-help.top/pay"}},
    {"type": "tool_call", "step": 1, "tool": "official_contact_check", "args": {"brand": "USPS", "observed_url_or_domain": "usps-redelivery-help.top"}},
    {"type": "triage", "verdict": "Scam", "confidence": 0.99, "model": "meta-models/muse-spark-open-1026", "latency_ms": 2900},
    {"type": "tool_result", "step": 1, "tool": "expand_url", "result": {"final_domain": "usps-redelivery-help.top", "redirect_count": 0, "chain": []}},
    {"type": "tool_result", "step": 1, "tool": "rdap_lookup", "result": {"domain": "x", "age_days": 3, "registrar": "NameCheap"}},
    {"type": "tool_result", "step": 1, "tool": "check_blocklists", "result": {"listed_in": [], "lookalike_signals": ["domain imitates 'usps.com' but is not it"], "suspicious_tld": True}},
    {"type": "tool_result", "step": 1, "tool": "official_contact_check", "result": {"known": True, "official_domains": ["usps.com"], "matches_official_domain": False, "company_policy": "USPS never texts for fees."}},
    {"type": "tool_result", "step": 0, "tool": "inspect_link_sandbox", "result": {"title": "USPS Redelivery", "password_fields": 1, "screenshot_b64": TINY_JPEG}},
    {"type": "verdict", "verdict": "Scam", "confidence": 0.97, "summary": "This is a fake USPS delivery-fee text that sends you to a copycat website.",
     "evidence": [{"finding": "Domain imitates usps.com", "source": "check_blocklists", "severity": "high"}, {"finding": "Domain is 3 days old", "source": "rdap_lookup", "severity": "medium"}],
     "tactics": ["impersonation", "urgency"], "advice": "Do not click or pay. Delete the message.", "usage": {}},
]


def verdict_events(verdict, **kw):
    v = {"type": "verdict", "verdict": verdict, "confidence": 0.8, "summary": "Summary sentence.", "evidence": [{"finding": "A finding", "source": "message", "severity": "low"}],
         "tactics": [], "advice": "Advice sentence.", "usage": {}}
    v.update(kw)
    return [{"type": "start", "source": "text", "urls_found": []}, v]


@pytest.fixture(scope="session")
def server():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    env = {**os.environ, "DISABLE_TOOLS": "inspect_link_sandbox", "MODEL_API_KEY": "test", "PER_IP_PER_MIN": "100000"}
    p = subprocess.Popen([sys.executable, "-m", "uvicorn", "redflag.api.server:app", "--port", str(port), "--log-level", "warning"], cwd=ROOT, env=env)
    for _ in range(80):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close(); break
        except OSError:
            time.sleep(0.1)
    yield f"http://127.0.0.1:{port}"
    p.terminate()


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        yield b
        b.close()


VIEWPORTS = {"phone-s": (320, 640), "phone": (375, 812), "tablet": (768, 1024), "laptop": (1280, 800), "wide": (1920, 1080)}


@pytest.fixture
def make_page(browser, server):
    """make_page(w, h, scheme, events) -> page whose /api/investigate returns the scripted stream."""
    ctxs = []

    def _make(w=1280, h=800, scheme="light", events=None, status=200, body=None, reduced=False, abort=False, delay=0):
        ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, reduced_motion="reduce" if reduced else "no-preference")
        ctxs.append(ctx)
        page = ctx.new_page()
        page.problems = []
        page.on("console", lambda m: m.type in ("error", "warning") and page.problems.append(f"console {m.type}: {m.text}"))
        page.on("pageerror", lambda e: page.problems.append(f"pageerror: {e}"))
        page.requests = []

        def handle(route):
            page.requests.append(route.request.url)
            if abort:
                return route.abort()
            if delay:
                time.sleep(delay)
            route.fulfill(status=status, headers={"content-type": "text/event-stream"} if status == 200 else {"content-type": "application/json"},
                          body=body if body is not None else sse(events or SCAM))
        page.route("**/api/investigate**", handle)
        page.goto(server)
        return page

    yield _make
    for c in ctxs:
        c.close()
