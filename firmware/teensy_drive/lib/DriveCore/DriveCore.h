#pragma once
#include <cstddef>
#include <cstdint>

namespace drive {
constexpr uint32_t kTimeoutMs = 250;
constexpr size_t kFrameSize = 18;
// Prototype limit only, NOT a measured rover speed limit.
constexpr int32_t kPrototypeLimitMrad = 1000;

struct Command {
    uint32_t sequence;
    int32_t left_mrad_s;
    int32_t right_mrad_s;
};
uint16_t crc16(const uint8_t* data, size_t size);
void encode(const Command& command, uint8_t* frame);

class Core {
public:
    // A complete, valid frame is the only route to changing a target.
    bool receive(uint8_t byte, uint32_t now_ms);
    void tick(uint32_t now_ms);
    void disconnect();
    int32_t left() const { return left_; }
    int32_t right() const { return right_; }
    bool armed() const { return armed_; }
private:
    bool accept(const Command& command, uint32_t now_ms);
    void stop();
    uint8_t buffer_[kFrameSize]{};
    size_t used_ = 0;
    uint32_t last_byte_ms_ = 0;
    uint32_t last_valid_ms_ = 0;
    uint32_t last_sequence_ = 0;
    bool have_sequence_ = false;
    bool armed_ = false;
    int32_t left_ = 0;
    int32_t right_ = 0;
};
}  // namespace drive
