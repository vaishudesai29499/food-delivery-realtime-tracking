# Real-Time Food Delivery Driver Tracking

A runnable starter demo using **FastAPI, WebSockets, Redis Pub/Sub, and simulated GPS**.

## What it demonstrates
- Driver sends GPS updates through HTTP.
- Pydantic validates coordinates and timestamps.
- Redis atomically stores the latest location using sequence numbers.
- Redis Pub/Sub broadcasts accepted updates.
- Customer connects through WebSocket and receives a location snapshot and live events.
- Demo token and order authorization are included.

> This is a local testing/demo project, not a production-ready delivery platform. Demo tokens are hard-coded defaults. Replace them with real JWT verification and database-backed order/assignment authorization before deployment. The WebSocket snapshot/event race and durable event delivery also need production-grade reconciliation.

## Requirements
- Python 3.12+
- Docker + Docker Compose (recommended)

## Run with Docker
```bash
docker compose up --build
```
API docs: http://localhost:8000/docs  
Health: http://localhost:8000/health

## Run the GPS simulator
In another terminal:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python scripts/simulate_driver.py
```

The demo order is `order-1`. Driver token: `driver-demo-token`. Customer token: `customer-demo-token`.

## WebSocket
Connect to:
```text
ws://localhost:8000/ws/orders/order-1/tracking?token=customer-demo-token
```
Example message:
```json
{
  "type": "location_update",
  "order_id": "order-1",
  "data": {
    "latitude": 18.5204,
    "longitude": 73.8567,
    "accuracy_meters": 10,
    "timestamp": "2026-10-26T12:00:00+00:00",
    "sequence": 1
  }
}
```

## HTTP request
```bash
curl -X POST http://localhost:8000/api/v1/orders/order-1/location \
  -H 'Authorization: Bearer driver-demo-token' \
  -H 'Content-Type: application/json' \
  -d '{"latitude":18.5204,"longitude":73.8567,"accuracy_meters":10,"timestamp":"2026-10-26T12:00:00Z","sequence":1}'
```

Use a current UTC timestamp when testing; timestamps older than 30 seconds are rejected.

## Tests
```bash
pip install -e '.[dev]'
pytest
```

## Architecture
```text
Driver GPS Simulator
  -> FastAPI location endpoint
  -> auth + order authorization
  -> atomic Redis latest-location Hash (TTL)
  -> Redis Pub/Sub channel
  -> FastAPI WebSocket
  -> authorized customer
```

## Known demo limitations
- Authentication uses fixed demo tokens.
- Authorization uses one seeded demo order and driver.
- No PostgreSQL persistence in this starter.
- Pub/Sub is not durable; reconnect retrieves the latest Redis snapshot.
- Snapshot/subscription race requires sequence reconciliation for production.
- No rate limiter, production metrics, TLS termination, or frontend map.
- Redis location TTL is configured to 30 seconds.
