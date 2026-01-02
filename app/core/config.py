from __future__ import annotations

import os
from dotenv import load_dotenv

# Load .env once when this module is imported
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. "
        "Create a .env file or export it in the environment."
    )
