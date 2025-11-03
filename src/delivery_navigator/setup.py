from setuptools import find_packages, setup

package_name = 'delivery_navigator'

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
    description='Navigation package for sending the robot to goal locations',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'goal_navigator_node = delivery_navigator.goal_navigator_node:main',
        ],
    },
)
