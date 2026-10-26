"""Builds JSONL eval sets: the hand-written benchmark and a seeded sample of the UCI SMS Spam Collection (CC BY 4.0).
Citation: Almeida & Hidalgo (2011), SMS Spam Collection, UCI ML Repository, doi:10.24432/C5CC84"""
import json
import random
from pathlib import Path

from benchmark_src import LEGIT, SCAM
from hard_src import HARD_LEGIT, HARD_SCAM

ROOT = Path(__file__).parent
OUT = ROOT / "data"


def write(name, rows):
    with open(OUT / name, "w") as f:
        for i, r in enumerate(rows):
            f.write(json.dumps({"id": f"{name.split('.')[0]}-{i:03d}", **r}) + "\n")
    print(name, len(rows), "rows")


bench = [{"label": "scam", "category": c, "text": t} for c, t in SCAM] + \
        [{"label": "legit", "category": c, "text": t} for c, t in LEGIT]
write("benchmark.jsonl", bench)

rows = [l.rstrip("\n").split("\t", 1) for l in open(OUT / "raw/uci/SMSSpamCollection", encoding="utf-8", errors="replace")]
spam = [t for lab, t in rows if lab == "spam" and 60 <= len(t) <= 320]
ham = [t for lab, t in rows if lab == "ham" and 25 <= len(t) <= 200]
rnd = random.Random(2026)
sample = [{"label": "scam", "category": "uci_spam", "text": t} for t in rnd.sample(spam, 40)] + \
         [{"label": "legit", "category": "uci_ham", "text": t} for t in rnd.sample(ham, 40)]
write("uci_sample.jsonl", sample)

hard = [{"label": "scam", "category": c, "text": t} for c, t in HARD_SCAM] + \
       [{"label": "legit", "category": c, "text": t} for c, t in HARD_LEGIT]
write("hard_text.jsonl", hard)

# Held-out UCI sample: different seed, no overlap with the dev sample used while tuning the agent prompt.
used = {r["text"] for r in sample}
rnd2 = random.Random(99)
holdout = [{"label": "scam", "category": "uci_spam", "text": t} for t in rnd2.sample([t for t in spam if t not in used], 50)] + \
          [{"label": "legit", "category": "uci_ham", "text": t} for t in rnd2.sample([t for t in ham if t not in used], 50)]
write("uci_holdout.jsonl", holdout)
