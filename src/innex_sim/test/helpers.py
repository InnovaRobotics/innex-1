import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import NamedTuple

PACKAGE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = PACKAGE_DIR / 'models'
GENERATOR = PACKAGE_DIR / 'scripts' / 'generate_assets.py'
WORLD = PACKAGE_DIR / 'worlds' / 'moon_yard.sdf'

ARENA_LENGTH = 7.9
ARENA_WIDTH = 4.4


class Rect(NamedTuple):
    x_min: float
    x_max: float
    y_min: float
    y_max: float


START_ZONE = Rect(0.0, 2.0, 2.4, 4.4)

# UK Lunabotics 2026 rulebook v1.0, p. 5
MIN_ROCK_SIZE = 0.30
MAX_ROCK_SIZE = 0.40
MAX_CRATER_WIDTH = 0.50
MAX_CRATER_DEPTH = 0.50

MAX_ROCK_TRIANGLES = 500
MAX_TERRAIN_TRIANGLES = 40000
ROCK_COUNT = 9
CRATER_COUNT = 3

# The OBJ files hold six decimal places.
OBJ_PRECISION = 1e-5
CRATER_DEPTH_THRESHOLD = -0.005


class RockPlacement(NamedTuple):
    name: str
    x: float
    y: float


def run_generator(output_dir):
    subprocess.run([sys.executable, str(GENERATOR), '--output-dir', str(output_dir)],
                   check=True, timeout=60)


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


def depressed_regions(vertices, faces, threshold):
    """Group the vertices below threshold into connected regions of vertex indices."""
    deep = {i for i, v in enumerate(vertices) if v[2] < threshold}
    neighbours = {i: set() for i in deep}
    for face in faces:
        deep_in_face = [i for i in face if i in deep]
        for i in deep_in_face:
            neighbours[i].update(deep_in_face)

    regions = []
    seen = set()
    for start in sorted(deep):
        if start in seen:
            continue
        seen.add(start)
        region = []
        stack = [start]
        while stack:
            node = stack.pop()
            region.append(node)
            for other in neighbours[node] - seen:
                seen.add(other)
                stack.append(other)
        regions.append(region)
    return regions


def rock_includes():
    root = ET.parse(WORLD).getroot()
    rocks = []
    for include in root.iter('include'):
        if include.findtext('uri').startswith('model://rock_'):
            pose = include.findtext('pose').split()
            rocks.append(RockPlacement(include.findtext('name'), float(pose[0]), float(pose[1])))
    return rocks


def circle_rect_distance(cx, cy, rect):
    dx = max(rect.x_min - cx, 0.0, cx - rect.x_max)
    dy = max(rect.y_min - cy, 0.0, cy - rect.y_max)
    return math.hypot(dx, dy)
