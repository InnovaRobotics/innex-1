import subprocess
import xml.etree.ElementTree as ET

import pytest
from ament_index_python.packages import get_package_share_directory

XACRO = f'{get_package_share_directory("innex_description")}/urdf/innex_1.urdf.xacro'

DRIVE_LIMITS = {
    'min_linear_velocity': -0.4,
    'max_linear_velocity': 0.4,
    'min_angular_velocity': -0.8,
    'max_angular_velocity': 0.8,
    'min_linear_acceleration': -0.5,
    'max_linear_acceleration': 0.3,
    'min_angular_acceleration': -0.6,
    'max_angular_acceleration': 0.6,
}


@pytest.fixture(scope='module')
def sdf(tmp_path_factory):
    urdf = tmp_path_factory.mktemp('rover') / 'innex_1.urdf'
    expanded = subprocess.run(['xacro', XACRO], capture_output=True, text=True, timeout=60)
    assert expanded.returncode == 0, expanded.stderr
    urdf.write_text(expanded.stdout)

    result = subprocess.run(['gz', 'sdf', '-p', str(urdf)], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


@pytest.fixture(scope='module')
def sdf_root(sdf):
    return ET.fromstring(sdf.replace('gz:expressed_in', 'expressed_in'))


def test_rover_converts_to_sdf_with_drive_plugins(sdf):
    assert 'gz::sim::systems::DiffDrive' in sdf
    assert 'gz::sim::systems::JointStatePublisher' in sdf


def test_visuals_have_colours(sdf_root):
    visuals = sdf_root.findall('.//visual')
    assert visuals
    for visual in visuals:
        assert visual.find('material/diffuse') is not None, visual.get('name')


def test_drive_limits(sdf_root):
    plugin = sdf_root.find('.//plugin[@name="gz::sim::systems::DiffDrive"]')
    for tag, value in DRIVE_LIMITS.items():
        assert [float(element.text) for element in plugin.findall(tag)] == [value], tag
