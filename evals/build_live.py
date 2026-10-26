"""Builds the 'live phishing' paired set from a snapshot of the OpenPhish community feed.
Each live phishing URL (scam) is paired with the SAME message template using the brand's real URL (legit).
Stored defanged (hxxp) so nobody clicks it from the repo; the runner refangs at run time.
Source: OpenPhish community feed (https://openphish.com), snapshot taken at build time."""
import json
import random
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
feed = [u.strip() for u in open(sys.argv[1]) if u.strip().startswith("http")]

BRANDS = {  # keyword in URL -> (display name, real URL for the legit twin)
    "bankofamerica": ("Bank of America", "https://www.bankofamerica.com/online-banking/"),
    "netflix": ("Netflix", "https://www.netflix.com/account"),
    "adobe": ("Adobe", "https://account.adobe.com/"),
    "facebook": ("Facebook", "https://www.facebook.com/settings"),
    "xfinity": ("Xfinity", "https://www.xfinity.com/mobile/account"),
    "xflnlty": ("Xfinity", "https://www.xfinity.com/mobile/account"),
    "xfinnity": ("Xfinity", "https://www.xfinity.com/mobile/account"),
    "icloud": ("Apple iCloud", "https://www.icloud.com/find"),
    "coinbase": ("Coinbase", "https://www.coinbase.com/settings"),
    "dhl": ("DHL", "https://www.dhl.com/us-en/home/tracking.html"),
    "ticket-att": ("AT&T", "https://www.att.com/my/"),
    "roblox": ("Roblox", "https://www.roblox.com/home"),
    "steam": ("Steam", "https://steamcommunity.com/my/"),
    "metamask": ("MetaMask", "https://docs.metamask.io/"),
    "microsoft": ("Microsoft", "https://account.microsoft.com/"),
    "amazon": ("Amazon", "https://www.amazon.com/gp/css/order-history"),
}
TEMPLATES = [
    "{b}: We noticed a new sign-in to your account. You can review it here: {u}",
    "{b}: Your account statement is ready to view: {u}",
    "Hi, a quick note from {b} support about your account. Please take a look when you have a moment: {u}",
    "{b} notice: a document was shared with you. Open it here: {u}",
]
rnd = random.Random(26)
seen, picks = set(), []
for u in feed:
    host = urlparse(u).hostname or ""
    if host in seen:
        continue
    for kw, (name, real) in BRANDS.items():
        if kw in u.lower():
            # skip the generic 'metamask-docs-*.vercel.app' dupes after the first two and any 'clone' hobby sites
            if "clone" in u.lower():
                break
            seen.add(host)
            picks.append((name, real, u))
            break
rnd.shuffle(picks)
picks = picks[:30]
rows = []
for i, (name, real, u) in enumerate(picks):
    t = TEMPLATES[i % len(TEMPLATES)]
    defang = lambda s: re.sub(r"^http", "hxxp", s)
    rows.append({"label": "scam", "category": f"live_phish_{name}", "text": t.format(b=name, u=defang(u)), "pair": i})
    rows.append({"label": "legit", "category": f"live_twin_{name}", "text": t.format(b=name, u=real), "pair": i})
with open(ROOT / "data/live_pairs.jsonl", "w") as f:
    for i, r in enumerate(rows):
        f.write(json.dumps({"id": f"live-{i:03d}", **r}) + "\n")
print(len(picks), "pairs;", "brands:", sorted({p[0] for p in picks}))
