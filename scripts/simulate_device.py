#!/usr/bin/env python3
"""Simulates an ESP8266 relay device over MQTT for end-to-end testing without
real hardware. Publishes a register message, heartbeats every 30s (spec
section 3), and replies to relay commands on home/{device_id}/set with a
status echo on home/{device_id}/status (spec section 7).

Usage:
    pip install paho-mqtt
    python scripts/simulate_device.py light001

Env vars (defaults match .env.example): MQTT_HOST, MQTT_PORT, MQTT_USERNAME,
MQTT_PASSWORD, HEARTBEAT_INTERVAL_SECONDS (default 30, lower for faster testing).
"""
import argparse
import json
import os
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "ha_backend")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "change_me")
HEARTBEAT_INTERVAL = float(os.environ.get("HEARTBEAT_INTERVAL_SECONDS", "30"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("device_id", help="e.g. light001")
    parser.add_argument("--rssi", type=int, default=-45)
    args = parser.parse_args()

    device_id = args.device_id
    set_topic = f"home/{device_id}/set"
    status_topic = f"home/{device_id}/status"
    heartbeat_topic = f"home/{device_id}/heartbeat"
    register_topic = f"home/{device_id}/register"

    state = {"status": "OFF"}

    def on_connect(client, userdata, flags, reason_code, properties=None):
        print(f"[{device_id}] connected to {MQTT_HOST}:{MQTT_PORT} (rc={reason_code})")
        client.subscribe(set_topic)
        client.publish(
            register_topic,
            json.dumps({"mac_address": "AA:BB:CC:DD:EE:FF", "ip_address": "192.168.1.50", "firmware": "1.0.0"}),
            qos=1,
        )
        print(f"[{device_id}] published register on {register_topic}")

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
        except json.JSONDecodeError:
            print(f"[{device_id}] bad payload on {msg.topic}: {msg.payload!r}")
            return
        command = payload.get("command")
        if command not in ("ON", "OFF"):
            print(f"[{device_id}] ignoring unknown command: {command!r}")
            return
        state["status"] = command
        client.publish(
            status_topic,
            json.dumps({"status": command, "timestamp": datetime.now(timezone.utc).isoformat()}),
            qos=1,
        )
        print(f"[{device_id}] received command {command}, echoed status on {status_topic}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"sim-{device_id}")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

    def heartbeat_loop():
        while True:
            client.publish(heartbeat_topic, json.dumps({"online": True, "rssi": args.rssi}), qos=1)
            print(f"[{device_id}] heartbeat sent (rssi={args.rssi})")
            time.sleep(HEARTBEAT_INTERVAL)

    threading.Thread(target=heartbeat_loop, daemon=True).start()

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n[{device_id}] stopped")


if __name__ == "__main__":
    main()
