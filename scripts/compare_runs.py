"""Compare eval result files: python scripts/compare_runs.py agent agent_fast [agent_fast_open ...]"""
import json, statistics, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "evals" / "results"
tags = sys.argv[1:]
for s in ("benchmark", "hard_text", "live_pairs", "uci_holdout", "injection"):
    row = [s]
    for t in tags:
        f = R / f"{s}_{t}.json"
        if not f.exists(): row.append(f"{t}: -"); continue
        d = json.load(open(f)); res = d["results"]; L = d["summary"]["lenient"]; c = L["confusion"]
        sec = statistics.median(r["seconds"] for r in res)
        row.append(f"{t}: acc {L['accuracy']:.3f} fn {c['fn']} fp {c['fp']} err {L['errors']} med {sec:.0f}s")
    print(" | ".join(row))
