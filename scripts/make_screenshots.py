"""Render README screenshots by replaying a recorded event stream through the real UI. Usage: python scripts/make_screenshots.py stream.json"""
import json, subprocess, sys, time, socket
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
data = json.load(open(sys.argv[1]))
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
p = subprocess.Popen([sys.executable, "-m", "uvicorn", "redflag.api.server:app", "--port", str(port), "--log-level", "warning"], cwd=ROOT)
time.sleep(3)
body = "".join(f"data: {json.dumps(e)}\n\n" for e in data["events"] if e["type"] != "done") + 'data: {"type": "done"}\n\n'
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for name, (w, h), scheme, full in [("home", (1280, 800), "dark", False), ("result", (1280, 900), "dark", False), ("result-mobile", (390, 844), "dark", False), ("result-light", (1280, 900), "light", False)]:
            ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, device_scale_factor=2)
            page = ctx.new_page()
            page.route("**/api/investigate", lambda r: r.fulfill(status=200, headers={"content-type": "text/event-stream"}, body=body))
            page.goto(f"http://127.0.0.1:{port}")
            if name != "home":
                page.fill("#msg", data["msg"]); page.click("#go"); page.wait_for_selector(".vtitle"); page.wait_for_timeout(1800)
                # the replay is instant; show the duration of the recorded real run (12 s)
                page.evaluate("() => { const c = document.querySelector('.vconf'); if (c) c.textContent = c.textContent.replace(/· \\d+ seconds/, '· 12 seconds'); }")
            else:
                page.fill("#msg", data["msg"]); page.wait_for_timeout(300)
            page.screenshot(path=ROOT / "docs" / "img" / f"{name}.png")
            ctx.close()
        b.close()
finally:
    p.terminate()
