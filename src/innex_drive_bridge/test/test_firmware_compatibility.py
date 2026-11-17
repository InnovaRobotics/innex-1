# Copyright 2026 Leo-P-1109
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Feed host frames through the actual PR 10 C++ receiver, without a board."""

from pathlib import Path
import struct
import subprocess

from innex_drive_bridge.control import CommandState
from innex_drive_bridge.protocol import encode
from innex_drive_bridge.sender import Sender
from innex_drive_bridge.sequence import SequenceCounter
from innex_drive_bridge.transport import DryRunTransport
import pytest


@pytest.fixture(scope='module')
def firmware_runner(tmp_path_factory):
    """Compile the unchanged receiver reference with an in-memory input harness."""
    folder = tmp_path_factory.mktemp('firmware_compatibility')
    reference = Path(__file__).parent / 'firmware_reference'
    source = folder / 'runner.cpp'
    source.write_text("""
#include "DriveCore.h"
#include <iostream>
int main() {
    drive::Core core;
    unsigned char event[22];
    while (std::cin.read(reinterpret_cast<char*>(event), sizeof(event))) {
        uint32_t now = uint32_t(event[0]) | (uint32_t(event[1]) << 8) |
            (uint32_t(event[2]) << 16) | (uint32_t(event[3]) << 24);
        for (unsigned i = 4; i < 22; ++i) core.receive(event[i], now);
        core.tick(now);
        std::cout << core.left() << " " << core.right() << " " << core.armed() << "\\n";
    }
}
""")
    binary = folder / 'runner'
    subprocess.run([
        'g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-I', str(reference),
        str(source), str(reference / 'DriveCore.cpp'), '-o', str(binary),
    ], check=True, timeout=30, capture_output=True)
    return binary


def run_frames(binary, events):
    """Return the receiver's output after each timestamped host frame."""
    payload = b''.join(struct.pack('<I', ms) + frame for ms, frame in events)
    result = subprocess.run([str(binary)], input=payload, capture_output=True,
                            check=True, timeout=5)
    return [tuple(map(int, line.split())) for line in result.stdout.splitlines()]


def test_host_frames_drive_reference_and_stop(firmware_runner):
    """Verify complete sender-to-firmware conversion and host timeout recovery."""
    state = CommandState()
    transport = DryRunTransport()
    sender = Sender(state, transport, SequenceCounter())
    sender.tick(0)
    events = [(0, transport.last_frame)]
    assert state.update(.077, .1, 1_000_000_000, 'base_link', 1_000_000_000, 20_000_000)
    sender.tick(20_000_000)
    events.append((20, transport.last_frame))
    sender.tick(520_000_000)
    events.append((520, transport.last_frame))
    assert run_frames(firmware_runner, events) == [(0, 0, 1), (301, 699, 1), (0, 0, 1)]


def test_firmware_rejects_old_frames_and_stops_on_corruption(firmware_runner):
    """Use the firmware's independent implementation of CRC and sequence checks."""
    corrupt = bytearray(encode(4, 300, 300))
    corrupt[8] ^= 1
    events = [
        (0, encode(1, 0, 0)), (20, encode(3, -300, 400)),
        (30, encode(2, 800, 800)), (40, bytes(corrupt)),
    ]
    assert run_frames(firmware_runner, events) == [
        (0, 0, 1), (-300, 400, 1), (-300, 400, 1), (0, 0, 0),
    ]
