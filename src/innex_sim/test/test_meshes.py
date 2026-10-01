import pytest

from helpers import (ARENA_LENGTH, ARENA_WIDTH, CRATER_COUNT, CRATER_DEPTH_THRESHOLD,
                     MAX_CRATER_DEPTH, MAX_CRATER_WIDTH, MAX_ROCK_SIZE, MAX_ROCK_TRIANGLES,
                     MAX_TERRAIN_TRIANGLES, MIN_ROCK_SIZE, OBJ_PRECISION, START_ZONE,
                     depressed_regions, read_obj, run_generator)

ROCKS = ('rock_a', 'rock_b', 'rock_c', 'rock_d')
TERRAIN = 'moon_yard_terrain/meshes/terrain.obj'
GENERATED = [f'{rock}/meshes/rock.obj' for rock in ROCKS] + [TERRAIN]


@pytest.mark.parametrize('rock', ROCKS)
def test_rock_mesh_limits(rock, models_dir):
    vertices, faces = read_obj(models_dir / rock / 'meshes' / 'rock.obj')
    xs, ys, zs = zip(*vertices)
    size = max(max(xs) - min(xs), max(ys) - min(ys))
    assert MIN_ROCK_SIZE - OBJ_PRECISION <= size <= MAX_ROCK_SIZE + OBJ_PRECISION
    assert max(zs) <= MAX_ROCK_SIZE
    assert min(zs) == pytest.approx(0.0, abs=OBJ_PRECISION)
    assert len(faces) <= MAX_ROCK_TRIANGLES


def test_terrain_mesh_limits(models_dir):
    vertices, faces = read_obj(models_dir / TERRAIN)
    xs, ys, zs = zip(*vertices)
    assert min(xs) == pytest.approx(0.0, abs=OBJ_PRECISION)
    assert max(xs) == pytest.approx(ARENA_LENGTH, abs=OBJ_PRECISION)
    assert min(ys) == pytest.approx(0.0, abs=OBJ_PRECISION)
    assert max(ys) == pytest.approx(ARENA_WIDTH, abs=OBJ_PRECISION)
    assert max(zs) == 0.0
    assert min(zs) >= -MAX_CRATER_DEPTH
    assert len(faces) <= MAX_TERRAIN_TRIANGLES


def test_terrain_craters_are_small_and_clear_of_start_zone(models_dir):
    vertices, faces = read_obj(models_dir / TERRAIN)
    regions = depressed_regions(vertices, faces, CRATER_DEPTH_THRESHOLD)
    assert len(regions) == CRATER_COUNT
    for region in regions:
        xs = [vertices[i][0] for i in region]
        ys = [vertices[i][1] for i in region]
        assert max(xs) - min(xs) <= MAX_CRATER_WIDTH
        assert max(ys) - min(ys) <= MAX_CRATER_WIDTH
        overlaps_start_zone = (max(xs) >= START_ZONE.x_min and min(xs) <= START_ZONE.x_max
                               and max(ys) >= START_ZONE.y_min and min(ys) <= START_ZONE.y_max)
        assert not overlaps_start_zone


def test_generator_is_deterministic(tmp_path):
    run_generator(tmp_path / 'first')
    run_generator(tmp_path / 'second')
    for relative in GENERATED:
        assert (tmp_path / 'first' / relative).read_bytes() == (tmp_path / 'second' / relative).read_bytes()
