#!/usr/bin/env python3
"""
Nav2 launch file for delivery bot
Uses optimized parameters for smooth spot turning and better obstacle avoidance
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Get the path to our config file
    workspace_dir = os.environ.get('HOME') + '/delivery_bot_pkg'
    nav2_config = os.path.join(workspace_dir, "config", "nav2.yaml")
    
    # Declare launch argument for params file (default to our config)
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=[nav2_config],
        description='Path to Nav2 parameters file'
    )
    
    # Get Nav2 bringup package
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    
    # Get params file from argument
    params_file = LaunchConfiguration('params_file')
    
    # Include the standard Nav2 bringup launch with our config
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                pkg_nav2_bringup,
                'launch',
                'bringup_launch.py'
            ])
        ]),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': 'false',
            'namespace': ''
        }.items()
    )
    
    return LaunchDescription([
        params_file_arg,
        nav2_bringup_launch
    ])

