import urllib.request
import json

def chat(customer_id, message, memory_mode="with_memory"):
    url = "http://127.0.0.1:8000/api/v1/chat"
    data = {
        "customer_id": customer_id,
        "session_id": "test-session",
        "message": message,
        "memory_mode": memory_mode
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode())
    except Exception as e:
        print("Error:", e)
        if hasattr(e, 'read'):
            print(e.read().decode())
        return None

# Test isolation
print("\n--- Interaction A (Customer 1) ---")
resA = chat("cust-001", "My payment failed.")
print("Customer 1 Recalled:", len(resA.get("memories_recalled", [])))

print("\n--- Interaction B (Customer 2) ---")
resB = chat("cust-002", "My payment failed.")
print("Customer 2 Recalled:", len(resB.get("memories_recalled", [])))
