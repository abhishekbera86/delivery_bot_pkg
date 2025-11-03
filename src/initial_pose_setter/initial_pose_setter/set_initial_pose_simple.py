#!/usr/bin/env python3
"""
Simple command-line tool to set initial pose using a location from locations.json
Usage: python3 set_initial_pose_simple.py [location_name]
"""

import sys
import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
import json
import os

def set_initial_pose_from_location(location_name):
    """Set initial pose from a location in locations.json"""
    locations_file = os.path.expanduser("~/delivery_bot_ws/data/locations.json")
    
    if not os.path.exists(locations_file):
        print(f"ERROR: Locations file not found: {locations_file}")
        return False
    
    # Load locations
    with open(locations_file, 'r') as f:
        locations = json.load(f)
    
    if location_name not in locations:
        print(f"ERROR: Location '{location_name}' not found in {locations_file}")
        print(f"Available locations: {list(locations.keys())}")
        return False
    
    # Get location data
    loc = locations[location_name]
    
    # Initialize ROS2
    rclpy.init()
    node = rclpy.create_node('set_initial_pose')
    pub = node.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
    
    # Create message
    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = 'map'
    msg.header.stamp = node.get_clock().now().to_msg()  # CRITICAL: Set current timestamp
    msg.pose.pose.position.x = float(loc['position']['x'])
    msg.pose.pose.position.y = float(loc['position']['y'])
    msg.pose.pose.position.z = float(loc['position']['z'])
    msg.pose.pose.orientation.x = float(loc['orientation']['x'])
    msg.pose.pose.orientation.y = float(loc['orientation']['y'])
    msg.pose.pose.orientation.z = float(loc['orientation']['z'])
    msg.pose.pose.orientation.w = float(loc['orientation']['w'])
    
    # Covariance
    msg.pose.covariance = [
        0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891945200942
    ]
    
    # Wait for publisher to be ready
    import time
    time.sleep(0.5)
    
    # Publish
    pub.publish(msg)
    print(f"SUCCESS: Initial pose set using location '{location_name}'")
    print(f"  Position: x={loc['position']['x']}, y={loc['position']['y']}")
    
    # Small delay to ensure message is sent
    rclpy.spin_once(node, timeout_sec=0.5)
    
    node.destroy_node()
    rclpy.shutdown()
    return True

def list_locations():
    """List all available locations"""
    locations_file = os.path.expanduser("~/delivery_bot_ws/data/locations.json")
    
    if not os.path.exists(locations_file):
        print(f"ERROR: Locations file not found: {locations_file}")
        return
    
    with open(locations_file, 'r') as f:
        locations = json.load(f)
    
    print("Available locations:")
    for name in locations.keys():
        loc = locations[name]
        print(f"  - {name}: ({loc['position']['x']}, {loc['position']['y']})")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        location_name = sys.argv[1]
        if location_name == '--list' or location_name == '-l':
            list_locations()
        else:
            set_initial_pose_from_location(location_name)
    else:
        print("Usage: python3 set_initial_pose_simple.py <location_name>")
        print("       python3 set_initial_pose_simple.py --list  (to list available locations)")
        list_locations()

