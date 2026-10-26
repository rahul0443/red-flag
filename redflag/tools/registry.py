"""Tool schemas shown to the model + dispatch."""
from redflag.tools.blocklists import check_blocklists
from redflag.tools.official import official_contact_check
from redflag.tools.rdap import rdap_lookup
from redflag.tools.urls import expand_url


def _fn(name, desc, props, required):
    return {"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": props, "required": required}}}


TOOLS = [
    _fn("expand_url", "Follow redirects of a (possibly shortened) URL and return the full redirect chain and final domain. Never sends user data.",
        {"url": {"type": "string"}}, ["url"]),
    _fn("rdap_lookup", "Look up domain registration date, age in days and registrar via RDAP. Very young domains (<90 days) are a strong scam signal.",
        {"domain": {"type": "string", "description": "e.g. example.com"}}, ["domain"]),
    _fn("check_blocklists", "Check a URL against known phishing feeds and basic domain heuristics (suspicious TLD, hyphens).",
        {"url": {"type": "string"}}, ["url"]),
    _fn("official_contact_check", "Look up a company's official domains and its known policies (what it never does), and compare against a domain seen in the message.",
        {"brand": {"type": "string", "description": "company the message claims to be from"},
         "observed_url_or_domain": {"type": "string", "description": "URL/domain/sender seen in the message, if any"}}, ["brand"]),
    _fn("submit_verdict", "FINAL STEP. Submit your conclusion once you are confident. Every evidence item must come from the message or a tool result.",
        {"verdict": {"type": "string", "enum": ["Scam", "Suspicious", "Looks Safe"]},
         "confidence": {"type": "number", "description": "0 to 1"},
         "summary": {"type": "string", "description": "one plain-language sentence for a non-technical reader"},
         "evidence": {"type": "array", "items": {"type": "object", "properties": {
             "finding": {"type": "string"}, "source": {"type": "string", "description": "message | expand_url | rdap_lookup | check_blocklists | official_contact_check | inspect_link_sandbox"},
             "severity": {"type": "string", "enum": ["high", "medium", "low", "reassuring"]}}, "required": ["finding", "source", "severity"]}},
         "tactics": {"type": "array", "items": {"type": "string"}, "description": "manipulation tactics: urgency, threat, impersonation, gift-card/crypto payment, secrecy, too-good-to-be-true..."},
         "advice": {"type": "string", "description": "what the person should do next"}},
        ["verdict", "confidence", "summary", "evidence", "tactics", "advice"]),
]

import os

def inspect_link_sandbox(url: str) -> dict:
    from redflag.tools.sandbox import inspect_link_sandbox as run  # lazy: modal import is heavy
    return run(url)


_DISABLED = {t for t in os.getenv("DISABLE_TOOLS", "").split(",") if t}  # ablation studies
TOOLS = [t for t in TOOLS if t["function"]["name"] not in _DISABLED]

_SANDBOX_OK = "inspect_link_sandbox" not in _DISABLED and (
    os.path.exists(os.path.expanduser("~/.modal.toml")) or bool(os.getenv("MODAL_TOKEN_ID")))

DISPATCH = {"expand_url": expand_url, "rdap_lookup": rdap_lookup,
            "check_blocklists": check_blocklists, "official_contact_check": official_contact_check}
if _SANDBOX_OK:  # started by the system, not offered to the model as a tool
    DISPATCH["inspect_link_sandbox"] = inspect_link_sandbox
