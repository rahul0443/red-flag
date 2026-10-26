# Red Flag

Forward any suspicious text, email, screenshot or voicemail and an AI agent investigates it like a fraud analyst, returning an evidence-backed scam verdict in seconds.

Built for the Meta Global AI Developer Hackathon (Indie track, "Build for Your World").

## Problem
_TODO_

## How it works
_TODO: agent loop (Muse Spark picks tools, reads results, repeats), tools, Glimmer triage._

## Architecture
_TODO diagram_

## Eval results
_TODO: accuracy, false-positive rate_

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add MODEL_API_KEY
python scripts/quick_verdict.py samples/usps_smish.txt
```

## Safety
Red Flag never replies to or contacts scammers, never sends user data to URLs found in messages, and opens links only in an isolated sandbox.

## Built during the hackathon
Everything in this repo (Oct 26 – Nov 4, 2026).
