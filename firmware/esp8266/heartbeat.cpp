#include "heartbeat.h"

#include <ArduinoJson.h>

const char* Heartbeat::payload(int32_t rssi) {
  StaticJsonDocument<64> doc;
  doc["online"] = true;
  doc["rssi"] = rssi;
  serializeJson(doc, _buf, sizeof(_buf));
  return _buf;
}
