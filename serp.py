import requests

try:
    r = requests.get("https://serpapi.com", timeout=5)
    print("Connected! Status code:", r.status_code)
except Exception as e:
    print("Cannot connect:", e)
