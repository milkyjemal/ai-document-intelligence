import os

# Force mock LLM for all pytest runs
os.environ["USE_MOCK_LLM"] = "1"
