#include <Arduino.h>
#include <DriveCore.h>

// PROTOTYPE ONLY. This backend never configures or writes motor pins.
// A reviewed controller-specific adapter and safe hardware defaults are required.
namespace {
drive::Core core;
struct DryRunOutput {
    int32_t left = 0;
    int32_t right = 0;
    void apply(int32_t l, int32_t r) { left = l; right = r; }
} output;
}

void setup() {
    output.apply(0, 0);
    // Teensy USB Serial is initialised by the framework. Do not wait for a host.
}

void loop() {
    core.tick(millis());
    if (!Serial) core.disconnect();
    // Bound work even if the host continuously supplies bytes.
    for (unsigned count = 0; count < 64 && Serial && Serial.available(); ++count) {
        const int byte = Serial.read();
        if (byte < 0) break;
        core.receive(static_cast<uint8_t>(byte), millis());
    }
    core.tick(millis());
    output.apply(core.left(), core.right());
}
