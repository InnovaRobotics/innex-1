// Copyright 2026 Leo-P-1109
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "DriveCore.h"
#include <cstring>

namespace drive {
namespace {
uint32_t read32(const uint8_t* p) {
    return uint32_t(p[0]) | (uint32_t(p[1]) << 8) |
           (uint32_t(p[2]) << 16) | (uint32_t(p[3]) << 24);
}
int32_t signed32(const uint8_t* p) {
    const uint32_t bits = read32(p);
    // Avoid implementation-defined unsigned-to-signed overflow conversions.
    return bits <= 0x7fffffffU ? int32_t(bits) : -1 - int32_t(~bits);
}
void write32(uint8_t* p, uint32_t value) {
    for (unsigned i = 0; i < 4; ++i) p[i] = uint8_t(value >> (8 * i));
}
bool in_range(int32_t value) {
    return value >= -kPrototypeLimitMrad && value <= kPrototypeLimitMrad;
}
}

uint16_t crc16(const uint8_t* data, size_t size) {
    uint16_t crc = 0xffff;
    for (size_t i = 0; i < size; ++i) {
        crc ^= uint16_t(data[i]) << 8;
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc & 0x8000) ? uint16_t((crc << 1) ^ 0x1021) : uint16_t(crc << 1);
    }
    return crc;
}

void encode(const Command& command, uint8_t* frame) {
    frame[0] = 'D'; frame[1] = 'R'; frame[2] = 1; frame[3] = 0;
    write32(frame + 4, command.sequence);
    write32(frame + 8, uint32_t(command.left_mrad_s));
    write32(frame + 12, uint32_t(command.right_mrad_s));
    const uint16_t crc = crc16(frame, 16);
    frame[16] = uint8_t(crc); frame[17] = uint8_t(crc >> 8);
}

void Core::stop() { armed_ = false; left_ = 0; right_ = 0; }
void Core::disconnect() { stop(); used_ = 0; }
void Core::tick(uint32_t now_ms) {
    // Unsigned subtraction remains valid across millis() wraparound.
    if (armed_ && uint32_t(now_ms - last_valid_ms_) >= kTimeoutMs) stop();
}

bool Core::accept(const Command& c, uint32_t now_ms) {
    if (!in_range(c.left_mrad_s) || !in_range(c.right_mrad_s)) { stop(); return false; }
    if (have_sequence_) {
        const uint32_t delta = c.sequence - last_sequence_;
        if (delta == 0 || delta >= 0x80000000U) return false;
    }
    // Startup and recovery require a fresh explicit zero command first.
    if (!armed_ && (c.left_mrad_s != 0 || c.right_mrad_s != 0)) return false;
    last_sequence_ = c.sequence;
    have_sequence_ = true;
    last_valid_ms_ = now_ms;
    armed_ = true;
    left_ = c.left_mrad_s;
    right_ = c.right_mrad_s;
    return true;
}

bool Core::receive(uint8_t byte, uint32_t now_ms) {
    tick(now_ms);
    if (used_ && uint32_t(now_ms - last_byte_ms_) >= kTimeoutMs) used_ = 0;
    last_byte_ms_ = now_ms;
    buffer_[used_++] = byte;
    if (used_ != kFrameSize) return false;
    const uint16_t received = uint16_t(buffer_[16]) | (uint16_t(buffer_[17]) << 8);
    const bool valid = buffer_[0] == 'D' && buffer_[1] == 'R' &&
        buffer_[2] == 1 && buffer_[3] == 0 && crc16(buffer_, 16) == received;
    if (!valid) {
        stop();
        // Sliding window recovers after noise, truncation or a corrupt frame.
        std::memmove(buffer_, buffer_ + 1, kFrameSize - 1);
        used_ = kFrameSize - 1;
        return false;
    }
    const Command c{read32(buffer_ + 4), signed32(buffer_ + 8), signed32(buffer_ + 12)};
    used_ = 0;
    return accept(c, now_ms);
}
}  // namespace drive
