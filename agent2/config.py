import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL_ID = "mistral-large-latest"

SEVERITY_LEVELS = {
    "LOW": "Low Risk",
    "MODERATE": "Moderate Risk",
    "HIGH": "High Risk of Destabilization",
}

TEMPERATURE = 0.7
MAX_TOKENS = 4096
