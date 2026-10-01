import shutil
import subprocess
import sys

import pytest

from helpers import MODELS_DIR, PACKAGE_DIR


@pytest.fixture(scope='session')
def models_dir(tmp_path_factory):
    """Source models plus freshly generated meshes, in a temporary tree."""
    target = tmp_path_factory.mktemp('models') / 'models'
    shutil.copytree(MODELS_DIR, target)
    subprocess.run(
        [sys.executable, str(PACKAGE_DIR / 'scripts' / 'generate_assets.py'),
         '--output-dir', str(target)],
        check=True, timeout=60)
    return target
