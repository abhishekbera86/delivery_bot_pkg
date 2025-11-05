#!/usr/bin/env python3
"""
Unified launch file for mapping and location tagging
Starts SLAM, map saver node, and unified GUI all in one
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    """Generate launch description for unified mapping and tagging"""
    
    # Launch arguments
    map_saver_enabled_arg = DeclareLaunchArgument(
        'map_saver_enabled',
        default_value='true',
        description='Enable map saver node'
    )
    
    map_saver_enabled = LaunchConfiguration('map_saver_enabled')
    
    # Find packages
    turtlebot4_navigation_pkg = FindPackageShare('turtlebot4_navigation')
    
    # Include SLAM launch
    from launch.actions import IncludeLaunchDescription
    from launch.launch_description_sources import PythonLaunchDescriptionSource
    from launch.substitutions import PathJoinSubstitution
    
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                turtlebot4_navigation_pkg,
                'launch',
                'slam.launch.py'
            ])
        ])
    )
    
    # Map saver node (runs in background)
    map_saver_node = Node(
        package='map_manager',
        executable='map_saver_node',
        name='map_saver_node',
        output='screen',
        condition=IfCondition(map_saver_enabled)
    )
    
    # Unified Mapping and Tagging GUI
    mapping_tagging_gui = Node(
        package='location_manager',
        executable='mapping_and_tagging_gui',
        name='mapping_and_tagging_gui',
        output='screen'
    )
    
    # Delay GUI to let SLAM start first
    delayed_gui = TimerAction(
        period=3.0,  # Wait 3 seconds for SLAM to initialize
        actions=[mapping_tagging_gui]
    )
    
    return LaunchDescription([
        map_saver_enabled_arg,
        slam_launch,
        map_saver_node,
        delayed_gui,
    ])

