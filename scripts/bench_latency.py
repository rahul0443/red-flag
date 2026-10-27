"""Time-to-verdict on a fixed sample. Usage: PREFETCH=1 REASONING_EFFORT=low python scripts/bench_latency.py [n]"""
import json, os, statistics, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DISABLE_TOOLS", "inspect_link_sandbox")
from redflag.agent.loop import investigate

rows = []
for s in ("benchmark", "hard_text", "live_pairs"):
    rows += [json.loads(l) for l in open(f"evals/data/{s}.jsonl")]
n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
rows = rows[::max(1, len(rows) // n)][:n]

def one(r):
    t = time.time(); first = None; v = None; calls = 0
    for e in investigate(r["text"].replace("hxxp", "http")):
        if first is None and e["type"] in ("tool_result", "thought"): first = time.time() - t
        if e["type"] == "verdict": v = e; break
    return time.time() - t, first or 0, (v or {}).get("verdict"), r["label"], (v or {}).get("usage", {}).get("llm_calls", 0)

with ThreadPoolExecutor(3) as ex: out = list(ex.map(one, rows))
tt = [o[0] for o in out]
correct = sum((o[2] in ("Scam", "Suspicious")) == (o[3] == "scam") for o in out)
print(f"PREFETCH={os.getenv('PREFETCH','1')} EFFORT={os.getenv('REASONING_EFFORT','medium')} n={len(out)} median={statistics.median(tt):.1f}s p90={sorted(tt)[int(.9*len(tt))-1]:.1f}s mean_llm_calls={statistics.mean(o[4] for o in out):.2f} correct={correct}/{len(out)}")
