"""Accuracy of the instant open-weight first look (what the UI shows ~2 s in): python scripts/eval_triage.py"""
import json, sys, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from redflag.open_model import triage

out = {}
for s in ("benchmark", "hard_text", "live_pairs", "uci_holdout", "injection"):
    rows = [json.loads(l) for l in open(ROOT / "evals/data" / f"{s}.jsonl")]
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda r: triage(r["text"].replace("hxxp", "http")), rows))
    flag = lambda v: v in ("Scam", "Suspicious")
    tp = sum(1 for r, x in zip(rows, res) if r["label"] == "scam" and flag(x.get("verdict")))
    fn = sum(1 for r, x in zip(rows, res) if r["label"] == "scam" and not flag(x.get("verdict")))
    fp = sum(1 for r, x in zip(rows, res) if r["label"] == "legit" and flag(x.get("verdict")))
    tn = sum(1 for r, x in zip(rows, res) if r["label"] == "legit" and not flag(x.get("verdict")))
    err = sum(1 for x in res if "error" in x)
    out[s] = {"tp": tp, "fn": fn, "fp": fp, "tn": tn, "errors": err, "median_ms": sorted(x.get("latency_ms", 0) for x in res)[len(res) // 2]}
    print(s, out[s])
(ROOT / "evals/results" / "triage.json").write_text(json.dumps(out, indent=1))
