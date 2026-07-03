#pragma once

#include <Arduino.h>

// GPIO abstraction for the relay: on/off/toggle and state read-back.
// Supports active-low relay modules (the common cheap 1-channel boards)
// via RELAY_ACTIVE_LOW in config.h.
class Relay {
 public:
  void begin(uint8_t pin, bool activeLow);

  void on();
  void off();
  void toggle();
  bool isOn() const { return _on; }

 private:
  void write(bool on);

  uint8_t _pin = 0;
  bool _activeLow = false;
  bool _on = false;
};
