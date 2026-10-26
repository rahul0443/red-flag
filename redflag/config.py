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
