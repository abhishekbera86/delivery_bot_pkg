#!/usr/bin/env python3
"""
Integrated launch file for complete location tagging workflow:
1. Starts localization with map
2. Opens initial pose setter GUI (for setting robot position)
3. Opens location tagging GUI (for tagging delivery locations)

This provides a complete single-command workflow for location tagging.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os


def generate_launch_description():
    # Launch arguments
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.environ.get('HOME') + '/delivery_bot_pkg/data/maps/planetary_office_map.yaml',
        description='Path to map file'
    )
    
    open_initial_pose_gui_arg = DeclareLaunchArgument(
        'open_initial_pose_gui',
        default_value='true',
        description='Open initial pose GUI automatically'
    )
    
    open_location_tagging_gui_arg = DeclareLaunchArgument(
        'open_location_tagging_gui',
        default_value='true',
        description='Open location tagging GUI automatically'
    )
    
    map_file = LaunchConfiguration('map')
    open_initial_pose_gui = LaunchConfiguration('open_initial_pose_gui')
    open_location_tagging_gui = LaunchConfiguration('open_location_tagging_gui')
    
    # Find packages
    turtlebot4_navigation_pkg = FindPackageShare('turtlebot4_navigation')
    
    # Include localization launch
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
        condition=IfCondition(open_initial_pose_gui)
    )
    
    # Location tagging GUI (waits for initial pose to be set before showing)
    location_tagging_gui = Node(
        package='location_manager',
        executable='location_tag_gui',
        name='location_tagging_gui',
        output='screen',
        condition=IfCondition(open_location_tagging_gui)
    )
    
    # Delay opening initial pose GUI to let localization start first
    delayed_initial_pose_gui = TimerAction(
        period=3.0,  # Wait 3 seconds for localization
        actions=[initial_pose_gui]
    )
    
    # Start location tagging GUI immediately (it will wait for initial pose signal internally)
    # The GUI will be hidden until initial pose is set via /initial_pose_set topic
    delayed_location_tagging_gui = TimerAction(
        period=3.5,  # Wait slightly after initial pose GUI starts
        actions=[location_tagging_gui]
    )
    
    return LaunchDescription([
        map_arg,
        open_initial_pose_gui_arg,
        open_location_tagging_gui_arg,
        localization_launch,
        delayed_initial_pose_gui,
        delayed_location_tagging_gui,
    ])

