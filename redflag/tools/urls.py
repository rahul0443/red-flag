import re
from urllib.parse import urljoin, urlparse

import httpx

from redflag.tools.safety import safe_url

URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"')]+", re.I)
BARE_DOMAIN_RE = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:com|net|org|top|xyz|info|co|io|ly|me|cc|club|online|site|link|click|shop|app|gov|us)(?:/[^\s<>\"')]*)?", re.I)
UA = "Mozilla/5.0 (compatible; RedFlagBot/0.1; +safe-inspection)"


def extract_urls(text: str) -> list[str]:
    found = [u.rstrip(".,;:!?") for u in URL_RE.findall(text)]
    for m in BARE_DOMAIN_RE.findall(text):
        if not any(m in f for f in found) and "@" not in text[max(0, text.find(m) - 1):text.find(m)]:
            found.append(m.rstrip(".,;:!?"))
    seen, out = set(), []
    for u in found:
        if not u.lower().startswith("http"):
            u = "http://" + u
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out[:10]


def expand_url(url: str, max_hops: int = 8) -> dict:
    """Follow redirects manually (each hop re-checked for safety), GET headers only, no body kept."""
    chain, current = [], url
    with httpx.Client(follow_redirects=False, timeout=8, headers={"User-Agent": UA}) as client:
        for _ in range(max_hops):
            err = safe_url(current)
            if err:
                chain.append({"url": current, "status": None, "note": f"blocked: {err}"})
                break
            try:
                with client.stream("GET", current) as r:
                    status, loc = r.status_code, r.headers.get("location")
            except httpx.HTTPError as e:
                chain.append({"url": current, "status": None, "note": f"unreachable: {type(e).__name__}"})
                break
            chain.append({"url": current, "status": status})
            if status in (301, 302, 303, 307, 308) and loc:
                current = urljoin(current, loc)
            else:
                break
    final = chain[-1]["url"]
    return {"original": url, "final_url": final, "final_domain": urlparse(final).hostname,
            "redirect_count": len(chain) - 1, "chain": chain}
