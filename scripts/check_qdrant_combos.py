import httpx
import json
import sys
import io

# Set encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://localhost:6333"
collection_name = "products"

def check_qdrant():
    with httpx.Client() as client:
        # Search for combo using scroll to get all points
        response = client.post(
            f"{base_url}/collections/{collection_name}/points/scroll",
            json={
                "limit": 100,
                "with_payload": True
            }
        )
        points = response.json()["result"]["points"]
        
        for p in points:
            payload = p.get("payload", {})
            name = payload.get("product_name", "")
            if "Combo" in name:
                print(f"--- {name} ---")
                print(payload.get("text", "NO TEXT"))
                print()

if __name__ == "__main__":
    check_qdrant()
