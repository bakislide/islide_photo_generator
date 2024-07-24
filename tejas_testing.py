import requests
import json

headers = {'content-type': 'application/json'}
url = 'http://127.0.0.1:8080/process-art'
data = {"url": "https://c19839app01p02.cloudiax.com:10443/GS_Warriors_Primary_BlackRobe_072423.png"}
r = requests.post(url, json=data, headers=headers)

print(r.text)
