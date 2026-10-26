"""Usage: python evals/run_eval.py --set benchmark --mode agent [--limit 10] [--workers 4]
Positive = flagged (verdict Scam or Suspicious). 'strict' counts only Scam as positive."""
import argparse
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))

from redflag.agent.loop import investigate  # noqa: E402
from redflag.verdict import analyze  # noqa: E402


def run_one(row, mode):
    t0 = time.time()
    row = {**row, "text": row["text"].replace("hxxp", "http")}  # refang defanged phishing URLs
    try:
        if mode == "agent":
            v = next((e for e in investigate(row["text"]) if e["type"] == "verdict"), None)
            if v is None:
                raise RuntimeError("no verdict")
            out = {"verdict": v["verdict"], "confidence": v.get("confidence"), "usage": v.get("usage", {}),
                   "summary": v.get("summary")}
        else:
            v = analyze(row["text"])
            out = {"verdict": v["verdict"], "confidence": v.get("confidence"), "usage": {}}
    except Exception as e:
        out = {"verdict": "ERROR", "error": f"{type(e).__name__}: {e}"[:200], "usage": {}}
    out["seconds"] = round(time.time() - t0, 1)
    return {**row, **out}


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(max(0, c - h), 3), round(min(1, c + h), 3)]


def metrics(results, strict=False):
    ok = [r for r in results if r["verdict"] != "ERROR"]
    flag = (lambda r: r["verdict"] == "Scam") if strict else (lambda r: r["verdict"] in ("Scam", "Suspicious"))
    tp = sum(1 for r in ok if r["label"] == "scam" and flag(r))
    fn = sum(1 for r in ok if r["label"] == "scam" and not flag(r))
    fp = sum(1 for r in ok if r["label"] == "legit" and flag(r))
    tn = sum(1 for r in ok if r["label"] == "legit" and not flag(r))
    div = lambda a, b: round(a / b, 3) if b else None
    prec, rec = div(tp, tp + fp), div(tp, tp + fn)
    return {"n": len(ok), "errors": len(results) - len(ok), "accuracy": div(tp + tn, len(ok)), "precision": prec,
            "recall": rec, "false_positive_rate": div(fp, fp + tn),
            "recall_95ci": wilson(tp, tp + fn), "fpr_95ci": wilson(fp, fp + tn),
            "f1": round(2 * prec * rec / (prec + rec), 3) if prec and rec else None,
            "confusion": {"tp": tp, "fn": fn, "fp": fp, "tn": tn}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="benchmark")
    ap.add_argument("--mode", choices=["agent", "baseline"], default="agent")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(ROOT / "data" / f"{a.set}.jsonl")]
    if a.limit:  # interleave so a small limit still has both classes
        s, l = [r for r in rows if r["label"] == "scam"], [r for r in rows if r["label"] == "legit"]
        rows = [x for pair in zip(s, l) for x in pair][: a.limit]
    with ThreadPoolExecutor(a.workers) as ex:
        results = list(ex.map(lambda r: run_one(r, a.mode), rows))
    secs = [r["seconds"] for r in results if r["verdict"] != "ERROR"]
    toks = [r["usage"].get("prompt_tokens", 0) + r["usage"].get("completion_tokens", 0) for r in results]
    summary = {"set": a.set, "mode": a.mode, "model": (lambda c: c.OPEN_MODEL if c.AGENT_BACKEND == "open" and a.mode == "agent" else c.MODEL)(__import__("redflag.config", fromlist=["x"])),
               "lenient": metrics(results), "strict": metrics(results, strict=True),
               "median_seconds": statistics.median(secs) if secs else None,
               "avg_tokens": round(sum(toks) / len(toks)) if toks else None,
               "avg_tool_calls": round(statistics.mean(r["usage"].get("tool_calls", 0) for r in results), 2) if a.mode == "agent" else 0}
    outdir = ROOT / "results"
    outdir.mkdir(exist_ok=True)
    tag = os.getenv("EVAL_TAG", "")
    name = f"{a.set}_{a.mode}{('_' + tag) if tag else ''}" + (f"_n{a.limit}" if a.limit else "")
    (outdir / f"{name}.json").write_text(json.dumps({"summary": summary, "results": results}, indent=1))
    print(json.dumps(summary, indent=1))
    wrong = [r for r in results if r["verdict"] == "ERROR" or (r["verdict"] in ("Scam", "Suspicious")) != (r["label"] == "scam")]
    for r in wrong:
        print(f"MISS [{r['label']}->{r['verdict']}] {r['id']} {r['category']}: {r['text'][:90]!r} {r.get('error','')}")


if __name__ == "__main__":
    main()
