from setuptools import find_packages, setup
import os

package_name = 'initial_pose_setter'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files
        (os.path.join('share', package_name, 'launch'),
         [os.path.join('initial_pose_setter', 'launch', 'localization_with_pose_setter.launch.py')]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='turtlebot4',
    maintainer_email='turtlebot4@todo.todo',
    description='GUI tool for setting initial pose for AMCL localization',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'initial_pose_gui = initial_pose_setter.initial_pose_gui:main',
        ],
    },
)

