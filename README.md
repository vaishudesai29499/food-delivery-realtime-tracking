# Real-Time Food Delivery Driver Tracking

A runnable real-time driver tracking demo built using **Python, FastAPI, WebSockets, Redis Pub/Sub, and simulated GPS coordinates**.

The project demonstrates how a food delivery application can receive driver GPS updates, process and store the latest location, and stream real-time location events to customers. 

## Project Overview

This project implements a basic real-time tracking workflow:

- Drivers send GPS coordinates to the backend through an HTTP API.
- Pydantic validates incoming location data and timestamps.
- FastAPI handles authentication and order authorization.
- Redis atomically stores the latest driver location using sequence numbers.
- Redis Pub/Sub broadcasts accepted location updates.
- Customers connect through WebSockets to receive an initial location snapshot and subsequent live updates.
- A lightweight HTML customer interface displays incoming GPS updates.
- A Python simulator generates sample driver movements for testing.

> **Note:** This is a local testing and demonstration project, not a production-ready delivery platform. Authentication, persistence, event delivery, and frontend functionality have been intentionally simplified.

## Architecture

```text
                 Driver GPS Simulator
                         |
                         | HTTP POST
                         v
                FastAPI Location API
                         |
                         v
                Authentication &
                Order Authorization
                         |
                         v
                  Pydantic Validation
                         |
                         v
                Redis Latest Location
                  (Atomic Hash + TTL)
                         |
                         v
                   Redis Pub/Sub
                         |
                         v
                  FastAPI WebSocket
                         |
                         v
                Authorized Customer
                         |
                         v
               Customer HTML Interface
```

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| API Validation | Pydantic |
| Real-time Communication | WebSockets |
| Location Storage | Redis |
| Event Broadcasting | Redis Pub/Sub |
| HTTP Client | HTTPX |
| Containerization | Docker, Docker Compose |
| Customer Interface | HTML, CSS, JavaScript |
| Testing | Pytest |

## Project Structure

```text
food-delivery-realtime-tracking/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── security.py
│   ├── redis_store.py
│   │
│   └── core/
│       └── config.py
│
├── scripts/
│   └── simulate_driver.py
│
├── tests/
│   └── test_schemas.py
│
├── docker/
│   └── Dockerfile
│
├── customer.html
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

Before running the project, make sure you have:

- Python 3.12 or newer
- Docker
- Docker Compose
- Git (optional)

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd food-delivery-realtime-tracking
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```

### 4. Start FastAPI and Redis

From the project root, execute:

```bash
docker compose up --build
```

This starts:

- FastAPI backend
- Redis server

The API will be available at:

```text
http://localhost:8000
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Project information and demo credentials |
| `/health` | GET | API and Redis health check |
| `/docs` | GET | Interactive Swagger API documentation |
| `/api/v1/orders/{order_id}/location` | POST | Receive driver GPS updates |
| `/ws/orders/{order_id}/tracking` | WebSocket | Stream customer tracking updates |

### Health Check

Open:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "redis": "connected"
}
```

## Running the GPS Simulator

Open a second terminal in the project directory.

Activate your virtual environment:

```bash
source .venv/bin/activate
```

Run the simulator:

```bash
python scripts/simulate_driver.py
```

The simulator sends five sample GPS updates to the backend at approximately two-second intervals.

Example response:

```text
202 {"status":"accepted","sequence":1}
202 {"status":"accepted","sequence":2}
202 {"status":"accepted","sequence":3}
202 {"status":"accepted","sequence":4}
202 {"status":"accepted","sequence":5}
```

Each accepted response indicates that the backend has processed the location update and stored the latest location in Redis.

## Demo Credentials

The project uses predefined demo credentials.

| Credential | Value |
|---|---|
| Demo Order ID | `order-1` |
| Driver Token | `driver-demo-token` |
| Customer Token | `customer-demo-token` |

These credentials are intended only for local testing.

## Customer Live Tracking Interface

The project includes a lightweight HTML-based customer interface that connects to the FastAPI WebSocket endpoint and displays real-time driver GPS updates.

### Features

