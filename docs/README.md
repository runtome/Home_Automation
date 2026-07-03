# docs/

Brief architecture notes for this build pass. The full 80-150 page IEEE 29148-style design
package described in specification.md section 16 is out of scope here.

## Architecture

See specification.md section 2 for the full diagram. In this pass:

- **backend/** — FastAPI app: JWT auth, device CRUD, relay control, activity logs, an MQTT
  service layer (subscribes to device status/heartbeat/register/info, publishes relay
  commands), and a WebSocket endpoint that pushes live device updates to the dashboard.
- **frontend/** — Next.js dashboard: login, device grid with online/offline + relay status,
  recent activity feed. Updates in real time via WebSocket, patched into the React Query cache.
- **mqtt/** — Mosquitto broker config (username/password auth).
- **nginx/** — reverse proxy: `/api/*` → backend, `/ws/*` → backend (websocket upgrade), `/` → frontend.

## MQTT topics (spec section 7)

```
home/{device_id}/set        {"command": "ON"|"OFF"|"TOGGLE"}   (backend -> device)
home/{device_id}/status     {"status": "ON"|"OFF", "timestamp": iso8601}
home/{device_id}/heartbeat  {"online": true, "rssi": -45}
home/{device_id}/register   {"mac_address", "ip_address", "firmware"}
home/{device_id}/info       {"firmware", "ip_address", "mac_address"}
```

## Deferred to future passes

Automation scheduling engine, ESP8266 firmware, OTA updates, sensors, AI automation, mobile
app, HTTPS/Let's Encrypt, full CSRF/rate-limiting middleware, multi-user/multi-home support.
