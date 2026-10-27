#!/bin/zsh
# The final configuration on every set: Spark agent, open agent, and the no-blocklist ablation (sandbox off in evals).
cd "$(dirname "$0")/.."
export DISABLE_TOOLS=inspect_link_sandbox PREFETCH=1
for s in benchmark hard_text live_pairs uci_holdout injection; do
  EVAL_TAG=final .venv/bin/python evals/run_eval.py --set $s --mode agent > evals/results/$s.agent_final.log 2>&1
done
for s in benchmark hard_text live_pairs uci_holdout injection; do
  AGENT_BACKEND=open EVAL_TAG=final_open .venv/bin/python evals/run_eval.py --set $s --mode agent > evals/results/$s.agent_final_open.log 2>&1
done
for s in live_pairs hard_text; do
  DISABLE_TOOLS=inspect_link_sandbox,check_blocklists EVAL_TAG=noblocklist .venv/bin/python evals/run_eval.py --set $s --mode agent > evals/results/$s.agent_noblocklist.log 2>&1
done
echo OK > evals/results/FINALDONE
