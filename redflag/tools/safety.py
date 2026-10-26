"""Network safety: Red Flag only ever sends requests to public internet hosts,
and never sends user content to a URL found in a message."""
import ipaddress
import socket
from urllib.parse import ParseResult, urlparse

ALLOWED_PORTS = {None, 80, 443, 8080, 8443}


def parse(url: str) -> ParseResult | None:
    """urlparse that never raises: malformed URLs ('http://[abc', bad ports) come back as None."""
    try:
        p = urlparse(str(url).strip())
        p.port  # raises ValueError for non-numeric or out-of-range ports
        return p
    except (ValueError, UnicodeError, AttributeError):
        return None


def host_of(url: str) -> str:
    p = parse(url)
    return (p.hostname or "").lower() if p else ""


def is_public_host(host: str) -> bool:
    """Block localhost, private ranges, link-local and metadata IPs (SSRF guard)."""
    try:
        infos = socket.getaddrinfo(host, None)
    except (socket.gaierror, UnicodeError):
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            return False
    return True


def safe_url(url: str) -> str | None:
    """Return an error string if the URL must not be fetched, else None."""
    p = parse(url)
    if p is None or p.scheme not in ("http", "https") or not p.hostname:
        return "only well-formed http/https URLs are allowed"
    if p.port not in ALLOWED_PORTS:
        return f"port {p.port} is not a normal web port; refusing to connect"
    try:
        socket.getaddrinfo(p.hostname, None)
    except (socket.gaierror, UnicodeError):
        return "domain does not resolve in DNS (taken down, never existed, or a typo-squat not yet live)"
    if not is_public_host(p.hostname):
        return "host resolves to a private/internal address; refusing to connect"
    return None
