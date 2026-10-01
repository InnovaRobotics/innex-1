import math
import xml.etree.ElementTree as ET
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = PACKAGE_DIR / 'models'
WORLDS_DIR = PACKAGE_DIR / 'worlds'
WORLDS = ('moon_yard', 'moon_yard_flat')

ARENA_X = 7.9
ARENA_Y = 4.4
START_ZONE = (0.0, 2.0, 2.4, 4.4)  # x min, x max, y min, y max


def read_obj(path):
    vertices = []
    faces = []
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'v':
            vertices.append(tuple(float(p) for p in parts[1:4]))
        elif parts[0] == 'f':
            faces.append(tuple(int(p.split('/')[0]) - 1 for p in parts[1:]))
    return vertices, faces


def rock_includes(world):
    """Return (model name, instance name, x, y, yaw) for each rock include."""
    root = ET.parse(WORLDS_DIR / f'{world}.sdf').getroot()
    rocks = []
    for include in root.iter('include'):
        uri = include.findtext('uri')
        if not uri.startswith('model://rock_'):
            continue
        pose = [float(v) for v in include.findtext('pose').split()]
        rocks.append((uri[len('model://'):], include.findtext('name'), pose[0], pose[1], pose[5]))
    return rocks


def circle_rect_distance(cx, cy, rect):
    x_min, x_max, y_min, y_max = rect
    dx = max(x_min - cx, 0.0, cx - x_max)
    dy = max(y_min - cy, 0.0, cy - y_max)
    return math.hypot(dx, dy)
