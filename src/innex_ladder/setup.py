from glob import glob
import os

from setuptools import find_packages, setup


package_name = 'innex_ladder'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
         glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sohafz8',
    maintainer_email='149010044+sohafz8@users.noreply.github.com',
    description='ROS 2 bucket ladder controller with gamepad input and a fake actuator',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ladder_joy = innex_ladder.ladder_joy:main',
            'fake_ladder = innex_ladder.fake_ladder:main',
        ],
    },
)
