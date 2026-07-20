import requests
import json

url = "https://rag-retrieval-api-640900979202.asia-south1.run.app/search"

payload = {
    "collection": "rag_guest-all",
    "query": "who is ilaya ?",
    "limit": 3
}

response = requests.post(url, json=payload)

print(response.status_code)
print(json.dumps(response.json(), indent=4))






















# import requests
# import json
# from dotenv import load_dotenv
# import os

# load_dotenv()

# URL = os.getenv("QDRANT_PAYLOAD")
# HEADERS = {
#     "Content-Type": "application/json",
#     "api-key": os.getenv("QDRANT_API")
# }

# Payload = {
#   "filter": {
#     "must": [
#       {
#         "key": "page",
#         "match": {
#           "value": 5
#         }
#       }
#     ]
#   },
#   "limit": 10,
#   "with_payload": True
# }

# print("Sending request to Qdrant...")
# response = requests.post(URL, headers=HEADERS, json=Payload)

# print("Status Code:", response.status_code)
# print("Response Headers:", dict(response.headers))
# try:
#     print("Response JSON:\n", json.dumps(response.json(), indent=2))
# except Exception:
#     print("Response Content:\n", response.text)
