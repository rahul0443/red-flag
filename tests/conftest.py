import os
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ["DISABLE_TOOLS"] = "inspect_link_sandbox"   # no cloud sandbox in tests
os.environ.setdefault("MODEL_API_KEY", "test-key")
os.environ["BASETEN_API_KEY"] = "test-baseten"
os.environ["AGENT_BACKEND"] = "spark"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest


def call(name, args, cid="c1"):
    import json
    a = args if isinstance(args, str) else json.dumps(args)
    return SimpleNamespace(id=cid, function=SimpleNamespace(name=name, arguments=a))


def reply(content=None, tool_calls=None):
    msg = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg, finish_reason="stop")],
                           usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5))


class FakeClient:
    """Scripted stand-in for the OpenAI client. Each script item is a reply or an Exception to raise."""
    def __init__(self, script):
        self.script, self.calls = list(script), 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kw):
        self.calls += 1
        item = self.script.pop(0) if self.script else self.script_last
        self.script_last = item
        if isinstance(item, Exception):
            raise item
        return item


GOOD = {"verdict": "Scam", "confidence": 0.9, "summary": "s", "evidence": [{"finding": "f", "source": "message", "severity": "high"}],
        "tactics": ["urgency"], "advice": "a"}


@pytest.fixture
def stub_tools(monkeypatch):
    from redflag.agent import loop
    monkeypatch.setitem(loop.DISPATCH, "check_blocklists", lambda url: {"url": url, "listed_in": [], "feeds_checked": []})
    monkeypatch.setitem(loop.DISPATCH, "expand_url", lambda url: {"final_url": url, "redirect_count": 0, "chain": []})
    monkeypatch.setitem(loop.DISPATCH, "rdap_lookup", lambda domain: {"domain": domain, "age_days": 3})
    return loop


@pytest.fixture
def use_backends(monkeypatch):
    from redflag.agent import loop
    def _set(*clients):
        monkeypatch.setattr(loop, "backends", lambda: [(c, "m", f"B{i}") for i, c in enumerate(clients)])
    return _set
