from glob import glob

from setuptools import find_packages, setup

package_name = 'innex_linkmeter'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='KJdotIO',
    maintainer_email='98490529+KJdotIO@users.noreply.github.com',
    description='Show how many kbps each topic sends over the Wi-Fi link to mission control.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'link_meter = innex_linkmeter.node:main',
        ],
    },
)
