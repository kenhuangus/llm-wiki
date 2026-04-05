import requests
import json

def test_ingest():
    url = "http://localhost:8000/api/ingest"
    payload = {"urls": ["https://blog.trailofbits.com/feed/"], "domain": "security"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing {url} with ingest payload: {payload}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Ingest Queueing Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error connecting to API: {e}")

if __name__ == "__main__":
    test_ingest()
