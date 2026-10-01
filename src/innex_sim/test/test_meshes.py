import subprocess
import sys
from collections import defaultdict

import pytest

from helpers import ARENA_X, ARENA_Y, PACKAGE_DIR, START_ZONE, read_obj

ROCKS = ('rock_a', 'rock_b', 'rock_c', 'rock_d')
GENERATED = [f'{r}/meshes/rock.obj' for r in ROCKS] + ['moon_yard_terrain/meshes/terrain.obj']
DEPRESSION = -0.005


@pytest.mark.parametrize('rock', ROCKS)
def test_rock_mesh_limits(rock, models_dir):
    vertices, faces = read_obj(models_dir / rock / 'meshes' / 'rock.obj')
    xs, ys, zs = zip(*vertices)
    assert 0.30 <= max(max(xs) - min(xs), max(ys) - min(ys)) <= 0.40 + 1e-5
    assert max(zs) <= 0.40
    assert min(zs) == pytest.approx(0.0, abs=1e-3)
    assert len(faces) <= 500


def test_terrain_mesh_limits(models_dir):
    vertices, faces = read_obj(models_dir / 'moon_yard_terrain' / 'meshes' / 'terrain.obj')
    xs, ys, zs = zip(*vertices)
    assert min(xs) == pytest.approx(0.0, abs=1e-6)
    assert max(xs) == pytest.approx(ARENA_X, abs=1e-6)
    assert min(ys) == pytest.approx(0.0, abs=1e-6)
    assert max(ys) == pytest.approx(ARENA_Y, abs=1e-6)
    assert max(zs) == 0.0
    assert min(zs) >= -0.5
    assert len(faces) <= 40000


def test_terrain_depressions_are_small_and_clear_of_start_zone(models_dir):
    vertices, faces = read_obj(models_dir / 'moon_yard_terrain' / 'meshes' / 'terrain.obj')
    deep = {i for i, v in enumerate(vertices) if v[2] < DEPRESSION}
    assert deep

    neighbours = defaultdict(set)
    for face in faces:
        for a in face:
            for b in face:
                if a != b and a in deep and b in deep:
                    neighbours[a].add(b)

    seen = set()
    regions = 0
    for start in sorted(deep):
        if start in seen:
            continue
        regions += 1
        stack = [start]
        seen.add(start)
        region = []
        while stack:
            node = stack.pop()
            region.append(node)
            for other in neighbours[node]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        xs = [vertices[i][0] for i in region]
        ys = [vertices[i][1] for i in region]
        assert max(xs) - min(xs) <= 0.50
        assert max(ys) - min(ys) <= 0.50
        x_min, x_max, y_min, y_max = START_ZONE
        overlaps = max(xs) >= x_min and min(xs) <= x_max and max(ys) >= y_min and min(ys) <= y_max
        assert not overlaps
    assert regions == 3


def test_generator_is_deterministic(tmp_path):
    outputs = []
    for run in ('first', 'second'):
        output = tmp_path / run
        subprocess.run(
            [sys.executable, str(PACKAGE_DIR / 'scripts' / 'generate_assets.py'),
             '--output-dir', str(output)],
            check=True, timeout=60)
        outputs.append(output)
    for relative in GENERATED:
        assert (outputs[0] / relative).read_bytes() == (outputs[1] / relative).read_bytes(), relative
