# Home Automation Platform

A scalable IoT home automation platform for controlling ESP8266 relay devices through a
centralized cloud server. See [specification.md](specification.md) for the full SRS and
[docs/README.md](docs/README.md) for architecture notes.

This build pass implements the **backend foundation + a minimal frontend dashboard +
ESP8266 firmware**: JWT auth, device management, relay control, an MQTT service layer,
live WebSocket updates, activity logs, a Next.js dashboard, and real device firmware
(`firmware/esp8266/`, see firmware/README.md to flash a physical device). Automation
scheduling and other items in specification.md section 13 are deferred to future passes
(see docs/README.md).

## Quick start (Docker)

```bash
cp .env.example .env          # edit secrets/passwords as needed
./scripts/gen-mqtt-password.sh    # generates mqtt/passwd (requires Docker)
docker compose up --build
```

- Dashboard: http://localhost/
- API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost/api/health

Create the first admin user (device management requires the admin role):

```bash
docker compose exec backend python /app/../scripts/create_admin.py admin admin@example.com Passw0rd!
```

Simulate a fake ESP8266 device (no hardware required):

```bash
pip install paho-mqtt
MQTT_USERNAME=ha_backend MQTT_PASSWORD=<from .env> python scripts/simulate_device.py light001
```

To flash a real ESP8266, see [firmware/README.md](firmware/README.md).

## Local development

Backend (Python 3.12+):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
alembic upgrade head          # requires DATABASE_URL pointing at a running Postgres
uvicorn app.main:app --reload
pytest                        # runs against an isolated sqlite test database
```

Frontend (Node 20+):

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## Project layout

See [specification.md section 6](specification.md#6-folder-structure) for the full folder
structure rationale, and [docs/README.md](docs/README.md) for the MQTT topic spec and
architecture summary.
