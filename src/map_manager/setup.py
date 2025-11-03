from setuptools import find_packages, setup

package_name = 'map_manager'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='turtlebot4',
    maintainer_email='turtlebot4@todo.todo',
    description='Package for managing SLAM maps: creating, saving, and loading maps for the delivery bot',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'map_saver_node = map_manager.map_saver_node:main',
        ],
    },
)
