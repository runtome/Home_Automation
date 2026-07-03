#include "wifi.h"

#include <ESP8266WiFi.h>

void WifiManager::begin(const char* ssid, const char* password) {
  _ssid = ssid;
  _password = password;
  WiFi.persistent(false);   // avoid wearing flash on every reconnect
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(false);   // we drive reconnection explicitly (state machine owns it)
  WiFi.begin(_ssid, _password);
}

void WifiManager::reconnect() {
  WiFi.disconnect();
  WiFi.begin(_ssid, _password);
}

bool WifiManager::isConnected() const {
  return WiFi.status() == WL_CONNECTED;
}
