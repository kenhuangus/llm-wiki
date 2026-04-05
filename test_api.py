import requests
import json

def test_api():
    url = "http://localhost:8000/api/search"
    payload = {"query": "security"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing {url} with query: {payload['query']}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Search Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error connecting to API: {e}")

if __name__ == "__main__":
    test_api()
