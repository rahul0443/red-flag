"""Offline analysis of the email addresses in a message: who is really writing, and where are you told to reply.
No network, no model: it only reads the text it is given, so page or message content cannot talk it out of a finding."""
import re

from redflag.tools.official import BRANDS, _root
from redflag.tools.safety import host_of
from redflag.tools.signals import domain_signals

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
FREE_MAIL = {"gmail.com", "googlemail.com", "yahoo.com", "ymail.com", "outlook.com", "hotmail.com", "live.com", "msn.com", "aol.com",
             "icloud.com", "me.com", "proton.me", "protonmail.com", "mail.com", "gmx.com", "gmx.net", "yandex.com", "zoho.com", "qq.com", "163.com"}
ORG_WORDS = ("unicef", "united nations", "red cross", "university", "department of", "government", "police", "court", "bureau", "agency",
             "administration", "ministry", "embassy", "bank", "insurance", "human resources", "recruit", "career opportunity")


def check_sender(text: str) -> dict:
    text = str(text or "")[:6000]
    emails = []
    for m in EMAIL.findall(text):
        if m.lower() not in emails:
            emails.append(m.lower())
    emails = emails[:5]
    if not emails:
        return {"emails": [], "signals": [], "note": "no email address in the message"}
    low = text.lower()
    named = [k for k in BRANDS if re.search(rf"(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])", low)]
    org_named = bool(named) or any(w in low for w in ORG_WORDS)
    sender_line = next((l for l in text.splitlines() if re.match(r"\s*(sender|from)\s*:", l, re.I)), "")
    senders = EMAIL.findall(sender_line) or emails[:1]
    sender = senders[0].lower()
    s_root = _root(sender.split("@", 1)[1])
    signals = []
    if s_root in FREE_MAIL and org_named:
        signals.append(f"an organisation or official body is named, but the sender writes from a free mailbox ({s_root})")
    for b in named:
        domains = BRANDS[b]["domains"]
        if s_root not in domains and s_root not in FREE_MAIL and not any(s_root.endswith("." + d) for d in domains):
            signals.append(f"the message names {b}, but the sender's domain ({s_root}) is not one of its official domains ({', '.join(domains)})")
            break
    signals += [f"sender domain: {x}" for x in domain_signals(s_root)]
    others = [e for e in emails if e != sender]
    for e in others:
        e_root = _root(e.split("@", 1)[1])
        if e_root in FREE_MAIL and e_root != s_root:
            signals.append(f"you are told to contact {e}, a free mailbox that differs from the sender's address")
            break
    return {"emails": emails, "sender": sender, "sender_domain": s_root, "free_mail_sender": s_root in FREE_MAIL, "signals": signals}
