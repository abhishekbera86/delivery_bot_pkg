"""
Location Handler - Manages delivery location tagging and JSON storage
"""

import json
import os
from typing import Dict, List, Optional
from geometry_msgs.msg import PoseStamped


class LocationHandler:
    """Handles saving and loading delivery locations from JSON files"""
    
    def __init__(self, locations_file: str = None):
        """
        Initialize LocationHandler
        
        Args:
            locations_file: Path to JSON file for storing locations
                          Default: ~/delivery_bot_ws/data/locations.json
        """
        if locations_file is None:
            # Default path in gazebo_simulation data directory
            workspace_dir = os.path.expanduser("~/delivery_bot_ws/gazebo_simulation")
            data_dir = os.path.join(workspace_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            locations_file = os.path.join(data_dir, "locations.json")
        
        self.locations_file = locations_file
        self.locations: Dict = {}
        self.load_locations()
    
    def load_locations(self) -> None:
        """Load locations from JSON file"""
        if os.path.exists(self.locations_file):
            try:
                with open(self.locations_file, 'r') as f:
                    self.locations = json.load(f)
                print(f"Loaded {len(self.locations)} locations from {self.locations_file}")
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.locations_file}. Starting with empty locations.")
                self.locations = {}
        else:
            print(f"Locations file {self.locations_file} not found. Starting with empty locations.")
            self.locations = {}
    
    def save_locations(self) -> bool:
        """Save locations to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.locations_file), exist_ok=True)
            with open(self.locations_file, 'w') as f:
                json.dump(self.locations, f, indent=2)
            print(f"Saved {len(self.locations)} locations to {self.locations_file}")
            return True
        except Exception as e:
            print(f"Error saving locations: {e}")
            return False
    
    def add_location(self, name: str, pose: PoseStamped, description: str = "") -> bool:
        """
        Add a new location
        
        Args:
            name: Location name/identifier (e.g., "Loc1", "Office_Desk_1")
            pose: PoseStamped message with position and orientation
            description: Optional description of the location
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.locations:
            print(f"Warning: Location '{name}' already exists. Overwriting...")
        
        # Extract pose information
        position = pose.pose.position
        orientation = pose.pose.orientation
        
        self.locations[name] = {
            "name": name,
            "frame_id": pose.header.frame_id,
            "position": {
                "x": float(position.x),
                "y": float(position.y),
                "z": float(position.z)
            },
            "orientation": {
                "x": float(orientation.x),
                "y": float(orientation.y),
                "z": float(orientation.z),
                "w": float(orientation.w)
            },
            "description": description
        }
        
        return self.save_locations()
    
    def get_location(self, name: str) -> Optional[Dict]:
        """
        Get location by name
        
        Args:
            name: Location name
            
        Returns:
            Location dictionary or None if not found
        """
        return self.locations.get(name)
    
    def get_all_locations(self) -> Dict:
        """
        Get all locations
        
        Returns:
            Dictionary of all locations
        """
        return self.locations.copy()
    
    def get_location_names(self) -> List[str]:
        """
        Get list of all location names
        
        Returns:
            List of location names
        """
        return list(self.locations.keys())
    
    def delete_location(self, name: str) -> bool:
        """
        Delete a location
        
        Args:
            name: Location name to delete
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.locations:
            print(f"Location '{name}' not found.")
            return False
        
        del self.locations[name]
        return self.save_locations()
    
    def location_to_pose_stamped(self, name: str, frame_id: str = "map") -> Optional[PoseStamped]:
        """
        Convert stored location to PoseStamped message
        
        Args:
            name: Location name
            frame_id: Frame ID for the pose (default: "map")
            
        Returns:
            PoseStamped message or None if location not found
        """
        location = self.get_location(name)
        if location is None:
            return None
        
        pose = PoseStamped()
        pose.header.frame_id = frame_id
        pose.pose.position.x = location["position"]["x"]
        pose.pose.position.y = location["position"]["y"]
        pose.pose.position.z = location["position"]["z"]
        pose.pose.orientation.x = location["orientation"]["x"]
        pose.pose.orientation.y = location["orientation"]["y"]
        pose.pose.orientation.z = location["orientation"]["z"]
        pose.pose.orientation.w = location["orientation"]["w"]
        
        return pose

