#pragma once

#include <Arduino.h>

// Connects, monitors, and reconnects Wi-Fi non-blockingly. begin()/reconnect()
// only kick off the SDK's asynchronous association; isConnected() reflects
// the current link state on each call, polled from the main loop.
class WifiManager {
 public:
  void begin(const char* ssid, const char* password);
  void reconnect();
  bool isConnected() const;

 private:
  const char* _ssid = nullptr;
  const char* _password = nullptr;
};
