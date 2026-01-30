"""
Configuration file
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Mistral API Key (NOT Anthropic)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "your-mistral-api-key-here")

# Settings
MAX_STEPS = 50
SCREENSHOT_INTERVAL = 1.5  # seconds
