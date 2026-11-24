from setuptools import find_packages, setup


package_name = 'innex_video'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/video.launch.xml']),
        ('share/' + package_name + '/config', ['config/camera_ids.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='KJdotIO',
    maintainer_email='98490529+KJdotIO@users.noreply.github.com',
    description='OAK camera H.264 video relay for Foxglove.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'video_relay = innex_video.video_relay:main',
        ],
    },
)
