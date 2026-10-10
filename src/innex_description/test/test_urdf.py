import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import xacro

URDF_XACRO = Path(__file__).resolve().parent.parent / 'urdf' / 'innex_1.urdf.xacro'


@pytest.fixture(scope='module')
def urdf_text():
    return xacro.process_file(str(URDF_XACRO)).toxml()


@pytest.fixture(scope='module')
def robot(urdf_text):
    return ET.fromstring(urdf_text)


def floats(text):
    return [float(value) for value in text.split()]


def drive_joint_names(robot):
    plugin = robot.find('gazebo/plugin[@name="gz::sim::systems::DiffDrive"]')
    return {element.text for tag in ('left_joint', 'right_joint') for element in plugin.iter(tag)}


def test_check_urdf(urdf_text, tmp_path):
    urdf = tmp_path / 'innex_1.urdf'
    urdf.write_text(urdf_text)
    result = subprocess.run(['check_urdf', str(urdf)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


def test_root_link_is_base_link(robot):
    links = {link.get('name') for link in robot.findall('link')}
    children = {joint.find('child').get('link') for joint in robot.findall('joint')}
    assert links - children == {'base_link'}


def test_wheel_joints(robot):
    continuous = [joint for joint in robot.findall('joint') if joint.get('type') == 'continuous']
    assert {joint.get('name') for joint in continuous} == drive_joint_names(robot)

    links = {link.get('name'): link for link in robot.findall('link')}
    for joint in continuous:
        assert floats(joint.find('axis').get('xyz')) == [0, 1, 0], joint.get('name')
        radius = float(links[joint.find('child').get('link')].find('collision/geometry/cylinder').get('radius'))
        assert floats(joint.find('origin').get('xyz'))[2] == pytest.approx(radius), joint.get('name')


def test_drive_limits_are_valid(robot):
    plugin = robot.find('gazebo/plugin[@name="gz::sim::systems::DiffDrive"]')
    for quantity in ('linear_velocity', 'angular_velocity', 'linear_acceleration', 'angular_acceleration'):
        lower, upper = (plugin.findall(f'{bound}_{quantity}') for bound in ('min', 'max'))
        assert len(lower) == len(upper) == 1, quantity
        assert float(lower[0].text) < 0 < float(upper[0].text), quantity


def test_inertials_are_physical(robot):
    inertials = [(link.get('name'), link.find('inertial')) for link in robot.findall('link')
                 if link.find('inertial') is not None]
    assert inertials
    for name, inertial in inertials:
        assert float(inertial.find('mass').get('value')) > 0, name
        inertia = inertial.find('inertia')
        for axis in ('ixx', 'iyy', 'izz'):
            assert float(inertia.get(axis)) > 0, f'{name} {axis}'
