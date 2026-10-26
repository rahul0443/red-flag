"""Known-phishing checks: OpenPhish community feed (free, cached) + URLhaus if a key is set."""
import os
import time
from urllib.parse import urlparse

import httpx

_cache = {"ts": 0.0, "urls": set(), "hosts": set()}
SUSPICIOUS_TLDS = {"top", "xyz", "click", "link", "icu", "buzz", "cfd", "sbs", "rest", "monster", "cyou", "live", "shop", "club"}


def _load_openphish():
    if time.time() - _cache["ts"] < 3600 and _cache["urls"]:
        return
    try:
        r = httpx.get("https://openphish.com/feed.txt", timeout=15, follow_redirects=True)
        r.raise_for_status()
        urls = {u.strip().lower() for u in r.text.splitlines() if u.strip().lower().startswith("http")}
        _cache.update(ts=time.time(), urls=urls, hosts={urlparse(u).hostname for u in urls})
    except httpx.HTTPError:
        _cache["ts"] = time.time()


def check_blocklists(url: str) -> dict:
    host = (urlparse(url).hostname or "").lower()
    _load_openphish()
    hits, checked = [], []
    if _cache["urls"]:
        checked.append("OpenPhish")
        if url.lower() in _cache["urls"] or host in _cache["hosts"]:
            hits.append("OpenPhish")
    key = os.getenv("URLHAUS_AUTH_KEY")
    if key:
        checked.append("URLhaus")
        try:
            r = httpx.post("https://urlhaus-api.abuse.ch/v1/url/", data={"url": url},
                           headers={"Auth-Key": key}, timeout=10)
            if r.json().get("query_status") == "ok":
                hits.append("URLhaus")
        except (httpx.HTTPError, ValueError):
            pass
    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    return {"url": url, "listed_in": hits, "feeds_checked": checked,
            "not_listed_note": "Absence from feeds does NOT mean safe: new phishing sites are often not listed yet.",
            "suspicious_tld": tld in SUSPICIOUS_TLDS, "hyphen_count_in_domain": host.count("-")}
