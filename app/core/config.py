import os
from dotenv import load_dotenv

# Load .env once when this module is imported
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "1") == "1"
