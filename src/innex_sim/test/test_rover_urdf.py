import subprocess

from ament_index_python.packages import get_package_share_directory

XACRO = f'{get_package_share_directory("innex_description")}/urdf/innex_1.urdf.xacro'


def test_rover_converts_to_sdf_with_drive_plugins(tmp_path):
    urdf = tmp_path / 'innex_1.urdf'
    expanded = subprocess.run(['xacro', XACRO], capture_output=True, text=True, timeout=60)
    assert expanded.returncode == 0, expanded.stderr
    urdf.write_text(expanded.stdout)

    result = subprocess.run(['gz', 'sdf', '-p', str(urdf)], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'gz::sim::systems::DiffDrive' in result.stdout
    assert 'gz::sim::systems::JointStatePublisher' in result.stdout
