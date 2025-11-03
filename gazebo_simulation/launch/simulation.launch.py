#!/usr/bin/env python3
"""
Launch file for running the delivery bot in Gazebo simulation.
This replaces the robot hardware with Gazebo simulation.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, FindExecutable
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    # Launch arguments
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(
            os.path.expanduser('~'),
            'delivery_bot_ws',
            'gazebo_simulation',
            'worlds',
            'office_world_8desks.world'
        ),
        description='Path to the Gazebo world file'
    )

    use_slam_arg = DeclareLaunchArgument(
        'use_slam',
        default_value='true',
        description='Whether to use SLAM (true) or localization (false)'
    )

    map_file_arg = DeclareLaunchArgument(
        'map',
        default_value='',
        description='Path to map file (required if use_slam=false)'
    )

    # Get world file path
    world_file = LaunchConfiguration('world')
    use_slam = LaunchConfiguration('use_slam')
    map_file = LaunchConfiguration('map')

    # Find TurtleBot 4 packages
    turtlebot4_bringup_pkg = FindPackageShare('turtlebot4_bringup')
    turtlebot4_navigation_pkg = FindPackageShare('turtlebot4_navigation')

    # Launch Gazebo with world
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                turtlebot4_bringup_pkg,
                'launch',
                'gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'world': world_file,
        }.items()
    )

    # SLAM launch (for mapping)
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                turtlebot4_navigation_pkg,
                'launch',
                'slam.launch.py'
            ])
        ]),
        condition=IfCondition(use_slam)
    )

    # Localization launch (for navigation with saved map)
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                turtlebot4_navigation_pkg,
                'launch',
                'localization.launch.py'
            ])
        ]),
        launch_arguments={
            'map': map_file,
        }.items(),
        condition=UnlessCondition(use_slam)
    )

    # Nav2 launch (for navigation)
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                turtlebot4_navigation_pkg,
                'launch',
                'nav2.launch.py'
            ])
        ])
    )

    return LaunchDescription([
        world_arg,
        use_slam_arg,
        map_file_arg,
        gazebo_launch,
        slam_launch,
        localization_launch,
        nav2_launch,
    ])
