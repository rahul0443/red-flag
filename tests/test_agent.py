import json
import pytest
from conftest import GOOD, FakeClient, call, reply

MSG = "USPS: pay $1.99 now http://usps-fee.top/pay"


def run(loop, msg=MSG):
    return list(loop.investigate(msg))


def verdict(events):
    v = [e for e in events if e["type"] == "verdict"]
    assert len(v) == 1, [e["type"] for e in events]
    return v[0]


def test_happy_path_tool_then_submit(stub_tools, use_backends):
    c = FakeClient([reply("checking", [call("rdap_lookup", {"domain": "usps-fee.top"})]), reply(None, [call("submit_verdict", GOOD)])])
    use_backends(c)
    ev = run(stub_tools)
    assert verdict(ev)["verdict"] == "Scam"
    assert any(e["type"] == "tool_result" and e["tool"] == "rdap_lookup" for e in ev)


def test_malformed_tool_args_and_unknown_tool_do_not_crash(stub_tools, use_backends):
    c = FakeClient([reply(None, [call("rdap_lookup", "{not json", "a"), call("no_such_tool", {}, "b")]), reply(None, [call("submit_verdict", GOOD)])])
    use_backends(c)
    assert verdict(run(stub_tools))["verdict"] == "Scam"


@pytest.mark.parametrize("bad", [{}, {"verdict": "Banana"}, {"verdict": "Scam", "confidence": "high", "evidence": "oops", "tactics": 5},
                                 {"verdict": "Looks Safe", "confidence": 99, "evidence": [None, 3, {"finding": ""}, {"finding": "x", "severity": "weird"}]}])
def test_garbage_verdict_is_normalised(stub_tools, use_backends, bad):
    use_backends(FakeClient([reply(None, [call("submit_verdict", bad)])]))
    v = verdict(run(stub_tools))
    assert v["verdict"] in ("Scam", "Suspicious", "Looks Safe") and 0 <= v["confidence"] <= 1
    assert isinstance(v["evidence"], list) and isinstance(v["tactics"], list) and v["summary"] and v["advice"]
    assert all(e["severity"] in ("high", "medium", "low", "reassuring") for e in v["evidence"])


def test_blocklist_hit_can_never_be_called_safe(stub_tools, use_backends, monkeypatch):
    monkeypatch.setitem(stub_tools.DISPATCH, "check_blocklists", lambda url: {"url": url, "listed_in": ["OpenPhish"]})
    safe = dict(GOOD, verdict="Looks Safe")
    use_backends(FakeClient([reply(None, [call("check_blocklists", {"url": "http://usps-fee.top/pay"})]), reply(None, [call("submit_verdict", safe)])]))
    v = verdict(run(stub_tools))
    assert v["verdict"] == "Scam" and v["evidence"][0]["source"] == "check_blocklists"


def test_raw_text_tool_call_is_recovered(stub_tools, use_backends):
    params = "".join(f'<atem:parameter name="{k}">{json.dumps(v) if not isinstance(v, str) else v}</atem:parameter>' for k, v in GOOD.items())
    raw = f'<atem:function_calls><atem:invoke name="default.submit_verdict">{params}</atem:invoke></atem:function_calls>'
    use_backends(FakeClient([reply(raw)]))
    ev = run(stub_tools)
    assert verdict(ev)["verdict"] == "Scam"
    assert not any(e["type"] == "thought" and "function_calls" in e["text"] for e in ev)


def test_failover_to_second_backend(stub_tools, use_backends):
    dead = FakeClient([RuntimeError("503")])
    live = FakeClient([reply(None, [call("submit_verdict", GOOD)])])
    use_backends(dead, live)
    ev = run(stub_tools)
    assert verdict(ev)["verdict"] == "Scam"
    assert any(e["type"] == "thought" and "switching" in e["text"] for e in ev)


def test_all_backends_down_gives_graceful_verdict_not_exception(stub_tools, use_backends):
    use_backends(FakeClient([RuntimeError("down")]), FakeClient([TimeoutError("slow")]))
    v = verdict(run(stub_tools))
    assert v["verdict"] == "Suspicious" and "could not finish" in v["summary"]


def test_all_backends_down_but_blocklist_hit_still_scam(stub_tools, use_backends, monkeypatch):
    monkeypatch.setitem(stub_tools.DISPATCH, "check_blocklists", lambda url: {"listed_in": ["OpenPhish"]})
    use_backends(FakeClient([reply(None, [call("check_blocklists", {"url": "u"})]), RuntimeError("down")]))
    assert verdict(run(stub_tools))["verdict"] == "Scam"


def test_endless_chatter_hits_step_cap(stub_tools, use_backends, monkeypatch):
    monkeypatch.setattr(stub_tools.config, "MAX_AGENT_STEPS", 4)
    c = FakeClient([reply("hmm")])
    use_backends(c)
    v = verdict(run(stub_tools))
    assert c.calls <= 4 and v["verdict"] == "Suspicious"


def test_tool_exception_is_reported_not_raised(stub_tools, use_backends, monkeypatch):
    def boom(**kw): raise RuntimeError("tool exploded")
    monkeypatch.setitem(stub_tools.DISPATCH, "rdap_lookup", boom)
    use_backends(FakeClient([reply(None, [call("rdap_lookup", {"domain": "x.top"})]), reply(None, [call("submit_verdict", GOOD)])]))
    ev = run(stub_tools)
    assert any(e["type"] == "tool_result" and "error" in e["result"] for e in ev) and verdict(ev)


@pytest.mark.parametrize("msg", ["", "\x00\x00", "http://[abc", "x" * 9000, "🚩" * 500, "<script>alert(1)</script>"])
def test_odd_messages_never_raise(stub_tools, use_backends, msg):
    use_backends(FakeClient([reply(None, [call("submit_verdict", GOOD)])]))
    assert verdict(run(stub_tools, msg))


def test_no_model_configured(stub_tools, monkeypatch):
    monkeypatch.setattr(stub_tools, "backends", lambda: [])
    assert run(stub_tools)[-1]["type"] == "error"
