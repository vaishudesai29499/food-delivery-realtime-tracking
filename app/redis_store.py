import json
from datetime import datetime, timezone
from redis.asyncio import Redis

from app.core.config import settings

# Atomic sequence check + latest-location write. Pub/Sub is intentionally separate:
# the latest snapshot remains recoverable even if a subscriber misses an event.
SAVE_SCRIPT = """
local current = redis.call('HGET', KEYS[1], 'sequence')
if current and tonumber(ARGV[1]) <= tonumber(current) then
  return 0
end
redis.call('HSET', KEYS[1],
  'latitude', ARGV[2],
  'longitude', ARGV[3],
  'accuracy_meters', ARGV[4],
  'timestamp', ARGV[5],
  'sequence', ARGV[1],
  'order_id', ARGV[6])
redis.call('EXPIRE', KEYS[1], ARGV[7])
return 1
"""

class LocationStore:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.save_script = redis.register_script(SAVE_SCRIPT)

    @staticmethod
    def key(driver_id: str) -> str:
        return f"driver:{driver_id}:location"

    @staticmethod
    def channel(driver_id: str) -> str:
        return f"driver:{driver_id}:location_updates"

    async def save(self, driver_id: str, order_id: str, location: dict) -> bool:
        accepted = await self.save_script(
            keys=[self.key(driver_id)],
            args=[
                location["sequence"], location["latitude"], location["longitude"],
                location["accuracy_meters"], location["timestamp"], order_id,
                settings.location_ttl_seconds,
            ],
        )
        return bool(accepted)

    async def get_latest(self, driver_id: str):
        data = await self.redis.hgetall(self.key(driver_id))
        return data or None

    async def publish(self, driver_id: str, order_id: str, location: dict):
        event = {"type": "location_update", "order_id": order_id, "data": location}
        await self.redis.publish(self.channel(driver_id), json.dumps(event))

    async def update(self, driver_id: str, order_id: str, location: dict):
        accepted = await self.save(driver_id, order_id, location)
        if not accepted:
            return False
        await self.publish(driver_id, order_id, location)
        return True
