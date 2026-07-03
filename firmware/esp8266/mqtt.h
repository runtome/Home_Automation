#pragma once

#include <Arduino.h>
#include <PubSubClient.h>

// Broker connection, Last Will, subscribe/publish, and inbound message
// routing. Wraps PubSubClient so main.ino only deals with our narrow
// interface, not the library's connection-overload details.
class MqttClient {
 public:
  using MessageCallback = void (*)(char* topic, uint8_t* payload, unsigned int length);

  void begin(Client& netClient, const char* host, uint16_t port, MessageCallback callback);

  // Connects with the client id/credentials from config.h, registering a
  // Last Will on the heartbeat topic (see mqtt.cpp for the rationale).
  // Non-blocking from the caller's perspective in the sense that a failed
  // attempt returns immediately rather than retrying internally; the state
  // machine in main.ino owns backoff/retry timing.
  bool connectWithWill();

  bool isConnected();
  void loop();
  bool subscribe(const char* topic);
  bool publish(const char* topic, const char* payload, bool retain = false);

 private:
  PubSubClient _client;
};
