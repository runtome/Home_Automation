#pragma once

// Compile-time device configuration. Baseline configuration is compile-time
// for determinism; a captive-portal provisioning path is a future addition
// (see specification.md section 13) that would replace these with values
// read from LittleFS/EEPROM at boot instead of reflashing.

#define FIRMWARE_VERSION "1.0.0"

#define DEVICE_ID        "light001"
#define WIFI_SSID        "HomeNet"
#define WIFI_PASS        "********"

#define BROKER_HOST      "192.168.1.10"
#define BROKER_PORT      1883          // 8883 for TLS (see section 6.8, IMPORTANT note)
#define MQTT_USER        "light001"
#define MQTT_PASS        "********"

#define RELAY_PIN        5             // GPIO5 (D1)
#define RELAY_ACTIVE_LOW 1

#define HEARTBEAT_MS     30000UL       // spec section 3: 30s heartbeat interval
#define BACKOFF_MIN      1000UL
#define BACKOFF_MAX      32000UL

#define WIFI_CONNECT_TIMEOUT_MS 15000UL
#define MQTT_CONNECT_TIMEOUT_MS 8000UL

// MQTT topics per specification.md section 7: home/{device_id}/{suffix}
#define TOPIC_SET        "home/" DEVICE_ID "/set"
#define TOPIC_STATUS     "home/" DEVICE_ID "/status"
#define TOPIC_HEARTBEAT  "home/" DEVICE_ID "/heartbeat"
#define TOPIC_REGISTER   "home/" DEVICE_ID "/register"
#define TOPIC_INFO       "home/" DEVICE_ID "/info"

#define MQTT_CLIENT_ID   DEVICE_ID
