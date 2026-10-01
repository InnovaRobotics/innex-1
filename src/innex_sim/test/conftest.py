import shutil

import pytest

from helpers import MODELS_DIR, run_generator


@pytest.fixture(scope='session')
def models_dir(tmp_path_factory):
    """Source models plus freshly generated meshes, in a temporary tree."""
    target = tmp_path_factory.mktemp('models') / 'models'
    shutil.copytree(MODELS_DIR, target)
    run_generator(target)
    return target
