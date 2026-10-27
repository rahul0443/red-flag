"""Central settings, loaded from .env. Keys never leave the backend."""
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MODEL_API_KEY", "")
BASE_URL = os.getenv("META_BASE_URL", "https://api.meta.ai/v1")
MODEL = os.getenv("META_MODEL", "muse-spark-1.3")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "6000"))
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "8"))

# Open-weight path: Muse Spark Open (open weights) served by Baseten, the hackathon partner.
BASETEN_API_KEY = os.getenv("BASETEN_API_KEY", "")
OPEN_BASE_URL = os.getenv("OPEN_BASE_URL", "https://inference.baseten.co/v1")
OPEN_MODEL = os.getenv("OPEN_MODEL", "meta-models/muse-spark-open-1026")
# AGENT_BACKEND=open runs the whole investigation loop on the open-weight model instead of Muse Spark.
AGENT_BACKEND = os.getenv("AGENT_BACKEND", "spark")
# Reasoning budget for the agent's model calls: minimal | low | medium | high (lower is faster)
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "low")            # closed Muse Spark with tool evidence in hand
OPEN_REASONING_EFFORT = os.getenv("OPEN_REASONING_EFFORT", "medium")  # the open model does worse at low (measured), so it keeps more
NO_EVIDENCE_EFFORT = os.getenv("NO_EVIDENCE_EFFORT", "medium")        # no link or brand to check: the model has only its own reading, so think more
TRIAGE_EFFORT = os.getenv("TRIAGE_EFFORT", "low")
PREFETCH = os.getenv("PREFETCH", "1") == "1"
