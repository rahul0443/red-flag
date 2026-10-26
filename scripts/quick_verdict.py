"""Usage: python scripts/quick_verdict.py samples/usps_smish.txt   (or pipe text via stdin)"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from redflag.verdict import analyze  # noqa: E402

text = Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else sys.stdin.read()
print(json.dumps(analyze(text), indent=2))