- Establishes a WebSocket connection with the tracking API.
- Receives live driver location events.
- Displays latitude, longitude, timestamp, and sequence information.
- Shows connection and disconnection status.
- Displays incoming GPS updates without requiring a separate frontend framework.

### How to Run

1. Start the backend and Redis using:

   ```bash
   docker compose up --build
   ```

2. Open `customer.html` in your web browser.

3. Click **Connect Customer**.

4. Open another terminal, activate your Python virtual environment, and run:

   ```bash
   python scripts/simulate_driver.py
   ```

5. Observe incoming driver location updates in the browser.

**Note:** This is a lightweight demonstration interface. It displays location data as JSON; it does not yet include a map visualization.

## WebSocket Communication

Customers connect to the following WebSocket endpoint:

```text
ws://localhost:8000/ws/orders/order-1/tracking?token=customer-demo-token
```

The WebSocket connection provides:

- An initial location snapshot when available.
- Live location updates published through Redis Pub/Sub.

### Example WebSocket Message

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

The latitude and longitude values represent sample GPS coordinates. The simulator generates the actual updates used during testing.

## Testing the HTTP API Manually

You can also send a location update using `curl`.

```bash
curl -X POST \
  http://localhost:8000/api/v1/orders/order-1/location \
  -H 'Authorization: Bearer driver-demo-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "latitude": 18.5204,
    "longitude": 73.8567,
    "accuracy_meters": 10,
    "timestamp": "CURRENT_UTC_TIMESTAMP",
    "sequence": 1
  }'
```

Replace `CURRENT_UTC_TIMESTAMP` with the current UTC timestamp in ISO 8601 format.

**Important:** Location timestamps older than 30 seconds are rejected by the demo validation logic. The timestamp must also be in the expected format.

## Running Tests

Install the development dependencies:

```bash
python -m pip install -e '.[dev]'
```

Run the tests:

```bash
pytest
```

## How the Tracking Flow Works

1. The driver simulator generates GPS coordinates.
2. The simulator sends an HTTP POST request to the FastAPI location endpoint.
3. FastAPI authenticates the driver and validates the location payload.
4. Redis atomically checks the sequence number and updates the latest location.
5. Redis Pub/Sub publishes the accepted location event.
6. The customer's WebSocket connection receives the event.
7. The customer interface displays the updated GPS information.

Redis also stores the latest location temporarily using a configurable TTL. The demo uses a 30-second location TTL.

## Known Demo Limitations

This project demonstrates the core backend tracking workflow, but several production concerns are intentionally outside its current scope:

- Authentication uses fixed demo tokens. Replace them with real JWT verification.
- Authorization uses one seeded demo order and driver.
- PostgreSQL persistence is not implemented in this starter.
- Redis Pub/Sub is not durable. Reconnecting customers can retrieve the latest Redis snapshot, but missed intermediate events are not replayed.
- The WebSocket snapshot/subscription race requires sequence-based reconciliation in a production implementation.
- There is no rate limiter or production monitoring and metrics setup.
- TLS termination and production deployment configuration are not included.
- The customer frontend is a basic HTML interface. Map visualization, route rendering, and a moving driver marker are not implemented.

## Future Improvements

Possible extensions for this project include:

- Integrate PostgreSQL for persistent order and driver information.
- Implement JWT-based authentication and database-backed authorization.
- Add a real-time map using Google Maps or Leaflet.
- Display a moving driver marker on the customer map.
- Implement route visualization and estimated arrival time.
- Add Redis Streams or a durable message broker for event replay.
- Add location update rate limiting.
- Introduce monitoring, logging, and performance metrics.
- Add automated integration and load tests.
- Deploy the application using Docker on AWS or another cloud platform.

## Learning Objectives

This project is useful for understanding:

- Real-time communication using FastAPI WebSockets.
- Redis Pub/Sub and in-memory location storage.
- Atomic Redis operations and sequence-number validation.
- HTTP-based GPS ingestion.
- Asynchronous backend processing.
- Customer subscriptions to live location events.
- Docker-based local development.

## License

This project is intended for learning, experimentation, and portfolio demonstration. Add an appropriate open-source license if you intend to distribute it publicly.
