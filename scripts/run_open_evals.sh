#!/bin/zsh
# Agent on open-weight Muse Spark Open (Baseten). Same sets and tools as run_all_evals.sh.
cd "$(dirname "$0")/.."
export DISABLE_TOOLS=inspect_link_sandbox AGENT_BACKEND=open EVAL_TAG=open
for s in benchmark hard_text live_pairs uci_holdout; do
  .venv/bin/python evals/run_eval.py --set $s --mode agent > evals/results/$s.agent_open.log 2>&1
done
echo OPENDONE > evals/results/OPENDONE
