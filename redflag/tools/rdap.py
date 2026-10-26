from datetime import datetime, timezone

import re

import httpx

_DOMAIN = re.compile(r"^(?=.{1,253}$)([a-z0-9_-]{1,63}\.)+[a-z0-9-]{2,63}$")


def _clean(domain: str) -> str | None:
    d = str(domain or "").lower().strip().removeprefix("www.").rstrip(".")
    try:
        d = d.encode("idna").decode("ascii")
    except UnicodeError:
        return None
    return d if _DOMAIN.match(d) else None


def _event(data: dict, action: str):
    for e in data.get("events", []):
        if e.get("eventAction") == action:
            return e.get("eventDate")


def rdap_lookup(domain: str) -> dict:
    raw = domain
    domain = _clean(domain)
    if not domain:
        return {"domain": str(raw)[:80], "error": "not a valid domain name, so no registration lookup was possible"}
    try:
        r = httpx.get(f"https://rdap.org/domain/{domain}", timeout=10, follow_redirects=True)
    except httpx.HTTPError as e:
        return {"domain": domain, "error": f"lookup failed: {type(e).__name__}"}
    if r.status_code == 404:
        return {"domain": domain, "error": "no registration record found (domain may not exist)"}
    if r.status_code != 200:
        return {"domain": domain, "error": f"RDAP returned HTTP {r.status_code}"}
    try:
        data = r.json()
        if not isinstance(data, dict):
            raise ValueError
    except ValueError:
        return {"domain": domain, "error": "registry returned an unreadable answer"}
    registered = _event(data, "registration")
    age_days = None
    if registered:
        try:
            dt = datetime.fromisoformat(registered.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - dt).days
        except ValueError:
            registered = None
    registrar = None
    try:
        for ent in data.get("entities", []):
            if "registrar" in ent.get("roles", []):
                for item in ent.get("vcardArray", [None, []])[1]:
                    if item[0] == "fn":
                        registrar = item[3]
    except (TypeError, IndexError, AttributeError, KeyError):
        pass
    return {"domain": domain, "registered": registered, "age_days": age_days,
            "registrar": registrar, "status": data.get("status", [])}
