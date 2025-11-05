#!/usr/bin/env python3
"""
Launch file for GUI-based location tagging
Opens a colorful GUI for tagging delivery locations
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for location tagging GUI"""
    
    # Location tagging GUI node
    location_tag_gui = Node(
        package='location_manager',
        executable='location_tag_gui',
        name='location_tag_gui',
        output='screen',
        parameters=[]
    )
    
    return LaunchDescription([
        location_tag_gui,
    ])

