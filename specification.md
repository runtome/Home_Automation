# Home Automation System

## Software Requirement Specification (SRS)

**Version:** 1.0  
**Purpose:** AI Coding Specification (Claude Code / Codex / ChatGPT / Cursor / Gemini CLI)

---

# 1. Project Information

## Project Name

**Home Automation Platform**

## Project Goal

Develop a scalable IoT Home Automation Platform capable of controlling multiple ESP8266 relay devices through a centralized cloud server.

The platform shall provide:

- User authentication
- Device management
- Real-time relay control
- Live device status
- Automation scheduling
- Event logging
- Secure remote access
- Responsive Web Dashboard
- REST API
- MQTT communication

The architecture must support future expansion including ESP32, sensors, AI automation, and mobile applications.

---

# 2. Overall Architecture

```text
                      Internet
                           |
                    HTTPS / MQTT
                           |
                     NGINX Reverse Proxy
                           |
        +------------------+------------------+
        |                                     |
     React Frontend                    FastAPI Backend
                                              |
                                    MQTT Service Layer
                                              |
                                     Mosquitto Broker
                                              |
                                        PostgreSQL
                                              |
                                           WiFi Router
                                              |
              +---------------+--------------+--------------+
              |               |              |              |
         ESP8266 #1      ESP8266 #2     ESP8266 #N
           Relay             Relay          Relay
```

---

# 3. Functional Requirements

## User Management

Features:

- Register account
- Login
- Logout
- JWT Authentication
- Refresh Token
- Password Hashing

Roles:

```text
Administrator
User
Guest (future)
```

## Device Management

Each ESP8266 represents one device.

Each device has:

```text
Device ID
Device Name
Room
Relay Status
Online Status
IP Address
Firmware Version
Last Seen
RSSI
MAC Address
```

Administrator can:

- Add device
- Remove device
- Rename device
- Move room
- Restart device (future)

## Relay Control

Each relay supports:

```text
Turn ON
Turn OFF
Toggle
Read Status
```

All actions must update:

- MQTT
- Database
- Dashboard

## Device Monitoring

Every device shall publish:

```text
Online
Offline
Relay Status
Heartbeat
Firmware Version
Signal Strength
```

Heartbeat interval:

```text
30 seconds
```

If heartbeat timeout exceeds:

```text
90 seconds
```

Server marks device Offline.

## Automation

Automation types:

```text
Time Schedule
Sensor Trigger
Manual Scene
Future AI Rule
```

Example:

```text
Every day
18:00
Turn ON Living Room Light
```

## Activity Logs

Every action shall be logged.

Examples:

```text
User Login
Relay ON
Relay OFF
Device Connected
Device Disconnected
Automation Triggered
```

---

# 4. Non-functional Requirements

## Performance

Dashboard update:

```text
< 1 second
```

MQTT latency:

```text
< 200 ms
```

API Response:

```text
< 500 ms
```

## Scalability

Minimum:

```text
100 ESP8266 Devices
```

Future:

```text
1000 Devices
```

## Availability

Backend:

```text
24/7
```

Reconnect automatically:

- MQTT
- WiFi

---

# 5. Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js |
| UI | TailwindCSS |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| MQTT | Eclipse Mosquitto |
| Authentication | JWT |
| Container | Docker |
| Reverse Proxy | NGINX |
| HTTPS | Let's Encrypt |
| Firmware | Arduino IDE |
| MCU | ESP8266 |

---

# 6. Folder Structure

```text
home-automation/
    backend/
    frontend/
    firmware/
    docker/
    nginx/
    docs/
    scripts/
    database/
    mqtt/
    tests/
```

## Backend Structure

```text
backend/
    app/
        api/
        auth/
        models/
        schemas/
        mqtt/
        automation/
        websocket/
        database/
        services/
        utils/
        config/
        main.py
```

## Frontend Structure

```text
frontend/
    src/
        pages/
        components/
        layouts/
        hooks/
        services/
        contexts/
        types/
        utils/
```

## Firmware Structure

```text
firmware/
    esp8266/
        config.h
        wifi.cpp
        mqtt.cpp
        relay.cpp
        heartbeat.cpp
        main.ino
```

---

# 7. MQTT Specification

Topic naming:

```text
home/{device_id}/set
home/{device_id}/status
home/{device_id}/heartbeat
home/{device_id}/register
home/{device_id}/info
```

Example:

```text
home/light001/set
```

Payload:

```json
{
  "command": "ON"
}
```

Status:

```json
{
  "status": "ON",
  "timestamp": "2026-07-01T10:30:00"
}
```

Heartbeat:

```json
{
  "online": true,
  "rssi": -45
}
```

---

# 8. REST API

Authentication:

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

Devices:

```text
GET /devices
GET /devices/{id}
POST /devices
PUT /devices/{id}
DELETE /devices/{id}
```

Relay:

```text
POST /devices/{id}/on
POST /devices/{id}/off
POST /devices/{id}/toggle
```

Automation:

```text
GET /automations
POST /automations
PUT /automations/{id}
DELETE /automations/{id}
```

Logs:

```text
GET /logs
```

Health:

```text
GET /health
```

---

# 9. Database Schema

## users

```text
id
username
email
password_hash
role
created_at
updated_at
```

## devices

```text
id
device_id
device_name
room
status
online
ip_address
mac_address
firmware
last_seen
created_at
```

## automations

```text
id
device_id
action
schedule
enabled
created_at
```

## logs

```text
id
user_id
device_id
action
message
created_at
```

---

# 10. Web Dashboard

Pages:

