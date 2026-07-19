import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.getenv("QDRANT_PAYLOAD")
HEADERS = {
    "Content-Type": "application/json",
    "api-key": os.getenv("QDRANT_API")
}

Payload = {
  "filter": {
    "must": [
      {
        "key": "page",
        "match": {
          "value": 5
        }
      }
    ]
  },
  "limit": 10,
  "with_payload": True
}

print("Sending request to Qdrant...")
response = requests.post(URL, headers=HEADERS, json=Payload)

print("Status Code:", response.status_code)
print("Response Headers:", dict(response.headers))
try:
    print("Response JSON:\n", json.dumps(response.json(), indent=2))
except Exception:
    print("Response Content:\n", response.text)
