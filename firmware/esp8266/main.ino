// Application: orchestrates WifiManager, MqttClient, Relay, and Heartbeat
// through the state machine from specification.md chapter 6.4. The main loop
// never blocks: all timing is millis()-based and every branch returns
// quickly so the SDK/watchdog keep running (section 6.5, 6.10).

#include <ArduinoJson.h>
#include <ESP8266WiFi.h>

#include "config.h"
#include "heartbeat.h"
#include "mqtt.h"
#include "relay.h"
#include "wifi.h"

enum class State { BOOT, WIFI_CONNECT, MQTT_CONNECT, REGISTER, OPERATIONAL, RECONNECT };

// Deliberately not wrapped in an anonymous namespace: the Arduino/PlatformIO
// .ino prototype-generation pass does not handle anonymous namespaces
// correctly and mis-declares setup()/loop(), so file-scope (internal
// linkage doesn't matter for a single-TU sketch) is used instead.
WiFiClient netClient;
WifiManager wifi;
MqttClient mqttClient;
Relay relay;
Heartbeat heartbeat;

State state = State::BOOT;
uint32_t stateEnteredAt = 0;
uint32_t lastAttempt = 0;
uint32_t lastBeat = 0;
uint32_t backoffMs = BACKOFF_MIN;

const uint32_t kMqttAttemptIntervalMs = 1000UL;

void enterState(State next) {
  state = next;
  stateEnteredAt = millis();
}

void publishStatus(const char* requestId) {
  StaticJsonDocument<128> doc;
  doc["status"] = relay.isOn() ? "ON" : "OFF";
  if (requestId && requestId[0] != '\0') {
    doc["request_id"] = requestId;
  }
  char buf[128];
  serializeJson(doc, buf, sizeof(buf));
  mqttClient.publish(TOPIC_STATUS, buf);
}

// Publishes the register payload and (re-)subscribes to the command topic.
// Called once after every successful MQTT connection, whether that is the
// very first boot or a recovery after a dropped link (spec: "re-announce
// presence after reconnection").
void announcePresence() {
  StaticJsonDocument<192> doc;
  doc["mac_address"] = WiFi.macAddress();
  doc["ip_address"] = WiFi.localIP().toString();
  doc["firmware"] = FIRMWARE_VERSION;
  char buf[192];
  serializeJson(doc, buf, sizeof(buf));
  mqttClient.publish(TOPIC_REGISTER, buf);

  mqttClient.subscribe(TOPIC_SET);
  publishStatus("");   // authoritative status right after (re)announcing
}

void onMessage(char* topic, uint8_t* payload, unsigned int len) {
  StaticJsonDocument<128> doc;
  if (deserializeJson(doc, payload, len)) return;   // ignore malformed

  const char* cmd = doc["command"] | "";
  if (!strcmp(cmd, "ON")) {
    relay.on();
  } else if (!strcmp(cmd, "OFF")) {
    relay.off();
  } else if (!strcmp(cmd, "TOGGLE")) {
    relay.toggle();
  } else {
    return;   // unknown command: ignore silently (section 6.10)
  }
  publishStatus(doc["request_id"] | "");
}

void setup() {
  // BOOT: relay to a defined safe state before any network activity.
  relay.begin(RELAY_PIN, RELAY_ACTIVE_LOW);

  wifi.begin(WIFI_SSID, WIFI_PASS);
  mqttClient.begin(netClient, BROKER_HOST, BROKER_PORT, onMessage);

  enterState(State::WIFI_CONNECT);
}

void loop() {
  const uint32_t now = millis();

  switch (state) {
    case State::BOOT:
      // Unreachable after setup(); kept for completeness of the state table.
      enterState(State::WIFI_CONNECT);
      break;

    case State::WIFI_CONNECT:
      if (wifi.isConnected()) {
        enterState(State::MQTT_CONNECT);
      } else if (now - stateEnteredAt >= WIFI_CONNECT_TIMEOUT_MS) {
        enterState(State::RECONNECT);
      }
      break;

    case State::MQTT_CONNECT:
      if (now - lastAttempt >= kMqttAttemptIntervalMs) {
        lastAttempt = now;
        if (mqttClient.connectWithWill()) {
          enterState(State::REGISTER);
        } else if (now - stateEnteredAt >= MQTT_CONNECT_TIMEOUT_MS) {
          enterState(State::RECONNECT);
        }
      }
      break;

    case State::REGISTER:
      announcePresence();
      backoffMs = BACKOFF_MIN;
      lastBeat = now;
      enterState(State::OPERATIONAL);
      break;

    case State::OPERATIONAL:
      if (!wifi.isConnected() || !mqttClient.isConnected()) {
        enterState(State::RECONNECT);
        break;
      }
      mqttClient.loop();   // process inbound, keepalive
      if (now - lastBeat >= HEARTBEAT_MS) {
        mqttClient.publish(TOPIC_HEARTBEAT, heartbeat.payload(WiFi.RSSI()));
        lastBeat = now;
      }
      break;

    case State::RECONNECT:
      if (now - lastAttempt >= backoffMs) {
        lastAttempt = now;
        if (!wifi.isConnected()) {
          wifi.reconnect();
          enterState(State::WIFI_CONNECT);
        } else if (mqttClient.connectWithWill()) {
          announcePresence();
          backoffMs = BACKOFF_MIN;
          lastBeat = now;
          enterState(State::OPERATIONAL);
        } else {
          const uint32_t doubled = backoffMs * 2;
          backoffMs = (doubled < BACKOFF_MAX) ? doubled : BACKOFF_MAX;
        }
      }
      break;
  }

  yield();   // feed WDT, let the SDK run
}
