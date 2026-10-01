import re
import xml.etree.ElementTree as ET

import pytest

from helpers import MODELS_DIR, WORLD

MODEL_URI = re.compile(r'model://([A-Za-z0-9_]+)')


def test_world_models_exist(models_dir):
    names = sorted(set(MODEL_URI.findall(WORLD.read_text())))
    assert names
    for name in names:
        assert (models_dir / name / 'model.config').is_file(), name
        assert (models_dir / name / 'model.sdf').is_file(), name


@pytest.mark.parametrize('name', sorted(p.name for p in MODELS_DIR.iterdir() if p.is_dir()))
def test_model_asset_uris_resolve(name, models_dir):
    model_dir = models_dir / name
    root = ET.parse(model_dir / 'model.sdf').getroot()
    checked = 0
    for tag in ('uri', 'albedo_map'):
        for element in root.iter(tag):
            uri = element.text.strip()
            if uri.startswith('model://'):
                target = models_dir / uri[len('model://'):]
            else:
                target = model_dir / uri
            assert target.is_file(), f'{uri} -> {target}'
            checked += 1
    assert checked > 0
