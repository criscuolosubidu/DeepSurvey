import arxiv
import json
from datetime import datetime


client = arxiv.Client()

search = arxiv.Search(
    query="deep learning",
    max_results=10
)

all_results = []
for r in client.results(search):
    result_dict = {}
    for k, v in r.__dict__.items():
        if isinstance(v, datetime):
            result_dict[k] = v.isoformat()
        else:
            try:
                result_dict[k] = json.dumps(v)
            except:
                result_dict[k] = str(v)
    all_results.append(result_dict)

with open("arxiv_data_response.json", "w") as f:
    json.dump(all_results, f, indent=4, ensure_ascii=False)
