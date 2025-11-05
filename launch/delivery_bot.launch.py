#!/usr/bin/env python3
"""
Unified launch file for delivery bot application
Launches the main GUI which handles all node management
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for delivery bot main GUI"""
    
    # Main GUI node (handles all other node launching)
    delivery_bot_main_gui = Node(
        package='delivery_bot_gui',
        executable='delivery_bot_main_gui',
        name='delivery_bot_main_gui',
        output='screen'
    )
    
    return LaunchDescription([
        delivery_bot_main_gui,
    ])

