"""Central settings, loaded from .env. Keys never leave the backend."""
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MODEL_API_KEY", "")
BASE_URL = os.getenv("META_BASE_URL", "https://api.meta.ai/v1")
MODEL = os.getenv("META_MODEL", "muse-spark-1.3")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "6000"))
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "8"))

# Open-weight path: Muse Glimmer 30B (Apache-2.0) served by a partner (NVIDIA NIM free endpoint by default).
GLIMMER_API_KEY = os.getenv("GLIMMER_API_KEY", "")
GLIMMER_BASE_URL = os.getenv("GLIMMER_BASE_URL", "https://integrate.api.nvidia.com/v1")
GLIMMER_MODEL = os.getenv("GLIMMER_MODEL", "meta/muse-glimmer-30b")
# AGENT_BACKEND=glimmer runs the whole investigation loop on the open-weight model instead of Muse Spark.
AGENT_BACKEND = os.getenv("AGENT_BACKEND", "spark")
