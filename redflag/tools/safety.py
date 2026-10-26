"""Network safety: Red Flag only ever sends requests to public internet hosts,
and never sends user content to a URL found in a message."""
import ipaddress
import socket
from urllib.parse import urlparse


def is_public_host(host: str) -> bool:
    """Block localhost, private ranges, link-local and metadata IPs (SSRF guard)."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            return False
    return True


def safe_url(url: str) -> str | None:
    """Return an error string if the URL must not be fetched, else None."""
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        return "only http/https URLs are allowed"
    try:
        socket.getaddrinfo(p.hostname, None)
    except socket.gaierror:
        return "domain does not resolve in DNS (taken down, never existed, or a typo-squat not yet live)"
    if not is_public_host(p.hostname):
        return "host resolves to a private/internal address; refusing to connect"
    return None
