import requests
import json

url = "https://google.serper.dev/scholar"

payload = json.dumps({
  "q": "transformer",
  "hl": "en",
  "as_sdt": "0,5",
  "as_vis": "1"
})

headers = {
  'X-API-KEY': '769aed5f5ca7b1ad747d71b57224eb53135d0069',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

with open('google_scholar_response.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)
