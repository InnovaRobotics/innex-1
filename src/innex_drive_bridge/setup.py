from glob import glob

from setuptools import find_packages, setup

package_name = 'innex_drive_bridge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Leo-P-1109',
    maintainer_email='344364293+Leo-P-1109@users.noreply.github.com',
    description='ROS 2 body velocity bridge with a watchdog and bounded serial writes',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'bridge_node = innex_drive_bridge.bridge_node:main'
        ],
    },
)
