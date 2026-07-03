#!/usr/bin/env bash
# Generates mqtt/passwd (bcrypt-hashed mosquitto credentials) used by the
# mosquitto broker for username/password auth (specification.md section 11).
#
# Usage: ./scripts/gen-mqtt-password.sh <username> <password>
#   defaults to the MQTT_USERNAME/MQTT_PASSWORD in .env if omitted.
#
# Safe to run multiple times for multiple credentials (backend + one per
# device): the first run creates mqtt/passwd, subsequent runs add/update a
# user in place rather than clobbering existing entries.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

USERNAME="${1:-${MQTT_USERNAME:-ha_backend}}"
PASSWORD="${2:-${MQTT_PASSWORD:-change_me}}"

mkdir -p mqtt

if [ -f mqtt/passwd ]; then
  CREATE_FLAG=""
else
  CREATE_FLAG="-c"
fi

docker run --rm -v "$(pwd)/mqtt:/mosquitto/config" eclipse-mosquitto:2 \
  mosquitto_passwd -b $CREATE_FLAG /mosquitto/config/passwd "$USERNAME" "$PASSWORD"

echo "Wrote mqtt/passwd for user '$USERNAME'."
