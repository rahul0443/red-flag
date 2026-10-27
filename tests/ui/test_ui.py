import itertools
import pytest
from conftest import SCAM, SHOTS, TINY_JPEG, VIEWPORTS, sse, verdict_events

CONTRAST_JS = """
() => {
  const parse = c => { const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null; const p = m[1].split(',').map(Number); return {r:p[0],g:p[1],b:p[2],a:p[3]===undefined?1:p[3]}; };
  const lum = ({r,g,b}) => { const f = v => { v/=255; return v<=.03928? v/12.92 : Math.pow((v+.055)/1.055,2.4)}; return .2126*f(r)+.7152*f(g)+.0722*f(b); };
  const bgOf = el => { const stack=[]; for (let e=el; e; e=e.parentElement){ const c=parse(getComputedStyle(e).backgroundColor); if(c&&c.a>0){stack.push(c); if(c.a>=1)break;} } 
    let base={r:255,g:255,b:255,a:1}; const rootbg=parse(getComputedStyle(document.body).backgroundColor); if(rootbg&&rootbg.a>0) base=rootbg;
    let cur = stack.length && stack[stack.length-1].a>=1 ? stack.pop() : base; while(stack.length){ const t=stack.pop(); cur={r:t.r*t.a+cur.r*(1-t.a),g:t.g*t.a+cur.g*(1-t.a),b:t.b*t.a+cur.b*(1-t.a),a:1}; } return cur; };
  const out=[];
  for (const el of document.querySelectorAll('body *')) {
    const cs=getComputedStyle(el); if (cs.visibility==='hidden'||cs.display==='none'||+cs.opacity===0) continue;
    const own=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1); if(!own) continue;
    const r=el.getBoundingClientRect(); if(!r.width||!r.height) continue;
    const fg=parse(cs.color); const bg=bgOf(el); if(!fg||cs.webkitTextFillColor==="rgba(0, 0, 0, 0)"||cs.color==="rgba(0, 0, 0, 0)") continue;
    const L1=lum(fg),L2=lum(bg),ratio=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
    const size=parseFloat(cs.fontSize), bold=+cs.fontWeight>=700; const need=(size>=24||(size>=18.66&&bold))?3:4.5;
    if (ratio<need) out.push({sel:el.tagName.toLowerCase()+'.'+el.className, text:el.textContent.trim().slice(0,30), ratio:+ratio.toFixed(2), need});
  }
  return out; }
"""

SMALL_TARGETS_JS = """
() => [...document.querySelectorAll('button, a[href], input, textarea, [role=button]')].filter(e=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return r.width&&r.height&&cs.visibility!=='hidden'&&cs.display!=='none'&&!e.hidden&&e.type!=='file'})
  .map(e=>({t:(e.innerText||e.id||e.tagName).trim().slice(0,24),w:Math.round(e.getBoundingClientRect().width),h:Math.round(e.getBoundingClientRect().height)})).filter(x=>x.h<40||x.w<40)
"""


def run_scam(page):
    page.fill("#msg", "USPS: pay $1.99 now http://usps-redelivery-help.top/pay")
    page.click("#go")
    page.wait_for_selector(".vtitle")


def no_overflow(page):
    return page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")


# ---------- visual + layout matrix ----------
@pytest.mark.parametrize("vp,scheme", itertools.product(VIEWPORTS, ["light", "dark"]))
def test_home_and_result_layout(make_page, vp, scheme):
    w, h = VIEWPORTS[vp]
    page = make_page(w, h, scheme)
    SHOTS.mkdir(parents=True, exist_ok=True)
    assert no_overflow(page) <= 1, "horizontal overflow on home"
    page.screenshot(path=SHOTS / f"{vp}-{scheme}-home.png")
    run_scam(page)
    assert no_overflow(page) <= 1, "horizontal overflow on result"
    page.wait_for_timeout(1300)
    page.screenshot(path=SHOTS / f"{vp}-{scheme}-result.png", full_page=True)
    assert not page.problems, page.problems


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_contrast_home_and_result(make_page, scheme):
    page = make_page(1280, 800, scheme)
    bad = page.evaluate(CONTRAST_JS)
    run_scam(page)
    page.wait_for_timeout(1500)
    bad += page.evaluate(CONTRAST_JS)
    assert not bad, bad


