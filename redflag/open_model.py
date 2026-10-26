"""Instant first-pass triage on open-weight Muse Spark Open, shown while the full investigation runs."""
import time

from redflag import config
from redflag.verdict import SYSTEM_PROMPT, get_open_client, parse_json


def triage(message: str) -> dict:
    """One fast call, no tools. Returns verdict, confidence, latency_ms; {'error': ...} if the endpoint is unavailable."""
    t0 = time.time()
    try:
        resp = get_open_client().chat.completions.create(
            model=config.OPEN_MODEL, max_tokens=config.MAX_TOKENS, temperature=0,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": f"<message>\n{message[:4000]}\n</message>"}])
        out = parse_json(resp.choices[0].message.content or "")
        return {"verdict": out.get("verdict"), "confidence": out.get("confidence"),
                "model": config.OPEN_MODEL, "latency_ms": int((time.time() - t0) * 1000)}
    except Exception as e:  # triage is optional: never block the investigation
        return {"error": f"{type(e).__name__}: {e}"[:200]}
