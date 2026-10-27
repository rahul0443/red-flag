#!/bin/zsh
# Prompt-injection robustness: baseline, agent on Muse Spark, agent on Muse Spark Open.
cd "$(dirname "$0")/.."
export DISABLE_TOOLS=inspect_link_sandbox
.venv/bin/python evals/injection_src.py
.venv/bin/python evals/run_eval.py --set injection --mode baseline > evals/results/injection.baseline.log 2>&1
.venv/bin/python evals/run_eval.py --set injection --mode agent > evals/results/injection.agent.log 2>&1
AGENT_BACKEND=open EVAL_TAG=open .venv/bin/python evals/run_eval.py --set injection --mode agent > evals/results/injection.agent_open.log 2>&1
echo INJDONE > evals/results/INJDONE
