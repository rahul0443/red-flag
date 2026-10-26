from datetime import datetime, timezone

import httpx


def _event(data: dict, action: str):
    for e in data.get("events", []):
        if e.get("eventAction") == action:
            return e.get("eventDate")


def rdap_lookup(domain: str) -> dict:
    domain = domain.lower().strip().removeprefix("www.")
    try:
        r = httpx.get(f"https://rdap.org/domain/{domain}", timeout=10, follow_redirects=True)
    except httpx.HTTPError as e:
        return {"domain": domain, "error": f"lookup failed: {type(e).__name__}"}
    if r.status_code == 404:
        return {"domain": domain, "error": "no registration record found (domain may not exist)"}
    if r.status_code != 200:
        return {"domain": domain, "error": f"RDAP returned HTTP {r.status_code}"}
    data = r.json()
    registered = _event(data, "registration")
    age_days = None
    if registered:
        dt = datetime.fromisoformat(registered.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - dt).days
    registrar = None
    for ent in data.get("entities", []):
        if "registrar" in ent.get("roles", []):
            for item in ent.get("vcardArray", [None, []])[1]:
                if item[0] == "fn":
                    registrar = item[3]
    return {"domain": domain, "registered": registered, "age_days": age_days,
            "registrar": registrar, "status": data.get("status", [])}
