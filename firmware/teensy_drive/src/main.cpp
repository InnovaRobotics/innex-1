#include <Arduino.h>
#include <DriveCore.h>

// Dry-run motor backend until Sabertooth 2x32 Packet Serial wiring is integrated.
// LED_BUILTIN lights whenever DriveCore is armed with a non-zero wheel target,
// allowing end-to-end USB bench checks on a bare Teensy 4.1 with no motors wired.
namespace {
drive::Core core;
struct DryRunOutput {
    int32_t left = 0;
    int32_t right = 0;
    void apply(int32_t l, int32_t r) { left = l; right = r; }
} output;
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
    output.apply(0, 0);
}

void loop() {
    core.tick(millis());
    if (!Serial) core.disconnect();
    // Bound reads per pass so continuous USB bytes cannot starve the timeout check.
    for (unsigned count = 0; count < 64 && Serial && Serial.available(); ++count) {
        const int byte = Serial.read();
        if (byte < 0) break;
        core.receive(static_cast<uint8_t>(byte), millis());
    }
    core.tick(millis());
    output.apply(core.left(), core.right());
    const bool moving = core.armed() && (core.left() != 0 || core.right() != 0);
    digitalWrite(LED_BUILTIN, moving ? HIGH : LOW);
}
