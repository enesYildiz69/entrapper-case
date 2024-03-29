import requests
import json

# The URL of the GraphQL endpoint
url = 'https://ranking.glassdollar.com/graphql'

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://ranking.glassdollar.com',
    'Referer': 'https://ranking.glassdollar.com/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
}

payload = {
    "operationName": "TopRankedCorporates",
    "variables": {},
    "query": "query TopRankedCorporates {\n  topRankedCorporates {\n    id\n    name\n    logo_url\n    industry\n    hq_city\n    startup_partners {\n      company_name\n      logo_url: logo\n      __typename\n    }\n    startup_friendly_badge\n    __typename\n  }\n}\n"
}

# Making the POST request to the GraphQL endpoint
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    file_path = 'data.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Content saved to {file_path}")
else:
    print(f"Failed to fetch data, status code: {response.status_code}")