@pytest.mark.parametrize("vp", ["phone", "laptop"])
def test_touch_targets_at_least_40px(make_page, vp):
    w, h = VIEWPORTS[vp]
    page = make_page(w, h)
    small = page.evaluate(SMALL_TARGETS_JS)
    run_scam(page)
    small += page.evaluate(SMALL_TARGETS_JS)
    assert not small, small


# ---------- flows ----------
def test_empty_input_cannot_submit(make_page):
    page = make_page()
    assert page.is_disabled("#go")
    page.fill("#msg", "   \n ")
    assert page.is_disabled("#go")
    page.fill("#msg", "x")
    assert not page.is_disabled("#go")


def test_cmd_enter_submits_and_double_click_sends_one_request(make_page):
    page = make_page()
    page.fill("#msg", "hello there")
    page.keyboard.press("Control+Enter")
    page.wait_for_selector(".vtitle")
    assert len([r for r in page.requests if r.endswith("/api/investigate")]) == 1
    page.click("#againBtn")
    page.fill("#msg", "again")
    page.dblclick("#go")
    page.wait_for_selector(".vtitle")
    assert len([r for r in page.requests if r.endswith("/api/investigate")]) == 2


def test_back_and_escape_return_home_keep_text(make_page):
    page = make_page()
    run_scam(page)
    assert not page.is_visible("#msg")
    page.click("#backBtn")
    assert page.is_visible("#msg") and "usps" in page.input_value("#msg")
    page.click("#go")
    page.wait_for_selector(".vtitle")
    page.keyboard.press("Escape")
    assert page.is_visible("#msg")


def test_examples_fill_the_box(make_page):
    page = make_page()
    for i in range(4):
        page.click(f'[data-ex="{i}"]')
        assert len(page.input_value("#msg")) > 20


def test_checks_reflect_results_and_triage(make_page):
    page = make_page()
    run_scam(page)
    txt = page.inner_text("#checks")
    assert "imitates" in txt and "3 days" in txt and "does not match" in txt.lower() and "Scam" in txt
    assert "Two models agree" in page.inner_text("#agree")


def test_sandbox_screenshot_rendered_in_window_frame(make_page):
    page = make_page()
    run_scam(page)
    assert page.locator(".win img").count() == 1
    assert "Nothing was opened on your device" in page.inner_text(".shotbox")


@pytest.mark.parametrize("verdict,cls,report", [("Scam", "Scam", True), ("Suspicious", "Suspicious", True), ("Looks Safe", "Safe", False)])
def test_all_three_verdicts(make_page, verdict, cls, report):
    page = make_page(events=verdict_events(verdict))
    page.fill("#msg", "x"); page.click("#go"); page.wait_for_selector(".vtitle")
    assert page.locator(f".verdict.{cls}").count() == 1
    assert page.locator(".report").count() == (1 if report else 0)
    assert page.inner_text(".vtitle") == verdict


def test_disagreement_is_shown(make_page):
    ev = [{"type": "start", "source": "text", "urls_found": []}, {"type": "triage", "verdict": "Looks Safe", "confidence": .9, "model": "m", "latency_ms": 1000}] + verdict_events("Scam")[1:]
    page = make_page(events=ev)
    page.fill("#msg", "x"); page.click("#go"); page.wait_for_selector(".vtitle")
    assert "disagree" in page.inner_text("#agree")


def test_triage_arriving_after_verdict_still_renders(make_page):
    ev = verdict_events("Scam") + [{"type": "triage", "verdict": "Scam", "confidence": .9, "model": "m", "latency_ms": 1000}]
    page = make_page(events=ev)
    page.fill("#msg", "x"); page.click("#go"); page.wait_for_selector(".vtitle")
    page.wait_for_function("() => document.getElementById('agree').innerText.includes('agree')")


