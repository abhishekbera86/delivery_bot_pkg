# Delivery Bot Project

A complete ROS2 Jazzy project for TurtleBot 4 delivery automation. This system enables autonomous indoor navigation by combining SLAM mapping, location tagging, and path planning for automated delivery operations.

## 🎯 Overview

The Delivery Bot Project provides a complete solution for autonomous indoor delivery using TurtleBot 4. It features:

- **Unified Mapping GUI** - Single GUI for mapping, location tagging, and map saving
- **SLAM Mapping** - Create detailed maps of indoor environments
- **Location Tagging** - Tag delivery locations during mapping (no initial pose needed!)
- **Autonomous Navigation** - Navigate to tagged locations using Nav2
- **Persistent Storage** - Save maps and locations for repeated use

## 🚀 Quick Start

### Prerequisites

- TurtleBot 4 robot hardware
- Raspberry Pi with ROS2 Jazzy
- Host Computer (Intel NUC) with ROS2 Jazzy, Nav2, and SLAM Toolbox
- Both systems on the same network
- **Clock synchronization set up** (CRITICAL - see `docs/TIME_SYNCHRONIZATION.md`)

### Installation

```bash
cd ~/delivery_bot_pkg
colcon build
source install/setup.bash
```

See `INSTALLATION.md` for complete setup instructions.

### Basic Usage

#### Workflow 1: Map Creation with Location Tagging (First Time)

**Single unified launch - everything in one command!**

```bash
# On TurtleBot 4 Pi:
ros2 launch turtlebot4_bringup robot.launch.py

# On Host Computer (Terminal 1):
ros2 launch launch/mapping_with_tagging.launch.py

# On Host Computer (Terminal 2 - for teleoperation):
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**In the Unified GUI:**
1. Set JSON filename (optional, default: "locations.json")
2. Tag locations as you map
3. Enter map name and click "Save Map" when done
4. Click "Exit" when finished

**See:** `docs/MAPPING_AND_LOCATION_TAGGING.md` for complete guide

#### Workflow 2: Delivery Bot Navigation (Daily Use)

```bash
# On TurtleBot 4 Pi:
ros2 launch turtlebot4_bringup robot.launch.py

# On Host Computer:
ros2 launch launch/localization_with_location_tagging.launch.py map:=$HOME/delivery_bot_pkg/data/maps/your_map_name.yaml
ros2 launch launch/nav2.launch.py
ros2 run delivery_navigator goal_navigator_node
ros2 run delivery_bot_gui delivery_gui
```

**See:** `docs/DELIVERY_BOT_GUIDE.md` for complete guide

## 📁 Project Structure

```
delivery_bot_pkg/
├── src/
│   ├── map_manager/              # SLAM map management
│   ├── location_manager/          # Location tagging and storage
│   │   └── mapping_and_tagging_gui.py  # Unified GUI
│   ├── initial_pose_setter/      # Initial pose setting GUI
│   ├── delivery_bot_gui/         # Delivery location selection GUI
│   └── delivery_navigator/       # Navigation to goal locations
├── launch/
│   ├── mapping_with_tagging.launch.py  # Unified mapping launch
│   ├── nav2.launch.py            # Nav2 navigation stack
│   └── localization_with_location_tagging.launch.py  # Localization + tagging
├── data/
│   ├── maps/                      # Saved SLAM maps
│   └── locations/                 # Tagged delivery locations (JSON files)
└── docs/                          # Documentation
```

## 📦 Packages

| Package | Purpose | Usage |
|---------|---------|-------|
| `map_manager` | Save SLAM maps | Runs automatically with unified launch |
| `location_manager` | Tag locations | Unified GUI: `ros2 launch launch/mapping_with_tagging.launch.py` |
| `initial_pose_setter` | Set initial pose | Opens automatically with localization |
| `delivery_bot_gui` | Select destinations | `ros2 run delivery_bot_gui delivery_gui` |
| `delivery_navigator` | Handle navigation | `ros2 run delivery_navigator goal_navigator_node` |

## 🔄 Workflows

### Workflow 1: Map Creation with Location Tagging
**Single unified launch - one GUI handles everything!**
- Start unified launch: `ros2 launch launch/mapping_with_tagging.launch.py`
- Set JSON filename in GUI (optional)
- Tag locations as you map
- Save map from GUI
- Exit when done

**Result:** Map in `data/maps/`, locations in `data/locations/`

**See:** `docs/MAPPING_AND_LOCATION_TAGGING.md`

### Workflow 2: Delivery Bot Navigation
Use saved map and locations for autonomous navigation. Set initial pose using tagged locations (no RViz needed!).

**See:** `docs/DELIVERY_BOT_GUIDE.md`

## 📚 Documentation

- **[docs/MAPPING_AND_LOCATION_TAGGING.md](docs/MAPPING_AND_LOCATION_TAGGING.md)** - Unified mapping and tagging guide
- **[docs/DELIVERY_BOT_GUIDE.md](docs/DELIVERY_BOT_GUIDE.md)** - Delivery bot navigation guide
- **[docs/TIME_SYNCHRONIZATION.md](docs/TIME_SYNCHRONIZATION.md)** - Clock sync setup (CRITICAL!)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference
- **[INSTALLATION.md](INSTALLATION.md)** - Installation instructions

## ⚠️ Important Notes

1. **Clock Synchronization**: CRITICAL - Without clock sync, navigation will fail. See `docs/TIME_SYNCHRONIZATION.md`
2. **Unified GUI**: One GUI handles mapping, location tagging, and map saving - no need for multiple terminals!
3. **Location Tagging During SLAM**: Tag locations during SLAM mapping - no initial pose needed!
4. **Data Storage**: Maps saved to `data/maps/`, locations saved to `data/locations/`

## 🗂️ Data Storage

- **Maps**: `~/delivery_bot_pkg/data/maps/` (`.yaml` + `.pgm`)
- **Locations**: `~/delivery_bot_pkg/data/locations/` (JSON files)

## 📝 License

Apache-2.0

## 👤 Author

Abhishek
