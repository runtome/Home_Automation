#include "mqtt.h"

#include "config.h"

namespace {
// Design decision: the Last Will targets the heartbeat topic with the same
// {"online": false, ...} shape a graceful "going offline" message would use,
// rather than a bespoke "availability" topic. This lets the backend's
// existing heartbeat handler (which already flips Device.online) detect an
// ungraceful disconnect immediately via the broker-delivered LWT, instead of
// waiting out the ~90s offline-watchdog timeout (specification.md section 3).
const char kLastWillPayload[] = "{\"online\":false,\"rssi\":0}";
}  // namespace

void MqttClient::begin(Client& netClient, const char* host, uint16_t port, MessageCallback callback) {
  _client.setClient(netClient);
  _client.setServer(host, port);
  _client.setCallback(callback);
  _client.setBufferSize(256);   // spec section 6.8.2: MQTT buffers sized to max payload
}

bool MqttClient::connectWithWill() {
  const bool ok = _client.connect(
      MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS,
      TOPIC_HEARTBEAT, /*willQos=*/1, /*willRetain=*/false, kLastWillPayload,
      /*cleanSession=*/true);
  return ok;
}

bool MqttClient::isConnected() { return _client.connected(); }

void MqttClient::loop() { _client.loop(); }

bool MqttClient::subscribe(const char* topic) { return _client.subscribe(topic); }

bool MqttClient::publish(const char* topic, const char* payload, bool retain) {
  return _client.publish(topic, payload, retain);
}
