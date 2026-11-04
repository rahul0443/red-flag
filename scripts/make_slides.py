"""Render docs/slides/slides.html to 1920x1080 PNGs: python scripts/make_slides.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
with sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_page(viewport={"width": 1920, "height": 1080})
    page.goto((ROOT / "docs/slides/slides.html").as_uri())
    for i in (1, 2, 3):
        page.locator(f"#s{i}").screenshot(path=ROOT / "docs/slides" / f"slide-{i}.png")
    b.close()
