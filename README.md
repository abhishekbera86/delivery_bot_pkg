# Delivery Bot Project

A ROS2 Jazzy project for TurtleBot 4 delivery automation. This project provides a complete system for mapping indoor environments, tagging delivery locations, and navigating to selected destinations.

## Quick Start

### 1. Start Robot Hardware

**📍 On: TurtleBot 4 (Raspberry Pi)**

```bash
ros2 launch turtlebot4_bringup robot.launch.py
```

### 2. Load Map and Set Initial Pose

**📍 On: Host Computer (Intel NUC)**

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 launch initial_pose_setter localization_with_pose_setter.launch.py map:=$HOME/delivery_bot_ws/data/maps/planetary_office_map.yaml
```

**This will:**
- Load the saved map
- Start AMCL localization
- **Automatically open Initial Pose GUI** (after 3 seconds)

**In the Initial Pose GUI:**
- Select a tagged location from dropdown (if available)
- OR enter position manually (X, Y, Yaw)
- OR click "Open RViz2" to set pose visually
- Click the appropriate button to set initial pose

### 3. Start Nav2 Navigation

```bash
ros2 launch turtlebot4_navigation nav2.launch.py
```

### 4. Start Delivery Navigator

```bash
ros2 run delivery_navigator goal_navigator_node
```

### 5. Start Delivery GUI

```bash
ros2 run delivery_bot_gui delivery_gui
```

**In the GUI:**
- Select a location from dropdown
- Click "Go to Location"
- Robot navigates autonomously!

## Project Structure

```
delivery_bot_ws/
├── src/
│   ├── delivery_bot/              # Main coordination package
│   ├── map_manager/                # SLAM map management
│   ├── location_manager/           # Location tagging and JSON storage
│   ├── delivery_bot_gui/          # GUI for goal selection
│   ├── delivery_navigator/         # Navigation to goal locations
│   └── initial_pose_setter/       # GUI for setting initial pose
└── data/
    ├── maps/                       # Saved SLAM maps
    └── locations.json              # Tagged delivery locations
```

## Key Features

1. **Easy Initial Pose Setting** - GUI tool opens automatically with localization
2. **Location Tagging** - Tag delivery locations and save to JSON
3. **Graphical Interface** - Simple GUI to select destinations
4. **Autonomous Navigation** - Nav2 integration for path planning

## Packages Overview

### initial_pose_setter
**GUI tool for setting initial pose for AMCL**
- Opens automatically with localization launch file
- Shows available tagged locations
- Allows manual entry or RViz2 visual method
- **Usage:** Automatically opens, or manually: `ros2 run initial_pose_setter initial_pose_gui`

### map_manager
**Manages SLAM maps - saving maps created during mapping**
- **Usage:** `ros2 run map_manager map_saver_node`

### location_manager
**Tags and manages delivery locations**
- **Usage:** `ros2 run location_manager location_tag_node`

### delivery_bot_gui
**Graphical interface for selecting delivery locations**
- **Usage:** `ros2 run delivery_bot_gui delivery_gui`

### delivery_navigator
**Handles navigation to goal locations using Nav2**
- **Usage:** `ros2 run delivery_navigator goal_navigator_node`

## Installation

See `INSTALLATION.md` for complete dependency installation.

**⚠️ IMPORTANT:** Before starting, ensure clock synchronization is set up. The Raspberry Pi doesn't have a battery-backed clock - see `INSTALLATION.md` Step 0 or `docs/TIME_SYNCHRONIZATION.md` for setup.

## Documentation

For detailed guides, see the **docs/** directory:

- **[docs/TIME_SYNCHRONIZATION.md](docs/TIME_SYNCHRONIZATION.md)** - Setting up clock synchronization (CRITICAL)
- **[docs/MAPPING_GUIDE.md](docs/MAPPING_GUIDE.md)** - Creating SLAM maps
- **[docs/LOCATION_TAGGING_GUIDE.md](docs/LOCATION_TAGGING_GUIDE.md)** - Tagging delivery locations
- **[docs/DELIVERY_BOT_GUIDE.md](docs/DELIVERY_BOT_GUIDE.md)** - Using the delivery bot system

## Data Storage

- **Maps**: `~/delivery_bot_ws/data/maps/`
- **Locations**: `~/delivery_bot_ws/data/locations.json`

## License

Apache-2.0

## Author

turtlebot4
