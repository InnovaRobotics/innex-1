import os
import subprocess

import pytest

from helpers import (ARENA_X, ARENA_Y, START_ZONE, WORLDS, WORLDS_DIR,
                     circle_rect_distance, rock_includes)

ROCK_RADIUS = 0.2


def gz_env(models_dir):
    env = dict(os.environ)
    env['GZ_SIM_RESOURCE_PATH'] = str(models_dir)
    env['SDF_PATH'] = str(models_dir)
    return env


@pytest.mark.parametrize('world', WORLDS)
def test_gz_sdf_check(world, models_dir):
    result = subprocess.run(['gz', 'sdf', '-k', str(WORLDS_DIR / f'{world}.sdf')],
                            env=gz_env(models_dir), capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Valid' in result.stdout


@pytest.mark.parametrize('world', WORLDS)
def test_rock_layout(world):
    rocks = rock_includes(world)
    assert len(rocks) == 9
    assert len({name for _, name, *_ in rocks}) == len(rocks)
    for _, name, x, y, _ in rocks:
        assert ROCK_RADIUS <= x <= ARENA_X - ROCK_RADIUS, name
        assert ROCK_RADIUS <= y <= ARENA_Y - ROCK_RADIUS, name
        assert circle_rect_distance(x, y, START_ZONE) >= ROCK_RADIUS, name


@pytest.mark.parametrize('world', WORLDS)
def test_headless_smoke(world, models_dir):
    result = subprocess.run(
        ['gz', 'sim', '-s', '-r', '--iterations', '1000', str(WORLDS_DIR / f'{world}.sdf')],
        env=gz_env(models_dir), capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
