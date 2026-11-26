from glob import glob

from setuptools import find_packages, setup

package_name = 'innex_drive_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.launch.xml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Leo-P-1109',
    maintainer_email='344364293+Leo-P-1109@users.noreply.github.com',
    description='Bridge /cmd_vel commands to the Teensy 4.1 over USB serial.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'drive_bridge = innex_drive_bridge.drive_bridge:main',
        ],
    },
)
