# firmware/esp8266

ESP8266 relay device firmware implementing specification.md chapter 6: a non-blocking
state machine (`BOOT -> WIFI_CONNECT -> MQTT_CONNECT -> REGISTER -> OPERATIONAL`, with any
transient failure routing through a single `RECONNECT` state with bounded exponential
backoff), MQTT Last Will for fast disconnect detection, a 30s heartbeat, and relay command
handling over the topics defined in specification.md section 7.

## Module layout

| File | Responsibility |
| --- | --- |
| `config.h` | Compile-time device id, Wi-Fi/broker credentials, pins, intervals, topics. |
| `wifi.h` / `wifi.cpp` | `WifiManager`: non-blocking Wi-Fi connect/reconnect. |
| `mqtt.h` / `mqtt.cpp` | `MqttClient`: broker connection with Last Will, subscribe/publish. |
| `relay.h` / `relay.cpp` | `Relay`: GPIO on/off/toggle, active-low support. |
| `heartbeat.h` / `heartbeat.cpp` | `Heartbeat`: builds the `{"online","rssi"}` payload. |
| `main.ino` | `setup()`/`loop()`: wires the modules together and drives the state machine. |

## Before flashing

1. Edit `config.h`: set `DEVICE_ID`, `WIFI_SSID`/`WIFI_PASS`, `BROKER_HOST`, and
   `MQTT_USER`/`MQTT_PASS` for this device.
2. Register this device's MQTT credentials with the broker (each physical device should
   have its own username/password, distinct from the backend's own `MQTT_USERNAME`):
   ```bash
   ./scripts/gen-mqtt-password.sh light001 <device-password>
   ```
3. Create the matching `Device` row via the API/dashboard (admin only) with
   `device_id` = `DEVICE_ID` from step 1, *before* powering on the device — the MQTT
   handlers on the backend look up the device by `device_id` and silently ignore
   messages from unknown devices (see `backend/app/mqtt/handlers.py`).

## Building with the Arduino IDE (per specification.md section 5)

1. Install the **ESP8266 board package** (Boards Manager URL:
   `https://arduino.esp8266.com/stable/package_esp8266com_index.json`), then select an
   ESP-12E/NodeMCU 1.0 board.
2. Install libraries via Library Manager:
   - **PubSubClient** by Nick O'Leary (v2.8+)
   - **ArduinoJson** by Benoit Blanchon (v6.x)
3. Open `main.ino` (the IDE will pick up the other `.h`/`.cpp` files in the same folder
   automatically) and upload.

## Building with PlatformIO (optional, used to verify this firmware compiles)

```ini
; platformio.ini
[env:esp12e]
platform = espressif8266
board = esp12e
framework = arduino
lib_deps =
    knolleary/PubSubClient@^2.8
    bblanchon/ArduinoJson@^6.21.5
```

```bash
pio run          # compile
pio run -t upload -t monitor
```

This firmware was compile-verified with the above configuration: ~28.8 KB RAM (35%) and
~284 KB flash (27%) on an ESP-12E target, within the budget in specification.md 6.8.2.

## Wiring

`RELAY_PIN` defaults to GPIO5 (D1 on NodeMCU). Most inexpensive 1-channel relay boards are
**active-low** (`RELAY_ACTIVE_LOW = 1`); flip it to `0` for active-high modules.

## Design notes / deviations worth knowing about

- **Last Will target**: the LWT is published on `home/{device_id}/heartbeat` with
  `{"online": false, "rssi": 0}` rather than a bespoke availability topic, so the backend's
  existing heartbeat handler detects an ungraceful disconnect immediately instead of
  waiting out the ~90s offline-watchdog timeout.
- **No retained messages**: status/heartbeat/register are published without the MQTT
  retain flag. The backend tracks presence in its own database (`online`, `last_seen`)
  rather than relying on broker-retained state, so this keeps the retain/LWT interaction
  simple and avoids stale retained messages confusing new subscribers.
- **No wall-clock timestamp**: `status` messages omit `timestamp` (the backend schema
  treats it as optional) rather than pulling in NTP/RTC dependencies just for a field the
  backend doesn't currently use.
- **TLS**: `BROKER_PORT` defaults to 1883 (plain MQTT) per the constrained-RAM guidance in
  specification.md 6.8 (TLS handshake peak heap use is significant on this MCU); switch to
  8883 with a `WiFiClientSecure` in `mqtt.cpp` if the device crosses an untrusted network.
- **OTA, captive-portal provisioning**: not implemented in this pass (specification.md
  section 13 "Future Features").
