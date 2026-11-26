"""Test skid-steer wheel conversion, wire framing, and C++ DriveCore compatibility."""

import math
from pathlib import Path
import re
import struct
import subprocess

from innex_drive_bridge.protocol import (
    decode,
    encode,
    LIMIT_MRAD_S,
    MAX_WHEEL_RAD_S,
    wheel_targets,
)
import pytest


@pytest.fixture(scope='module')
def firmware_runner(tmp_path_factory):
    """Compile DriveCore on main into a small stdin-to-stdout test binary."""
    folder = tmp_path_factory.mktemp('firmware_compatibility')
    repo_root = Path(__file__).resolve().parents[3]
    reference = repo_root / 'firmware' / 'teensy_drive' / 'lib' / 'DriveCore'
    source = folder / 'runner.cpp'
    source.write_text(r"""
#include "DriveCore.h"
#include <cstring>
#include <iostream>
int main(int argc, char** argv) {
    if (argc > 1 && std::strcmp(argv[1], "--limit") == 0) {
        std::cout << drive::kPrototypeLimitMrad << "\n";
        return 0;
    }
    drive::Core core;
    unsigned char event[22];
    while (std::cin.read(reinterpret_cast<char*>(event), sizeof(event))) {
        uint32_t now = uint32_t(event[0]) | (uint32_t(event[1]) << 8) |
            (uint32_t(event[2]) << 16) | (uint32_t(event[3]) << 24);
        for (unsigned i = 4; i < 22; ++i) core.receive(event[i], now);
        core.tick(now);
        std::cout << core.left() << " " << core.right() << " " << core.armed() << "\n";
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
    """Feed timestamped 18-byte frames into DriveCore and return (left, right, armed)."""
    payload = b''.join(struct.pack('<I', ms) + frame for ms, frame in events)
    result = subprocess.run(
        [str(binary)], input=payload, capture_output=True, check=True, timeout=5)
    return [tuple(map(int, line.split())) for line in result.stdout.splitlines()]


def test_speed_limit_matches_firmware(firmware_runner):
    """Keep the Python wheel speed cap equal to DriveCore's kPrototypeLimitMrad."""
    result = subprocess.run(
        [str(firmware_runner), '--limit'], capture_output=True, text=True, check=True)
    assert LIMIT_MRAD_S == int(result.stdout.strip())
    assert MAX_WHEEL_RAD_S == LIMIT_MRAD_S / 1000.0


@pytest.mark.parametrize('linear,angular,expected', [
    (0.0, 0.0, (0, 0)),
    (0.153, 0.0, (1000, 1000)),
    (-0.0765, 0.0, (-500, -500)),
    (0.0, 0.4, (-882, 882)),
    (0.0, -0.4, (882, -882)),
    (1.53, 0.0, (1000, 1000)),
])
def test_wheel_targets(linear, angular, expected):
    """Check units, turn signs, and symmetric clamping."""
    assert wheel_targets(linear, angular) == expected


def test_curvature_preserved():
    """Scale both wheels together when saturated so turning radius stays unchanged."""
    assert wheel_targets(0.3, 0.5, radius=0.1, track=0.4) == (500, 1000)


@pytest.mark.parametrize('kwargs', [
    {'radius': 0.0},
    {'track': -1.0},
    {'max_wheel_rad_s': MAX_WHEEL_RAD_S + 0.1},
    {'radius': math.nan},
])
def test_invalid_geometry(kwargs):
    """Reject non-positive geometry or speed caps above the firmware limit."""
    with pytest.raises(ValueError):
        wheel_targets(0.0, 0.0, **kwargs)


@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf, 1e308])
def test_invalid_velocity(value):
    """Reject non-finite inputs and float overflow."""
    with pytest.raises(ValueError):
        wheel_targets(value, value)


def test_golden_frame_and_signed_roundtrip():
    """Match the golden CRC vector in firmware/teensy_drive/tools/test_protocol.py."""
    assert encode(1, 0, 0).hex() == '44520100010000000000000000000000be37'
    assert decode(encode(0xFFFFFFFF, -300, 400)) == (0xFFFFFFFF, -300, 400)


@pytest.mark.parametrize('args', [
    (-1, 0, 0), (2**32, 0, 0), (1, LIMIT_MRAD_S + 1, 0),
    (1, 0, -LIMIT_MRAD_S - 1), (1, 0.5, 0), (True, 0, 0),
])
def test_bad_encoder_values(args):
    """Reject out-of-range, float, or boolean arguments before packing bytes."""
    with pytest.raises(ValueError):
        encode(*args)


def test_decoder_checks():
    """Reject corrupted headers, bad CRCs, and truncated frames."""
    frame = encode(1, 0, 0)
    for index in (0, 2, 3, 8, 16):
        bad = bytearray(frame)
        bad[index] ^= 1
        with pytest.raises(ValueError):
            decode(bad)
    with pytest.raises(ValueError):
        decode(frame[:-1])


def test_host_frames_drive_firmware_and_recover(firmware_runner):
    """Verify arming, motion, old-sequence rejection, CRC stop, and restart jump."""
    left, right = wheel_targets(0.0765, 0.1)
    corrupt = bytearray(encode(4, 300, 300))
    corrupt[8] ^= 1
    events = [
        (0, encode(1, 0, 0)),
        (20, encode(2, left, right)),
        (30, encode(1, 800, 800)),
        (40, bytes(corrupt)),
        (1060, encode(1060, 0, 0)),
        (1080, encode(1061, -300, 400)),
    ]
    assert run_frames(firmware_runner, events) == [
        (0, 0, 1),
        (279, 721, 1),
        (279, 721, 1),
        (0, 0, 0),
        (0, 0, 1),
        (-300, 400, 1),
    ]


def test_geometry_matches_urdf():
    """Keep drive_bridge.yaml wheel radius and track aligned with the URDF."""
    repo_root = Path(__file__).resolve().parents[3]
    urdf = (repo_root / 'src' / 'innex_description' / 'urdf' / 'innex_1.urdf.xacro').read_text()
    cfg = (Path(__file__).resolve().parents[1] / 'config' / 'drive_bridge.yaml').read_text()

    urdf_radius = float(re.search(r'name="wheel_radius"\s+value="([0-9.]+)"', urdf).group(1))
    urdf_track = float(re.search(r'name="track"\s+value="([0-9.]+)"', urdf).group(1))
    cfg_radius = float(re.search(r'wheel_radius_m:\s*([0-9.]+)', cfg).group(1))
    cfg_track = float(re.search(r'track_width_m:\s*([0-9.]+)', cfg).group(1))

    assert cfg_radius == pytest.approx(urdf_radius)
    assert cfg_track == pytest.approx(urdf_track)
