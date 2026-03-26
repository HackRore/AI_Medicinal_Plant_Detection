import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.api.v1.symptoms import symptom_search

async def test_direct():
    payload = {"symptoms": "headache and fever for 2 days"}
    print("Testing symptom_search directly...")
    try:
        result = await symptom_search(payload)
        import json
        print("Success:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct())
