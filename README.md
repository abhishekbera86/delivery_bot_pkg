# Mapping and Location Tagging Project

A complete ROS2 Jazzy project for TurtleBot 4 mapping and location tagging. This system enables SLAM mapping and location tagging for indoor environments.

## 🎯 Overview

The Mapping and Location Tagging Project provides a complete solution for creating maps and tagging locations using TurtleBot 4. It features a **unified GUI** that handles all operations:

- **Unified Mapping & Tagging GUI** - Single GUI for mapping, location tagging, and map saving
- **SLAM Mapping** - Create detailed maps of indoor environments
- **Location Tagging** - Tag locations during mapping (no initial pose needed!)
- **Persistent Storage** - Save maps and locations for repeated use
- **Map-Aware System** - Locations are automatically associated with their corresponding maps

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

**Single unified launch - one GUI handles everything!**

```bash
# On TurtleBot 4 Pi:
ros2 launch turtlebot4_bringup robot.launch.py

# On Host Computer (Terminal 1):
ros2 launch launch/mapping_with_tagging.launch.py

# On Host Computer (Terminal 2 - for teleoperation):
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**In the Unified Mapping & Tagging GUI:**
1. Enter map name - JSON filename automatically matches map name
2. Tag locations as you map - Enter name, click "Save Location"
3. Save map when done - Enter map name, click "Save Map"
4. Click "Exit" when finished

**Result:**
- Map saved to: `~/delivery_bot_pkg/data/maps/{map_name}.yaml`
- Locations saved to: `~/delivery_bot_pkg/data/locations/{map_name}.json`

**See:** `docs/MAPPING_AND_LOCATION_TAGGING.md` for complete guide

## 📁 Project Structure

```
delivery_bot_pkg/
├── src/
│   ├── map_manager/              # SLAM map management
│   ├── location_manager/          # Location tagging and storage
│   │   └── mapping_and_tagging_gui.py  # Unified Mapping & Tagging GUI
│   └── initial_pose_setter/      # Initial pose setting GUI
├── launch/
│   ├── mapping_with_tagging.launch.py  # Unified mapping launch
│   └── localization_with_location_tagging.launch.py  # Localization + tagging
├── data/
│   ├── maps/                      # Saved SLAM maps
│   └── locations/                 # Tagged locations (JSON files)
└── docs/                          # Documentation
```

## 📦 Packages

| Package | Purpose | Usage |
|---------|---------|-------|
| `map_manager` | Save SLAM maps | Runs automatically with unified launch |
| `location_manager` | Tag locations | Unified GUI: `ros2 launch launch/mapping_with_tagging.launch.py` |
| `initial_pose_setter` | Set initial pose | Used for location tagging after map is loaded |

## 🔄 Workflows

### Workflow 1: Map Creation with Location Tagging
**Single unified launch - one GUI handles everything!**
- Start unified launch: `ros2 launch launch/mapping_with_tagging.launch.py`
- Enter map name (JSON filename auto-updates to match)
- Tag locations as you map
- Save map from GUI (map and locations saved together)
- Exit when done

**Result:** 
- Map in `data/maps/{map_name}.yaml`
- Locations in `data/locations/{map_name}.json`

**See:** `docs/MAPPING_AND_LOCATION_TAGGING.md`

## 📚 Documentation

- **[docs/MAPPING_AND_LOCATION_TAGGING.md](docs/MAPPING_AND_LOCATION_TAGGING.md)** - Unified mapping and tagging guide
- **[docs/TIME_SYNCHRONIZATION.md](docs/TIME_SYNCHRONIZATION.md)** - Clock sync setup (CRITICAL!)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference
- **[INSTALLATION.md](INSTALLATION.md)** - Installation instructions

## ⚠️ Important Notes

1. **Clock Synchronization**: CRITICAL - Without clock sync, SLAM will fail. See `docs/TIME_SYNCHRONIZATION.md`
2. **Unified Mapping & Tagging GUI**: One GUI handles mapping, location tagging, and map saving
3. **Location Tagging During SLAM**: Tag locations during SLAM mapping - no initial pose needed!
4. **Map-Aware System**: Locations are automatically associated with their corresponding maps (same filename)
5. **Auto JSON Filename**: When you enter a map name, the JSON filename automatically matches
6. **Data Storage**: Maps saved to `data/maps/`, locations saved to `data/locations/`

## 🗂️ Data Storage

- **Maps**: `~/delivery_bot_pkg/data/maps/` (`.yaml` + `.pgm`)
- **Locations**: `~/delivery_bot_pkg/data/locations/` (JSON files)

## 📝 License

Apache-2.0

## 👤 Author

Abhishek
