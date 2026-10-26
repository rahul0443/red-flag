"""Central settings, loaded from .env. Keys never leave the backend."""
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MODEL_API_KEY", "")
BASE_URL = os.getenv("META_BASE_URL", "https://api.meta.ai/v1")
MODEL = os.getenv("META_MODEL", "muse-spark-1.3")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "800"))
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "8"))
