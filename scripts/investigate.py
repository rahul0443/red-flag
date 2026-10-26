"""Usage: python scripts/investigate.py samples/usps_smish.txt"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from redflag.agent.loop import investigate  # noqa: E402

for ev in investigate(Path(sys.argv[1]).read_text()):
    print(json.dumps(ev, default=str)[:600])
