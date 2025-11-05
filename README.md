# Delivery Bot Project

A complete ROS2 Jazzy project for TurtleBot 4 delivery automation. This system enables autonomous indoor navigation by combining SLAM mapping, location tagging, and path planning for automated delivery operations.

## 🎯 Overview

The Delivery Bot Project provides a complete solution for autonomous indoor delivery using TurtleBot 4. It features **two unified GUIs** that handle all operations:

- **Unified Mapping & Tagging GUI** - Single GUI for mapping, location tagging, and map saving
- **Unified Delivery Bot GUI** - Single GUI for map selection, localization, initial pose setting, and navigation
- **SLAM Mapping** - Create detailed maps of indoor environments
- **Location Tagging** - Tag delivery locations during mapping (no initial pose needed!)
- **Autonomous Navigation** - Navigate to tagged locations using Nav2
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

#### Workflow 2: Delivery Bot Navigation (Daily Use)

**Single unified launch - one GUI handles everything!**

```bash
# On TurtleBot 4 Pi:
ros2 launch turtlebot4_bringup robot.launch.py

# On Host Computer (ONE COMMAND):
ros2 launch launch/delivery_bot.launch.py
```

**In the Unified Delivery Bot GUI:**
1. Select map from dropdown
2. Click "Load Map and Start Localization"
3. Set initial pose (use tagged location or manual entry)
4. Select location and click "Go to Location"
5. Click "Exit" when done

**The GUI automatically:**
- Loads the selected map
- Starts localization (AMCL)
- Starts Nav2 navigation stack
- Starts delivery navigator
- Shows locations associated with the selected map

**See:** `docs/DELIVERY_BOT_GUIDE.md` for complete guide

## 📁 Project Structure

```
delivery_bot_pkg/
├── src/
│   ├── map_manager/              # SLAM map management
│   ├── location_manager/          # Location tagging and storage
│   │   └── mapping_and_tagging_gui.py  # Unified Mapping & Tagging GUI
│   ├── initial_pose_setter/      # Initial pose setting GUI
│   ├── delivery_bot_gui/         # Delivery bot GUI
│   │   └── delivery_bot_main_gui.py  # Unified Delivery Bot GUI
│   └── delivery_navigator/       # Navigation to goal locations
├── launch/
│   ├── mapping_with_tagging.launch.py  # Unified mapping launch
│   ├── delivery_bot.launch.py   # Unified delivery bot launch
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
| `initial_pose_setter` | Set initial pose | Integrated into delivery bot GUI |
| `delivery_bot_gui` | Complete delivery workflow | Unified GUI: `ros2 launch launch/delivery_bot.launch.py` |
| `delivery_navigator` | Handle navigation | Runs automatically with delivery bot GUI |

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

### Workflow 2: Delivery Bot Navigation
**Single unified launch - one GUI handles everything!**
- Start unified launch: `ros2 launch launch/delivery_bot.launch.py`
- Select map from dropdown
- GUI automatically loads map and starts localization
- Set initial pose (use tagged location or manual entry)
- Select location and navigate

**The GUI automatically manages:**
- Map loading
- Localization (AMCL)
- Nav2 navigation stack
- Delivery navigator
- Location selection (shows only locations for selected map)

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
2. **Two Unified GUIs**: 
   - **Mapping & Tagging GUI**: One GUI handles mapping, location tagging, and map saving
   - **Delivery Bot GUI**: One GUI handles map selection, localization, initial pose, and navigation
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
