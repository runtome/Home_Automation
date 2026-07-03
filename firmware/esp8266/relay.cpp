#include "relay.h"

void Relay::begin(uint8_t pin, bool activeLow) {
  _pin = pin;
  _activeLow = activeLow;
  pinMode(_pin, OUTPUT);
  // Safe state on boot, before any network activity (spec section 6.10).
  write(false);
}

void Relay::on() { write(true); }

void Relay::off() { write(false); }

void Relay::toggle() { write(!_on); }

void Relay::write(bool on) {
  _on = on;
  const bool physicalHigh = _activeLow ? !on : on;
  digitalWrite(_pin, physicalHigh ? HIGH : LOW);
}
