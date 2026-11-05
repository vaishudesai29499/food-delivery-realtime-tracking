import asyncio
from datetime import datetime, timezone
import httpx

BASE_URL = "http://localhost:8000"
TOKEN = "driver-demo-token"
ORDER_ID = "order-1"

# Example route near Pune. Replace with coordinates for your chosen demo route.
ROUTE = [
    (18.5204, 73.8567),
    (18.5210, 73.8572),
    (18.5217, 73.8578),
    (18.5223, 73.8584),
    (18.5230, 73.8590),
]

async def main():
    async with httpx.AsyncClient(timeout=10) as client:
        for sequence, (lat, lon) in enumerate(ROUTE, start=1):
            payload = {
                "latitude": lat,
                "longitude": lon,
                "accuracy_meters": 10.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sequence": sequence,
            }
            response = await client.post(
                f"{BASE_URL}/api/v1/orders/{ORDER_ID}/location",
                json=payload,
                headers={"Authorization": f"Bearer {TOKEN}"},
            )
            print(response.status_code, response.text)
            response.raise_for_status()
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
