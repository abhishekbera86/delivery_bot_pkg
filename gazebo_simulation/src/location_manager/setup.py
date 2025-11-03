from setuptools import find_packages, setup

package_name = 'location_manager'

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
    description='Package for tagging, saving, and managing delivery locations as JSON files',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'location_tag_node = location_manager.location_tag_node:main',
        ],
    },
)
