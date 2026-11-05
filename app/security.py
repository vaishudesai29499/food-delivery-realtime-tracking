from fastapi import HTTPException, WebSocket

from app.core.config import settings

def authenticate_driver(token: str | None) -> str:
    if token != settings.demo_driver_token:
        raise HTTPException(status_code=401, detail="invalid driver token")
    return settings.demo_driver_id

def authenticate_customer(token: str | None) -> str:
    if token != settings.demo_customer_token:
        raise HTTPException(status_code=401, detail="invalid customer token")
    return settings.demo_customer_id

def authorize_demo_order(order_id: str, customer_id: str | None = None):
    # Demo assignment/ownership. Replace with PostgreSQL repositories in production.
    if order_id != settings.demo_order_id:
        raise HTTPException(status_code=404, detail="order not found")
    if customer_id and customer_id != settings.demo_customer_id:
        raise HTTPException(status_code=403, detail="not authorized for this order")
    return settings.demo_driver_id

async def ws_authenticate(websocket: WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if token != settings.demo_customer_token:
        await websocket.close(code=1008, reason="invalid token")
        return None
    return settings.demo_customer_id
