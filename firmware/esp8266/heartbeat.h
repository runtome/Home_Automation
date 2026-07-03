#pragma once

#include <Arduino.h>

// Assembles the timed liveness payload published on home/{device_id}/heartbeat
// (specification.md section 7): {"online": true, "rssi": <dBm>}.
class Heartbeat {
 public:
  // Buffer is reused across calls; the returned pointer is valid until the
  // next call to payload().
  const char* payload(int32_t rssi);

 private:
  char _buf[64];
};
