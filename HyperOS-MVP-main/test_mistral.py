import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"Key starts with: {api_key[:5]}...")

client = Mistral(api_key=api_key)
try:
    response = client.chat.complete(
        model="pixtral-12b-2409",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
    print("Mistral API test: Success")
except Exception as e:
    print(f"Mistral API test: Failed - {e}")
