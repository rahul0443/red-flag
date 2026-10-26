"""Fine-tune Muse Glimmer 30B on Fireworks (SFT is free until 11/30) via the REST API.

Usage:
  python training/fireworks_sft.py check            # key works? account id? is the base model tunable?
  python training/fireworks_sft.py train            # upload datasets and start the job
  python training/fireworks_sft.py status           # poll the job
"""
import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("FIREWORKS_API_KEY", "")
API = "https://api.fireworks.ai/v1"
BASE_MODEL = "accounts/fireworks/models/muse-glimmer-30b"
DATA = Path(__file__).parent / "data"
STATE = Path(__file__).parent / "data/job_state.json"
H = {"Authorization": f"Bearer {KEY}"}


def die(msg):
    sys.exit(msg)


def account_id():
    r = httpx.get(f"{API}/accounts", headers=H, timeout=30)
    if r.status_code != 200:
        die(f"Could not list accounts (HTTP {r.status_code}): {r.text[:200]}")
    accts = r.json().get("accounts", [])
    if not accts:
        die("No Fireworks account found for this key.")
    return accts[0]["name"].split("/")[-1]


def check():
    acct = account_id()
    print("account:", acct)
    r = httpx.get(f"{API}/accounts/fireworks/models/muse-glimmer-30b", headers=H, timeout=30)
    print("base model HTTP", r.status_code)
    if r.status_code == 200:
        m = r.json()
        print({k: m.get(k) for k in ("name", "state", "tunable", "supportsLora", "contextLength", "kind")})


def upload(acct, dataset_id, path):
    n = sum(1 for _ in open(path))
    body = {"datasetId": dataset_id, "dataset": {"displayName": dataset_id, "exampleCount": str(n), "format": "CHAT"}}
    r = httpx.post(f"{API}/accounts/{acct}/datasets", headers=H, json=body, timeout=60)
    if r.status_code not in (200, 409):
        die(f"create dataset failed: {r.status_code} {r.text[:300]}")
    with open(path, "rb") as f:
        r = httpx.post(f"{API}/accounts/{acct}/datasets/{dataset_id}:upload", headers=H,
                       files={"file": (path.name, f, "application/jsonl")}, timeout=300)
    if r.status_code != 200:
        die(f"upload failed: {r.status_code} {r.text[:300]}")
    print("uploaded", dataset_id, n, "examples")


def train():
    acct = account_id()
    upload(acct, "redflag-triage-train", DATA / "train.jsonl")
    upload(acct, "redflag-triage-val", DATA / "val.jsonl")
    time.sleep(5)
    body = {"dataset": f"accounts/{acct}/datasets/redflag-triage-train",
            "evaluationDataset": f"accounts/{acct}/datasets/redflag-triage-val",
            "baseModel": BASE_MODEL, "outputModel": f"accounts/{acct}/models/redflag-triage-glimmer",
            "epochs": 3, "learningRate": 0.0001, "loraRank": 16, "maxContextLength": 2048,
            "displayName": "Red Flag triage (Muse Glimmer 30B)"}
    r = httpx.post(f"{API}/accounts/{acct}/supervisedFineTuningJobs", headers=H, json=body, timeout=60)
    if r.status_code != 200:
        die(f"create job failed: {r.status_code} {r.text[:500]}")
    job = r.json()
    STATE.write_text(json.dumps({"account": acct, "job": job["name"]}))
    print("job started:", job["name"], job.get("state"))


def status():
    st = json.loads(STATE.read_text())
    r = httpx.get(f"{API}/{st['job']}", headers=H, timeout=30)
    j = r.json()
    print(j.get("state"), j.get("jobProgress"), j.get("status"), j.get("estimatedCost"))


if __name__ == "__main__":
    if not KEY:
        die("FIREWORKS_API_KEY is empty. Add it to .env.")
    {"check": check, "train": train, "status": status}[sys.argv[1] if len(sys.argv) > 1 else "check"]()
