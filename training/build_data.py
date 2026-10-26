"""Builds SFT data for the Muse Glimmer first-pass triage model.

Sources (all with clear rights):
  1. Hand-written template families (training/families.py, CC0) expanded with random slot fills.
  2. UCI SMS Spam Collection (CC BY 4.0, Almeida & Hidalgo 2011), EXCLUDING every message used in any eval set.
No Muse Spark outputs are used (API terms on output reuse are unclear).
Anything with high n-gram overlap with an eval message is dropped to prevent leakage.
"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from families import FAMILIES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
rnd = random.Random(1234)

CARRIERS = ["USPS", "FedEx", "UPS", "DHL", "Royal Mail", "Canada Post", "Amazon Logistics", "OnTrac"]
BANKS = ["Chase", "Wells Fargo", "Bank of America", "Citi", "Capital One", "US Bank", "PNC", "Truist", "TD Bank", "Navy Federal", "Regions", "Ally Bank"]
GOVS = ["IRS", "Social Security Administration", "Medicare", "Department of Justice", "FBI Cyber Division", "U.S. Treasury", "Customs and Border Protection", "Department of Veterans Affairs"]
SVCS = ["Apple ID", "Microsoft 365", "Google", "Netflix", "PayPal", "Amazon", "Facebook", "Instagram", "Spotify", "Dropbox", "Coinbase", "Outlook", "iCloud", "DocuSign", "LinkedIn", "Steam", "Roblox", "Adobe", "Xfinity", "AT&T"]
SVC_SAFE = ["Google", "Apple", "Microsoft", "Amazon", "PayPal", "Netflix", "Dropbox", "Uber", "Lyft", "Instagram", "Spotify", "Venmo"]
PAYS = ["Zelle", "Venmo", "Cash App", "PayPal", "Apple Cash"]
SOFTWARE = ["Norton", "McAfee", "Geek Squad", "Windows Defender", "Microsoft Support", "Avast", "LifeLock", "Best Buy Tech"]
COINS = ["Bitcoin", "Ethereum", "USDT", "BTC", "ETH"]
EXCH = ["Coinbase", "Binance", "Kraken", "Crypto.com", "MetaMask", "Trust Wallet"]
GIFTS = ["Apple gift cards", "Google Play cards", "Amazon gift cards", "Bitcoin", "prepaid cards", "Steam cards", "iTunes cards"]
STORES = ["Target", "Walmart", "Best Buy", "Costco", "Home Depot", "Starbucks", "Nike", "IKEA", "Lowe's", "Chipotle", "Macy's", "Sephora"]
UTILS = ["Duke Energy", "PG&E", "ConEd", "SRP", "FPL", "National Grid", "Xcel Energy", "Dominion Energy"]
TELCOS = ["Verizon", "T-Mobile", "AT&T", "Comcast", "Spectrum", "Cox"]
AIRLINES = ["Delta", "United", "American Airlines", "Southwest", "JetBlue", "Alaska Airlines"]
PHARMS = ["CVS Pharmacy", "Walgreens", "Rite Aid", "Walmart Pharmacy", "Costco Pharmacy"]
TOLLS = ["E-ZPass", "SunPass", "FasTrak", "TxTag", "I-Pass", "PikePass"]
NAMES = ["Sarah", "Mike", "Linda", "David", "Emma", "John", "Priya", "Carlos", "Anna", "Tom", "Grace", "Omar", "Mia", "Jake", "Elena"]
JOBS = ["US Army engineer", "oil rig engineer", "UN doctor", "marine officer", "offshore contractor"]
EVENTS = ["Sunrise", "Bright", "Evergreen", "Premier", "GreenPath"]
ROLES = ["remote data entry assistant", "personal assistant", "payment processing agent", "social media rater"]
LOTTERIES = ["Mega Millions International", "Euro Global", "Powerball Online", "UK National", "Microsoft"]
PRIZES = ["iPhone 15", "Samsung TV", "$500 Walmart voucher", "PlayStation 5", "Caribbean cruise"]
ITEMS = ["iPhone 15 Pro", "MacBook Air", "Sony 65-inch TV", "Rolex watch", "Dyson vacuum"]
SVC2 = ["Amazon", "PayPal", "Apple Store", "Best Buy", "Walmart", "eBay"]
MONTHS = ["September", "October", "November", "December"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Nov 3", "Nov 12", "Dec 1", "Oct 30"]
TIMES = ["9:00 AM", "10:30 AM", "noon", "2:30 PM", "4:15 PM", "6:00 PM", "7:30 PM"]
CITIES = ["Phoenix, AZ", "Austin, TX", "Denver, CO", "Chicago, IL", "Seattle, WA", "Miami, FL", "Boston, MA"]
BOOKS = ["The Remains of the Day", "Educated", "Project Hail Mary", "Where the Crawdads Sing"]
CHARITIES = ["American Red Cross", "Habitat for Humanity", "Feeding America", "UNICEF"]
PROPS = ["Cactus Ridge Apartments", "Oak Hill Residences", "Maple Court", "Lakeview Towers"]
SCHOOLS = ["Lincoln Elementary", "Desert View High", "Roosevelt Middle School", "St. Mary's Academy"]
CLINICS = ["Valley Family Medicine", "Smile Dental", "Happy Paws Vet", "Sunrise Pediatrics", "Mesa Eye Care"]
DRS = ["Dr. Patel", "Dr. Nguyen", "Dr. Garcia", "Dr. Okafor", "Dr. Kim"]
PETS = ["Buddy", "Luna", "Max", "Daisy"]
MEMOS = ["Pizza Friday", "rent split", "concert tickets", "groceries", "coffee", "gas"]
WORDS = ["secure", "verify", "help", "support", "login", "update", "account", "billing", "confirm", "alert", "pay", "refund", "track", "service"]
BADTLD = ["top", "xyz", "click", "info", "icu", "cfd", "sbs", "link", "support", "online", "site", "live", "cyou", "buzz", "shop", "co", "club"]
HANDLES = ["workfromhome_jobs", "hr_support_team", "mike_invest_pro", "claims_desk", "sunny.manager"]


def slug(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def badurl(brand):
    b = slug(brand)[:12]
    a, c = rnd.sample(WORDS, 2)
    host = rnd.choice([f"{b}-{a}.{rnd.choice(BADTLD)}", f"{b}{a}-{c}.{rnd.choice(BADTLD)}", f"{a}-{b}.{rnd.choice(BADTLD)}",
                       f"{b}.{a}-{c}.{rnd.choice(BADTLD)}", f"{b}-{a}{rnd.randint(10, 999)}.{rnd.choice(BADTLD)}"])
    path = rnd.choice(["", "/login", "/pay", "/verify", f"/id/{rnd.randint(1000, 99999)}", f"?ref={rnd.randint(100, 9999)}"])
    return rnd.choice(["", "http://", "https://"]) + host + path


def phone(scam=True):
    area = rnd.choice(["855", "888", "877", "866", "844", "800", "602", "480", "202", "310"])
    return rnd.choice([f"1-{area}-555-{rnd.randint(100, 199):04d}", f"{area}-555-{rnd.randint(100, 199):04d}", f"({area}) 555-{rnd.randint(100, 199):04d}"])


def fill(tpl):
    carrier, bank, svc = rnd.choice(CARRIERS), rnd.choice(BANKS), rnd.choice(SVCS)
    brand_for_url = rnd.choice([carrier, bank, svc]) if "{badurl}" in tpl else "x"
    for key in ("carrier", "bank", "svc"):
        pass
    gov = rnd.choice(GOVS)
    # pick the brand actually present in the template so the lookalike URL matches it
    if "{carrier}" in tpl:
        brand_for_url = carrier
    elif "{bank}" in tpl:
        brand_for_url = bank
    elif "{svc}" in tpl:
        brand_for_url = svc
    elif "{gov}" in tpl:
        brand_for_url = gov.split()[0]
    elif "{pay}" in tpl:
        brand_for_url = rnd.choice(PAYS)
    elif "{util}" in tpl:
        brand_for_url = rnd.choice(UTILS)
    elif "{svc2}" in tpl:
        brand_for_url = rnd.choice(SVC2)
    elif "{toll}" in tpl:
        brand_for_url = rnd.choice(TOLLS)
    slots = {
        "carrier": carrier, "bank": bank, "svc": svc, "gov": gov, "badurl": badurl(brand_for_url), "phone": phone(),
        "hrs": rnd.choice([1, 2, 6, 12, 24, 48]), "small": f"{rnd.choice([0.99, 1.49, 1.99, 2.45, 3.95, 4.30, 6.99])}",
        "small2": rnd.choice([50, 99, 100, 150, 199, 250, 300, 450]), "amt": f"{rnd.choice([212, 349, 480, 612, 849, 1149, 1299, 2400, 2847, 3800])}",
        "amt2": rnd.choice([450, 900, 1500, 2691]), "big": rnd.choice(["9,000", "48,200", "250,000", "750,000", "1.2 million", "20,000", "12,480"]),
        "num": rnd.randint(10000, 99999999), "last4": rnd.randint(1000, 9999), "code": rnd.randint(100000, 999999),
        "n": rnd.choice([2, 3, 5, 7, 12]), "pay": rnd.choice(PAYS), "software": rnd.choice(SOFTWARE), "coin": rnd.choice(COINS),
        "exch": rnd.choice(EXCH), "gift": rnd.choice(GIFTS), "store": rnd.choice(STORES), "util": rnd.choice(UTILS),
        "telco": rnd.choice(TELCOS), "airline": rnd.choice(AIRLINES), "pharm": rnd.choice(PHARMS), "toll": rnd.choice(TOLLS),
        "name": rnd.choice(NAMES), "name2": rnd.choice(NAMES), "job": rnd.choice(JOBS), "event": rnd.choice(EVENTS), "role": rnd.choice(ROLES),
        "lottery": rnd.choice(LOTTERIES), "prize": rnd.choice(PRIZES), "item": rnd.choice(ITEMS), "svc2": rnd.choice(SVC2),
        "month": rnd.choice(MONTHS), "day": rnd.choice(DAYS), "time": rnd.choice(TIMES), "city": rnd.choice(CITIES), "book": rnd.choice(BOOKS),
        "charity": rnd.choice(CHARITIES), "prop": rnd.choice(PROPS), "school": rnd.choice(SCHOOLS), "clinic": rnd.choice(CLINICS),
        "dr": rnd.choice(DRS), "pet": rnd.choice(PETS), "memo": rnd.choice(MEMOS), "handle": rnd.choice(HANDLES),
        "fnum": f"{rnd.choice(['DL', 'UA', 'AA', 'WN'])} {rnd.randint(100, 2999)}", "addr": f"{rnd.randint(100, 999)} Main St",
        "hotel": rnd.choice(["Hilton", "Marriott", "Hyatt", "Holiday Inn"]), "short": rnd.choice(["82277", "80608", "84199", "83383", "87121"]),
        "tones": rnd.choice([4, 6, 8]), "freeurl": rnd.choice(["www.tones4u.net", "www.winnerzone.tv", "www.funclub.co.uk", "www.moviequiz.tv"]),
    }
    for k in ("store", "util", "telco", "airline", "clinic", "charity", "svc"):
        slots[k + "_lc"] = slug(slots[k])
    slots["bank_lc"] = slug(slots["bank"])
    out = tpl
    for k, v in slots.items():
        out = out.replace("{" + k + "}", str(v))
    # legit templates that use {svc} should use consumer-brand names with real domains
    return out


def safe_fill(tpl):
    t = tpl.replace("{svc}", rnd.choice(SVC_SAFE))
    return fill(t)


def ngrams(text, n=5):
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(max(1, len(w) - n + 1))}


def overlap(a, b):
    return len(a & b) / max(1, min(len(a), len(b)))


# ---- eval texts to protect ----
eval_rows = []
for f in (ROOT / "evals/data").glob("*.jsonl"):
    eval_rows += [json.loads(l)["text"].replace("hxxp", "http") for l in open(f)]
eval_ng = [ngrams(t) for t in eval_rows]
eval_set = set(eval_rows)

SYSTEM = ("You are a fast first-pass scam triage model. Read the message and answer with ONLY a JSON object: "
          '{"verdict": "Scam" | "Suspicious" | "Looks Safe", "signals": [short signal names]}. '
          "Scam = clear fraud. Suspicious = risky or unverifiable ask. Looks Safe = ordinary or legitimate.")

examples, seen = [], set()
dropped_leak = 0


def add(text, verdict, signals, src, family):
    global dropped_leak
    text = " ".join(text.split())
    if text in seen or text in eval_set or len(text) < 8:
        return
    ng = ngrams(text)
    if any(overlap(ng, e) >= 0.5 for e in eval_ng if len(e) > 4 and len(ng) > 4):
        dropped_leak += 1
        return
    seen.add(text)
    examples.append({"text": text, "verdict": verdict, "signals": signals, "src": src, "family": family})


PER_FAMILY = {"Scam": 38, "Suspicious": 34, "Looks Safe": 30}
for fam, (verdict, signals, tpls) in FAMILIES.items():
    target = PER_FAMILY[verdict] * (2 if fam in ("l_chat", "l_receipt", "l_bank") else 1)
    tries = 0
    start = len([e for e in examples if e["family"] == fam])
    while len([e for e in examples if e["family"] == fam]) - start < target and tries < target * 12:
        tries += 1
        tpl = rnd.choice(tpls)
        add((safe_fill if verdict == "Looks Safe" else fill)(tpl), verdict, signals, "template", fam)

# ---- UCI (CC BY 4.0), minus anything in an eval set ----
uci = [l.rstrip("\n").split("\t", 1) for l in open(ROOT / "evals/data/raw/uci/SMSSpamCollection", encoding="utf-8", errors="replace")]
ham = [t for lab, t in uci if lab == "ham" and 12 <= len(t) <= 220]
spam = [t for lab, t in uci if lab == "spam" and 40 <= len(t) <= 320]
rnd.shuffle(ham)
rnd.shuffle(spam)
for t in ham[:450]:
    add(t, "Looks Safe", ["personal conversation", "no ask"], "uci", "uci_ham")
for t in spam[:170]:
    add(t, "Suspicious", ["unsolicited promotion", "premium-rate or prize bait"], "uci", "uci_spam")

rnd.shuffle(examples)
n_val = 150
val, train = examples[:n_val], examples[n_val:]


def to_chat(e):
    return {"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": e["text"]},
                         {"role": "assistant", "content": json.dumps({"verdict": e["verdict"], "signals": e["signals"]}), "weight": 1}]}


out = ROOT / "training/data"
out.mkdir(exist_ok=True)
for name, rows in (("train.jsonl", train), ("val.jsonl", val)):
    with open(out / name, "w") as f:
        for e in rows:
            f.write(json.dumps(to_chat(e)) + "\n")
with open(out / "meta_all.jsonl", "w") as f:
    for e in examples:
        f.write(json.dumps(e) + "\n")

from collections import Counter  # noqa: E402
print("total", len(examples), "train", len(train), "val", len(val), "dropped for eval overlap:", dropped_leak)
print("verdicts", Counter(e["verdict"] for e in examples))
print("sources", Counter(e["src"] for e in examples))