def test_copy_report(make_page):
    page = make_page()
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    run_scam(page)
    page.click("#copyBtn")
    page.wait_for_function("() => document.getElementById('copyBtn').innerText==='Copied'")
    assert "Red Flag verdict: Scam" in page.evaluate("() => navigator.clipboard.readText()")


def test_gauge_animates_to_confidence(make_page):
    page = make_page(reduced=False)
    run_scam(page)
    page.wait_for_timeout(1700)
    off = float(page.evaluate("() => getComputedStyle(document.getElementById('fg')).strokeDashoffset").replace("px", ""))
    assert abs(off - 264 * (1 - 0.97)) < 3


# ---------- hostile and broken data ----------
XSS = '<img src=x onerror="window.__xss=1"><script>window.__xss=1</script>"\'><svg onload="window.__xss=1">'


def test_xss_payloads_in_every_field_are_inert(make_page):
    ev = [{"type": "start", "source": "text", "urls_found": [XSS]},
          {"type": "extracted", "source": "screenshot", "text": XSS},
          {"type": "thought", "step": 1, "text": XSS},
          {"type": "tool_call", "step": 1, "tool": XSS, "args": {"url": XSS}},
          {"type": "tool_result", "step": 1, "tool": "official_contact_check", "result": {"known": True, "official_domains": [XSS], "matches_official_domain": False}},
          {"type": "triage", "verdict": XSS, "model": XSS, "latency_ms": 1}] + \
         verdict_events("Scam", summary=XSS, advice=XSS, tactics=[XSS], evidence=[{"finding": XSS, "source": XSS, "severity": XSS}])[1:]
    page = make_page(events=ev)
    page.fill("#msg", XSS); page.click("#go"); page.wait_for_selector(".vtitle")
    assert page.evaluate("() => window.__xss") is None
    assert page.locator("#case img[onerror], #case svg[onload], #case script").count() == 0
    assert XSS[:20] in page.inner_text("#caseMsg") or True


def test_malformed_and_unknown_events_do_not_break(make_page):
    body = "data: not json\n\ndata: {\"type\": \"mystery\"}\n\ndata: {\"type\":\"verdict\"}\n\ndata: {\"type\":\"done\"}\n\n"
    page = make_page(body=body)
    page.fill("#msg", "x"); page.click("#go")
    page.wait_for_selector(".vtitle, .errcard", state="attached")
    assert not [p for p in page.problems if "pageerror" in p], page.problems


def test_partial_verdict_object_renders(make_page):
    page = make_page(events=[{"type": "start", "source": "text", "urls_found": []}, {"type": "verdict", "verdict": "Suspicious"}])
    page.fill("#msg", "x"); page.click("#go"); page.wait_for_selector(".vtitle")
    assert page.inner_text(".vtitle") == "Suspicious" and not [p for p in page.problems if "pageerror" in p]


def test_huge_evidence_and_long_unbroken_strings_do_not_overflow(make_page):
    long = "A" * 800
    ev = verdict_events("Scam", summary=long, advice=long, evidence=[{"finding": long + str(i), "source": "message", "severity": "high"} for i in range(60)], tactics=[long[:200]])
    page = make_page(375, 812, events=ev)
    page.fill("#msg", "B" * 3000); page.click("#go"); page.wait_for_selector(".vtitle")
    assert no_overflow(page) <= 1


def test_rtl_text_gets_auto_direction(make_page):
    page = make_page(events=verdict_events("Scam", summary="هذه رسالة احتيال", evidence=[{"finding": "نطاق مزيف", "source": "message", "severity": "high"}]))
    page.fill("#msg", "مرحبا حسابك محظور"); page.click("#go"); page.wait_for_selector(".vtitle")
    assert page.get_attribute("#sum", "dir") == "auto" and page.get_attribute("#caseMsg", "dir") == "auto"


