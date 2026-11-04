"""Offline lookalike checks on a hostname: no network, deterministic, cannot be fooled by page content."""
import ipaddress
import re
import unicodedata

from redflag.tools.official import BRANDS, _root

# Platforms where anyone can publish a page under the platform's own registrable domain: the domain's age says nothing about the page.
FREE_HOSTS = ("vercel.app", "netlify.app", "github.io", "gitlab.io", "pages.dev", "workers.dev", "web.app", "firebaseapp.com", "herokuapp.com",
              "blogspot.com", "wordpress.com", "wixsite.com", "weebly.com", "glitch.me", "repl.co", "replit.app", "onrender.com", "fly.dev",
              "surge.sh", "000webhostapp.com", "azurewebsites.net", "godaddysites.com", "framer.website", "carrd.co", "webflow.io", "notion.site",
              "myshopify.com", "ngrok.io", "ngrok-free.app", "trycloudflare.com", "duckdns.org", "ddns.net", "weebly.com", "square.site")


def free_host(host: str) -> str | None:
    h = (host or "").lower().strip(".")
    return next((f for f in FREE_HOSTS if h.endswith("." + f)), None)


SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rb.gy", "shorturl.at", "t.ly", "buff.ly", "rebrand.ly"}


def _skeleton(label: str) -> str:
    """Fold common lookalike characters (digits for letters) so 'paypa1' compares equal to 'paypal'."""
    return label.translate(str.maketrans({"0": "o", "1": "l", "3": "e", "5": "s", "4": "a", "7": "t", "8": "b"})).replace("rn", "m").replace("vv", "w")


def domain_signals(host: str) -> list[str]:
    host = (host or "").lower().strip(".")
    out: list[str] = []
    if not host:
        return out
    try:
        ipaddress.ip_address(host)
        return ["host is a raw IP address, not a company domain"]
    except ValueError:
        pass
    if re.fullmatch(r"(0x[0-9a-f]+|\d+)", host):
        out.append("host is a numeric address in disguise")
    if "xn--" in host:
        out.append("internationalised (punycode) domain: can imitate a brand with look-alike letters")
    if any(ord(c) > 127 for c in host):
        scripts = {unicodedata.name(c, "?").split()[0] for c in host if c.isalpha()}
        if len(scripts) > 1:
            out.append("domain mixes alphabets (e.g. Latin and Cyrillic), a classic look-alike trick")
    root = _root(host)
    fh = free_host(host)
    if fh:
        out.append(f"the page is hosted on a free site-builder ({fh}), not on the company's own domain")
    if root in SHORTENERS:
        out.append("link shortener: hides the real destination")
    if host.count(".") >= 4:
        out.append("unusually many subdomains")
    official = {d for b in BRANDS.values() for d in b["domains"]}
    if root not in official:
        label = root.split(".")[0]
        first, tokens = _skeleton(label), re.split(r"[-_]", label)
        for d in official:
            name = d.split(".")[0]
            if root != d and ((len(name) >= 5 and (name in first or _skeleton(name) in first)) or (len(name) >= 3 and name in tokens)):
                out.append(f"domain imitates '{d}' but is not it")
                break
        else:
            sub = host[: -len(root)] if host.endswith(root) else host
            for d in official:
                if len(d.split(".")[0]) >= 5 and d in sub:
                    out.append(f"'{d}' appears as a subdomain of an unrelated site ({root})")
                    break
    return out