```text
Login
Dashboard
Devices
Automation
Logs
Settings
Profile
```

Dashboard Widgets:

```text
Online Devices
Offline Devices
Relay Status
Automation Count
Recent Activities
System Health
```

Device Card:

```text
Living Room
Online
Relay
ON
[ ON ]
[ OFF ]
```

---

# 11. Security

Authentication:

```text
JWT
```

Password:

```text
BCrypt
```

HTTPS:

```text
TLS
```

MQTT:

```text
Username
Password
TLS
```

API:

```text
Rate Limit
Input Validation
CORS
CSRF Protection
```

---

# 12. Docker Services

```text
frontend
backend
postgres
mosquitto
nginx
```

Docker Compose:

```text
docker-compose.yml
```

---

# 13. Future Features

- OTA Firmware Update
- ESP32 Support
- Motion Sensor
- Temperature Sensor
- Power Monitoring
- AI Automation
- Voice Assistant
- Google Home
- Alexa
- Mobile App
- Push Notification
- Multi-user Access
- Multi-home Support

---

# 14. Coding Standards

## Backend

- Python 3.12+
- FastAPI best practices
- Pydantic v2
- SQLAlchemy 2.x
- Async APIs where appropriate
- Type hints for all functions
- Structured logging
- Unit and integration tests

## Frontend

- TypeScript only
- React functional components
- TailwindCSS
- React Query for server state
- WebSocket client for real-time updates

## Firmware

- C++17 (Arduino framework)
- Modular classes (WiFi, MQTT, Relay)
- Automatic WiFi/MQTT reconnection
- Configuration via header file or captive portal (future)
- Non-blocking code: avoid `delay()` where possible

---

# 15. AI Coding Instructions

Use the following as a system prompt for AI coding assistants:

> **Project Goal:** Build a production-quality IoT Home Automation Platform using FastAPI, Next.js, PostgreSQL, Mosquitto MQTT, Docker, and ESP8266 firmware. The architecture must be modular, scalable, and maintainable.
>
> **Requirements:**
>
> - Follow Clean Architecture principles.
> - Use repository and service layers in the backend.
> - Use SQLAlchemy ORM with Alembic for migrations.
> - Use JWT authentication with refresh tokens.
> - Implement MQTT publish/subscribe through a dedicated service.
> - Push real-time updates to the frontend using WebSockets.
> - Separate configuration, business logic, API routes, and data models.
> - Write clean, documented, strongly typed code with meaningful names.
> - Create Dockerfiles and a `docker-compose.yml` for local deployment.
> - Ensure each module is independently testable.
> - Design the system so that adding new device types such as switches, sensors, dimmers, and ESP32 nodes requires minimal changes.
> - Generate code incrementally by feature: authentication, devices, MQTT, dashboard, automation, and logs.

This specification is intentionally detailed and structured so that AI coding tools such as ChatGPT, Claude Code, Cursor, GitHub Copilot, and Gemini can use it as a blueprint to generate consistent, production-ready code across the entire project.

---

# 16. Recommended Professional Software Design Package

Since this is a university capstone, the project should also include a professional software design package of approximately 80 to 150 pages, similar to what software companies use before development.

It should include:

## 16.1 Software Requirement Specification (IEEE 29148)

- Complete functional requirements
- Complete non-functional requirements
- User roles and permissions
- Use cases
- Acceptance criteria
- System constraints

## 16.2 System Architecture Document

- High-level architecture
- Component diagrams
- Deployment diagrams
- Sequence diagrams

## 16.3 Database Design

- ER Diagram
- Table definitions
- Relationships
- Indexing strategy
- Migration strategy

## 16.4 MQTT Protocol Specification

- Topic hierarchy
- Payload formats
- QoS strategy
- Last Will and Testament
- Retained messages policy
- Security strategy

## 16.5 REST API Specification

- OpenAPI/Swagger compatible endpoints
- Request examples
- Response examples
- Error codes
- Authentication and authorization rules

## 16.6 ESP8266 Firmware Design

- State machine
- Class diagrams
- Memory layout
- Reconnection flow
- MQTT handling
- Relay control logic

## 16.7 Frontend Design

- UI wireframes
- Page specifications
- Component hierarchy
- State management
- Real-time update flow

## 16.8 Automation Engine

- Rule engine
- Scheduler
- Event processing
- Trigger conditions
- Action execution

## 16.9 Security Design

- JWT authentication
- HTTPS
- MQTT security
- Role-based access control
- Password policy
- Rate limiting

## 16.10 Docker & Deployment

- Docker Compose
- Production deployment
- Reverse proxy
- SSL certificates
- Environment variables
- Backup strategy

## 16.11 Development Roadmap

- Sprint planning
- Milestones
- Feature phases
- Risk management

## 16.12 Coding Standards

- Python
- TypeScript
- C++ for ESP8266
- Formatting
- Naming conventions
- Testing expectations

## 16.13 AI Coding Guide

- Optimized prompts for ChatGPT
- Optimized prompts for Claude Code
- Optimized prompts for Cursor
- Optimized prompts for GitHub Copilot
- Optimized prompts for Gemini
- Feature-by-feature implementation plan

## 16.14 Testing Plan

- Unit tests
- Integration tests
- Hardware tests
- Load testing
- Security testing
- User acceptance testing

## 16.15 Future Expansion

- ESP32 support
- Energy monitoring
- OTA updates
- AI automation
- Voice assistants
- Mobile app

This design package would become the master design document for the project, allowing AI coding assistants to generate the system consistently while also serving as strong documentation for a capstone report and portfolio.