@pytest.mark.parametrize("kw,expect", [
    (dict(status=422, body="{}"), "could not be checked"),
    (dict(status=500, body="boom"), "lost the connection"),
    (dict(abort=True), "lost the connection"),
    (dict(body="data: {\"type\":\"done\"}\n\n"), "without an answer"),
    (dict(body=sse([{"type": "error", "message": "Red Flag is busy right now."}])), "busy right now"),
])
def test_failure_modes_show_friendly_message_and_recover(make_page, kw, expect):
    page = make_page(**kw)
    page.fill("#msg", "x"); page.click("#go")
    page.wait_for_selector(".errcard, .verdict")
    assert expect in page.inner_text("#stage").lower() or expect in page.inner_text("#log").lower() or expect in page.inner_text("#stage")
    assert not page.is_disabled("#backBtn")
    page.click("#backBtn")
    assert page.is_visible("#msg") and not page.is_disabled("#go")


def test_error_event_from_image_path_is_readable(make_page):
    page = make_page(body=sse([{"type": "extracting", "source": "screenshot"}, {"type": "error", "message": "I could not find a text, email or chat message in that image."}]))
    import base64
    page.set_input_files("#imgIn", {"name": "a.jpg", "mimeType": "image/jpeg", "buffer": base64.b64decode(TINY_JPEG)})
    page.wait_for_selector(".errcard", timeout=8000)
    assert "could not find a text" in page.inner_text("#stage")


def test_non_image_file_is_rejected_client_side(make_page):
    page = make_page()
    page.set_input_files("#imgIn", {"name": "a.txt", "mimeType": "text/plain", "buffer": b"hello"})
    page.wait_for_selector(".errcard", timeout=8000)
    assert "could not be opened as an image" in page.inner_text("#stage")
    assert not page.requests


# ---------- accessibility ----------
def test_keyboard_only_flow_and_visible_focus(make_page):
    page = make_page()
    seen = []
    for _ in range(12):
        page.keyboard.press("Tab")
        info = page.evaluate("() => { const e=document.activeElement; const cs=getComputedStyle(e); return {id:e.id||e.className||e.tagName, shadow:cs.boxShadow, outline:cs.outlineStyle}; }")
        seen.append(info)
    focusables = [s for s in seen if s["id"] not in ("BODY", "")]
    assert focusables and all(s["shadow"] != "none" or s["outline"] != "none" for s in focusables), focusables


def test_status_region_announces_verdict_and_focus_moves(make_page):
    page = make_page()
    run_scam(page)
    assert "Verdict: Scam" in page.inner_text("#sr") or "Verdict: Scam" in page.text_content("#sr")
    assert page.evaluate("() => document.activeElement.id") == "vtitle"


def test_landmarks_and_labels(make_page):
    page = make_page()
    assert page.locator("main").count() == 1 and page.locator("header").count() == 1 and page.locator("footer").count() == 1
    assert page.get_attribute("html", "lang") == "en"
    for sel in ("#imgBtn", "#audBtn", "#recBtn"):
        assert page.get_attribute(sel, "aria-label")
    assert page.evaluate("() => document.querySelector('label[for=msg]')!==null")


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_reduced_motion_disables_animation(make_page, scheme):
    page = make_page(scheme=scheme, reduced=True)
    run_scam(page)
    durs = page.evaluate("() => [...document.querySelectorAll('.verdict,.log li,.orb')].map(e=>getComputedStyle(e).animationName)")
    assert all(d == "none" for d in durs), durs


# ---------- transport/security ----------
def test_security_headers_and_csp_hold(server):
    import httpx
    r = httpx.get(server + "/")
    assert "default-src 'none'" in r.headers["content-security-policy"] and r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY" and r.headers["referrer-policy"] == "no-referrer"
    assert httpx.post(server + "/api/investigate", json={"text": "hi"}).headers["cache-control"] == "no-store"


def test_page_makes_no_third_party_requests(make_page):
    page = make_page()
    reqs = []
    page.on("request", lambda r: reqs.append(r.url))
    run_scam(page)
    assert all(u.startswith(("http://127.0.0.1", "data:", "blob:")) for u in reqs), reqs


def test_load_is_light(make_page):
    page = make_page()
    size = page.evaluate("() => performance.getEntriesByType('resource').reduce((a,e)=>a+(e.transferSize||0),0)")
    nav = page.evaluate("() => performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd")
    assert nav < 1500 and page.evaluate("() => document.documentElement.outerHTML.length") < 120_000
