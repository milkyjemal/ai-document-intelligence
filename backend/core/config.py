import os
from dotenv import load_dotenv

# Load .env once when this module is imported
load_dotenv()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# ---- LLM config ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "1") == "1"


# ---- Job / async config ----
JOB_TTL_SECONDS = _int_env("JOB_TTL_SECONDS", 60)
