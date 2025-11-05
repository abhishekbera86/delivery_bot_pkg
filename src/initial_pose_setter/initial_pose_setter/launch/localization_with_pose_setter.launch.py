#!/usr/bin/env python3
"""
Launch file for localization with initial pose setter GUI
Automatically opens GUI to set initial pose after localization starts
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    # Launch arguments
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.environ.get('HOME') + '/delivery_bot_pkg/data/maps/planetary_office_map.yaml',
        description='Path to map file'
    )
    
    open_gui_arg = DeclareLaunchArgument(
        'open_gui',
        default_value='true',
        description='Open initial pose GUI automatically'
    )
    
    map_file = LaunchConfiguration('map')
    open_gui = LaunchConfiguration('open_gui')
    
    # Find packages
    turtlebot4_navigation_pkg = FindPackageShare('turtlebot4_navigation')
    
    # Include localization launch
    from launch.actions import IncludeLaunchDescription
    from launch.launch_description_sources import PythonLaunchDescriptionSource
    
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                turtlebot4_navigation_pkg,
                'launch',
                'localization.launch.py'
            ])
        ]),
        launch_arguments={'map': map_file}.items()
    )
    
    # Initial pose GUI (opens after delay to let localization start)
    initial_pose_gui = Node(
        package='initial_pose_setter',
        executable='initial_pose_gui',
        name='initial_pose_gui',
        output='screen',
        condition=IfCondition(open_gui)
    )
    
    # Delay opening GUI to let localization start first
    delayed_gui = TimerAction(
        period=3.0,  # Wait 3 seconds
        actions=[initial_pose_gui]
    )
    
    return LaunchDescription([
        map_arg,
        open_gui_arg,
        localization_launch,
        delayed_gui,
    ])

