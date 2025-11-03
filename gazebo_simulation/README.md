# Delivery Bot Project - Gazebo Simulation

A ROS2 Jazzy project for TurtleBot 4 delivery automation **in Gazebo simulation**. This project provides a complete system for mapping indoor environments, tagging delivery locations, and navigating to selected destinations using Gazebo simulation instead of physical hardware.

## Project Structure

```
gazebo_simulation/
├── src/
│   ├── delivery_bot/              # Main coordination package
│   ├── map_manager/                # SLAM map management
│   ├── location_manager/           # Location tagging and JSON storage
│   ├── delivery_bot_gui/          # GUI for goal selection
│   └── delivery_navigator/         # Navigation to goal locations
├── worlds/
│   └── office_world_8desks.world  # Gazebo world with 8 desks
├── src/
│   └── simulation/                # Simulation launch package
│       └── simulation/launch/
│           └── simulation.launch.py  # Main simulation launch file
├── data/
│   ├── maps/                       # Saved SLAM maps
│   └── locations.json              # Tagged delivery locations
├── docs/                           # Documentation guides
└── README.md                       # This file
```

## System Architecture

This simulation project runs **entirely on a single computer** using Gazebo for the robot simulation:

### Simulation Setup

**Runs on:** Single computer with ROS2 Jazzy

**Components:**
- **Gazebo Simulation** - TurtleBot 4 robot in Gazebo world
- **SLAM and Mapping** - SLAM Toolbox for creating maps
- **Navigation Stack** - Nav2 for autonomous navigation
- **Delivery Bot Nodes:**
  - GUI (`delivery_bot_gui`) - Graphical interface for selecting destinations
  - Navigator (`delivery_navigator`) - Navigation to goal locations
  - Location manager (`location_manager`) - Tag and store delivery locations
  - Map manager (`map_manager`) - Save SLAM maps

**Launch Files:**
- `ros2 launch simulation simulation.launch.py` - Start complete simulation with SLAM
- `ros2 launch simulation simulation.launch.py use_slam:=false map:=~/delivery_bot_ws/gazebo_simulation/data/maps/office_map.yaml` - Start simulation with saved map
- `ros2 run delivery_bot_gui delivery_gui` - Launch GUI
- `ros2 run delivery_navigator goal_navigator_node` - Start navigator
- `ros2 run location_manager location_tag_node` - Start location tagger
- `ros2 run map_manager map_saver_node` - Start map saver

## System Requirements

- **OS**: Ubuntu 24.04
- **ROS2**: Jazzy (desktop installation)
- **Gazebo**: Gazebo Classic (gazebo11) or Gazebo Fortress
- **Dependencies**: Nav2, SLAM Toolbox, TurtleBot 4 packages

## World Description

The simulation uses a custom world file (`office_world_8desks.world`) featuring:
- A 20x20 meter office room with walls
- **8 desks** positioned in a grid layout for delivery location tagging:
  - Desk 1: Bottom Left (-6, -6)
  - Desk 2: Bottom Center (0, -6)
  - Desk 3: Bottom Right (6, -6)
  - Desk 4: Center Left (-6, 0)
  - Desk 5: Center Right (6, 0)
  - Desk 6: Top Left (-6, 6)
  - Desk 7: Top Center (0, 6)
  - Desk 8: Top Right (6, 6)

## Packages Overview

### 1. map_manager
Manages SLAM maps - saving maps created during mapping sessions.

**Services Used:**
- `/map_saver/save_map` (Nav2 map saver service)
- `/slam_toolbox/save_map` (SLAM Toolbox map saver service)

**Topics:**
- `/save_map` (std_msgs/String) - Publish map name to save
- `/map_save_status` (std_msgs/String) - Status of map save operation

**Usage:**
```bash
ros2 run map_manager map_saver_node

# In another terminal, save a map:
ros2 topic pub /save_map std_msgs/String "data: 'office_map'"
```

### 2. location_manager
Tags and manages delivery locations. Saves locations to JSON file for persistence.

**Topics:**
- `/tag_location` (std_msgs/String) - Publish location name to tag current position
- `/location_tag_status` (std_msgs/String) - Status of tagging operation

**Data Format:**
Locations are saved in `~/delivery_bot_ws/gazebo_simulation/data/locations.json`:
```json
{
  "Desk1": {
    "name": "Desk1",
    "frame_id": "map",
    "position": {"x": -6.0, "y": -6.0, "z": 0.0},
    "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
    "description": "Tagged location: Desk1"
  }
}
```

**Usage:**
```bash
ros2 run location_manager location_tag_node

# In another terminal, tag current position:
ros2 topic pub /tag_location std_msgs/String "data: 'Desk1'"
```

### 3. delivery_bot_gui
Graphical user interface for selecting delivery locations. Provides a simple GUI to:
- View all available locations
- Select a target location
- Send navigation goals
- Monitor navigation status

