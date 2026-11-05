import asyncio
from contextlib import asynccontextmanager
from datetime import timezone

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Header
from redis.asyncio import Redis

from app.core.config import settings
from app.schemas import LocationUpdate
from app.security import authenticate_driver, authenticate_customer, authorize_demo_order, ws_authenticate
from app.redis_store import LocationStore

redis: Redis | None = None
store: LocationStore | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis, store
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    store = LocationStore(redis)
    try:
        await redis.ping()
        yield
    finally:
        await redis.aclose()

app = FastAPI(title="Real-Time Food Delivery Tracking", version="1.0.0", lifespan=lifespan)

def get_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    return parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else None

@app.get("/health")
async def health():
    try:
        await redis.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="redis unavailable")

@app.post("/api/v1/orders/{order_id}/location", status_code=202)
async def update_location(order_id: str, payload: LocationUpdate, authorization: str | None = Header(default=None)):
    token = get_bearer_token(authorization)
    driver_id = authenticate_driver(token)
    assigned_driver = authorize_demo_order(order_id)
    if driver_id != assigned_driver:
        raise HTTPException(status_code=403, detail="driver not assigned to order")
    location = payload.model_dump()
    location["timestamp"] = payload.timestamp.astimezone(timezone.utc).isoformat()
    accepted = await store.update(driver_id, order_id, location)
    if not accepted:
        raise HTTPException(status_code=409, detail="duplicate or out-of-order sequence")
    return {"status": "accepted", "sequence": payload.sequence}

@app.websocket("/ws/orders/{order_id}/tracking")
async def track_order(websocket: WebSocket, order_id: str):
    customer_id = await ws_authenticate(websocket)
    if customer_id is None:
        return
    try:
        driver_id = authorize_demo_order(order_id, customer_id)
    except HTTPException:
        await websocket.close(code=1008, reason="not authorized")
        return

    await websocket.accept()
    pubsub = redis.pubsub()
    channel = store.channel(driver_id)
    try:
        # Subscribe before snapshot so updates during snapshot retrieval are buffered.
        await pubsub.subscribe(channel)
        latest = await store.get_latest(driver_id)
        if latest:
            await websocket.send_json({"type": "location_snapshot", "order_id": order_id, "data": latest})

        # This compact demo streams events. For production, compare event sequence
        # against snapshot sequence and buffer/reconcile to close the snapshot race.
        async for message in pubsub.listen():
            if message.get("type") != "message":
                continue
            try:
                event = __import__("json").loads(message["data"])
                if event.get("order_id") == order_id:
                    await websocket.send_json(event)
            except (ValueError, TypeError):
                continue
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
        except Exception:
            pass

@app.get("/")
async def root():
    return {
        "name": "Real-Time Food Delivery Tracking",
        "docs": "/docs",
        "demo": {
            "driver_token": settings.demo_driver_token,
            "customer_token": settings.demo_customer_token,
            "order_id": settings.demo_order_id,
        },
    }
