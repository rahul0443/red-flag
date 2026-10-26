#!/bin/zsh
# Reproduces every number in the README. ~30 min, roughly $3-5 of API credits.
# The link sandbox is disabled in evals (slow, and would open live phishing pages 100+ times).
cd "$(dirname "$0")/.."
export DISABLE_TOOLS=inspect_link_sandbox
PY=.venv/bin/python
$PY evals/build_sets.py
for s in benchmark hard_text live_pairs uci_holdout uci_sample; do
  for m in baseline agent; do $PY evals/run_eval.py --set $s --mode $m > evals/results/$s.$m.log 2>&1; done
done
# Ablation: agent without the phishing-feed check (live_pairs labels come from the same feed)
for s in live_pairs hard_text; do
  DISABLE_TOOLS=inspect_link_sandbox,check_blocklists EVAL_TAG=noblocklist $PY evals/run_eval.py --set $s --mode agent > evals/results/$s.agent_noblocklist.log 2>&1
done
echo ALLDONE > evals/results/ALLDONE