**Topics:**
- `/delivery_goal` (std_msgs/String) - Publishes selected location name
- `/navigation_status` (std_msgs/String) - Subscribes to navigation status

**Usage:**
```bash
ros2 run delivery_bot_gui delivery_gui
```

### 4. delivery_navigator
Handles navigation to goal locations using Nav2. Reads locations from location_manager and sends navigation goals.

**Action Clients:**
- `navigate_to_pose` (Nav2 action)

**Topics:**
- `/delivery_goal` (std_msgs/String) - Subscribes to goal location names
- `/navigation_status` (std_msgs/String) - Publishes navigation status

**Usage:**
```bash
ros2 run delivery_navigator goal_navigator_node
```

## Installation

> **📦 For a complete installation guide with all dependencies, see `INSTALLATION.md`**

1. **Navigate to simulation directory:**
   ```bash
   cd ~/delivery_bot_ws/gazebo_simulation
   ```

2. **Build the workspace:**
   ```bash
   colcon build
   source install/setup.bash
   ```

3. **Install dependencies:**
   See `INSTALLATION.md` for complete dependency installation.

## Quick Start

### Step 1: Build Workspace
```bash
cd ~/delivery_bot_ws/gazebo_simulation
colcon build
source install/setup.bash
```

### Step 2: Start Simulation with SLAM (for mapping)
```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 launch simulation simulation.launch.py
```

### Step 3: Create a Map
In a new terminal:
```bash
source ~/delivery_bot_ws/gazebo_simulation/install/setup.bash
ros2 run map_manager map_saver_node
```

In another terminal:
```bash
# Teleoperate the robot in Gazebo to explore
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Save the map when done exploring
ros2 topic pub /save_map std_msgs/String "data: 'office_map'"
```

### Step 4: Tag Locations
After creating a map, restart simulation with localization:
```bash
# Stop the previous simulation (Ctrl+C)
# Start with saved map
ros2 launch simulation simulation.launch.py use_slam:=false map:=~/delivery_bot_ws/gazebo_simulation/data/maps/office_map.yaml
```

In new terminals:
```bash
# Start location tagger
ros2 run location_manager location_tag_node

# Teleoperate to each desk and tag it
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Tag each desk:
ros2 topic pub /tag_location std_msgs/String "data: 'Desk1'"
ros2 topic pub /tag_location std_msgs/String "data: 'Desk2'"
# ... repeat for all 8 desks
```

### Step 5: Use Delivery Bot
Start navigation:
```bash
# Start navigator
ros2 run delivery_navigator goal_navigator_node

# Start GUI
ros2 run delivery_bot_gui delivery_gui
```

Select a location from the GUI and click "Go to Location" to navigate autonomously!

## Documentation

For comprehensive step-by-step guides, see the **docs/** directory:

- **[docs/MAPPING_GUIDE.md](docs/MAPPING_GUIDE.md)** - Complete guide for creating SLAM maps in simulation
- **[docs/LOCATION_TAGGING_GUIDE.md](docs/LOCATION_TAGGING_GUIDE.md)** - How to tag the 8 desk locations
- **[docs/DELIVERY_BOT_GUIDE.md](docs/DELIVERY_BOT_GUIDE.md)** - How to use the delivery bot system

## Data Storage

- **Maps**: Saved in `~/delivery_bot_ws/gazebo_simulation/data/maps/`
- **Locations**: Saved in `~/delivery_bot_ws/gazebo_simulation/data/locations.json`

## Troubleshooting

### Gazebo Not Starting
- Ensure Gazebo is installed: `sudo apt install gazebo11 libgazebo11-dev`
- Check that world file exists: `ls ~/delivery_bot_ws/gazebo_simulation/worlds/office_world_8desks.world`

### Map Saver Not Working
- Ensure Nav2 map_saver service is available: `ros2 service list | grep map_saver`
- Check that SLAM/mapping is active and has created a map

### Location Tagging Fails
- Verify TF transform from `base_link` to `map` is available: `ros2 run tf2_ros tf2_echo map base_link`
- Ensure robot localization is active (AMCL or SLAM)

### Navigation Not Starting
- Verify Nav2 action server is running: `ros2 action list | grep navigate_to_pose`
- Check that the map is loaded correctly
- Ensure locations are in the correct frame (typically "map")

### GUI Not Showing Locations
- Click "Refresh Locations" button
- Verify `locations.json` file exists and has valid JSON
- Check file permissions in `~/delivery_bot_ws/gazebo_simulation/data/`

## Differences from Real Hardware

This simulation version differs from the real hardware setup:

1. **No Physical Robot Required** - Everything runs in Gazebo
2. **Single Computer** - No need for Raspberry Pi or distributed setup
3. **World File** - Uses custom `office_world_8desks.world` instead of TurtleBot 4 official world
4. **Simplified Setup** - No network configuration or hardware dependencies
5. **Data Paths** - All data stored in `gazebo_simulation/data/` directory

## License

Apache-2.0

## Author

turtlebot4