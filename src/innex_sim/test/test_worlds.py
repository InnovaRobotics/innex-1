import os
import subprocess

from helpers import (ARENA_LENGTH, ARENA_WIDTH, ROCK_COUNT, START_ZONE, WORLD,
                     circle_rect_distance, rock_includes)

ROCK_RADIUS = 0.2


def gz_env(models_dir):
    env = dict(os.environ)
    env['GZ_SIM_RESOURCE_PATH'] = str(models_dir)
    # gz sdf -k resolves model:// URIs through SDF_PATH, not GZ_SIM_RESOURCE_PATH.
    env['SDF_PATH'] = str(models_dir)
    return env


def test_gz_sdf_check(models_dir):
    result = subprocess.run(['gz', 'sdf', '-k', str(WORLD)],
                            env=gz_env(models_dir), capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Valid' in result.stdout


def test_rock_layout():
    rocks = rock_includes()
    assert len(rocks) == ROCK_COUNT
    assert len({rock.name for rock in rocks}) == len(rocks)
    for rock in rocks:
        assert ROCK_RADIUS <= rock.x <= ARENA_LENGTH - ROCK_RADIUS, rock.name
        assert ROCK_RADIUS <= rock.y <= ARENA_WIDTH - ROCK_RADIUS, rock.name
        assert circle_rect_distance(rock.x, rock.y, START_ZONE) >= ROCK_RADIUS, rock.name


def test_headless_smoke(models_dir):
    result = subprocess.run(
        ['gz', 'sim', '-s', '-r', '--iterations', '1000', str(WORLD)],
        env=gz_env(models_dir), capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
