#!/bin/zsh
# Agent with prefetch + low reasoning effort (the fast configuration) on every set, on both models.
cd "$(dirname "$0")/.."
export DISABLE_TOOLS=inspect_link_sandbox PREFETCH=1
TAG=${EVAL_TAG_FAST:-final}
for s in benchmark hard_text live_pairs uci_holdout injection; do
  EVAL_TAG=$TAG .venv/bin/python evals/run_eval.py --set $s --mode agent > evals/results/$s.agent_$TAG.log 2>&1
done
for s in benchmark hard_text live_pairs uci_holdout injection; do
  AGENT_BACKEND=open EVAL_TAG=${TAG}_open .venv/bin/python evals/run_eval.py --set $s --mode agent > evals/results/$s.agent_${TAG}_open.log 2>&1
done
echo FASTDONE > evals/results/FASTDONE
