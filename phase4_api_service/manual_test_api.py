import json
import httpx
import time
import subprocess
import os

print("Starting FastAPI server in the background...")
server_process = subprocess.Popen(
    ["uvicorn", "phase4_api_service.main:app", "--port", "8005"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for the server to load the dataset
print("Waiting for dataset to load (this takes ~15-20 seconds)...")
time.sleep(20)

client = httpx.Client(base_url="http://127.0.0.1:8005")

def check_health():
    try:
        res = client.get("/health")
        print(f"Health Check: {res.json()}")
        return res.json().get("db_connected", False)
    except Exception as e:
        print(f"Health Check failed: {e}")
        return False

if not check_health():
    print("giving it 10 more seconds...")
    time.sleep(10)
    check_health()

print("\n" + "="*50)
print("SCENARIO 1: Budget Cafe in Indiranagar")
payload1 = {
    "location": "Indiranagar",
    "cuisine": "Cafe",
    "max_price": 500
}
res1 = client.post("/recommend", json=payload1, timeout=30.0)
data1 = res1.json()
print(f"Matched Restaurants: {data1.get('restaurant_count')}")
print(f"API Response:\n{data1.get('recommendation_text')}")


print("\n" + "="*50)
print("SCENARIO 2: Date Night Italian (Premium, high rating)")
payload2 = {
    "cuisine": "Italian",
    "max_price": 2500,
    "min_rating": 4.5
}
res2 = client.post("/recommend", json=payload2, timeout=30.0)
data2 = res2.json()
print(f"Matched Restaurants: {data2.get('restaurant_count')}")
print(f"API Response:\n{data2.get('recommendation_text')}")


print("\n" + "="*50)
print("SCENARIO 3: Junk search (No results expected)")
payload3 = {
    "location": "Jupiter",
    "cuisine": "Plutonian",
}
res3 = client.post("/recommend", json=payload3, timeout=30.0)
data3 = res3.json()
print(f"Matched Restaurants: {data3.get('restaurant_count')}")
print(f"API Response:\n{data3.get('recommendation_text')}")

print("\nShutting down the server...")
server_process.terminate()
