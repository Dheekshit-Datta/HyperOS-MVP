import requests
import json

try:
    print("Testing HyperOS Agent Core (Mistral)...")
    response = requests.post(
        "http://127.0.0.1:8000/execute",
        json={"command": "Check if any chrome window is open and list elements"},
        timeout=60
    )
    print("Response Status:", response.status_code)
    print("Response Content:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Test Error:", e)
