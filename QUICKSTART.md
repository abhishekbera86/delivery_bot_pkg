# Quick Start Guide

## ⚠️ CRITICAL: Clock Synchronization First!

**Before starting, ensure Raspberry Pi clock is synchronized!** See `docs/TIME_SYNCHRONIZATION.md` or `INSTALLATION.md` Step 0 for setup.

The Pi doesn't have a battery-backed clock - without sync, navigation will fail with timestamp errors.

---

## Two Main Workflows

### Workflow 1: Map Creation with Location Tagging (First Time)

**Single unified launch - everything in one command!**

```bash
# On TurtleBot 4 Pi (Terminal 1):
ros2 launch turtlebot4_bringup robot.launch.py

# On Host Computer (Terminal 1):
ros2 launch launch/mapping_with_tagging.launch.py

# On Host Computer (Terminal 2 - for teleoperation):
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**In the Unified GUI:**
1. Set JSON filename (optional, default: "locations.json") - Click "Set"
2. Tag locations as you map - Enter name, click "Save Location"
3. Save map when done - Enter map name, click "Save Map"
4. Exit - Click "Exit" button

**Result:**
- Map saved to: `~/delivery_bot_pkg/data/maps/{map_name}.yaml`
- Locations saved to: `~/delivery_bot_pkg/data/locations/{json_filename}.json`

**See:** `docs/MAPPING_AND_LOCATION_TAGGING.md` for complete guide

---

## Key Commands

```bash
# Workflow 1: Unified mapping and location tagging (first time - ONE COMMAND!)
ros2 launch launch/mapping_with_tagging.launch.py

# Workflow 2: Location tagging after map is loaded
ros2 launch launch/localization_with_location_tagging.launch.py map:=$HOME/delivery_bot_pkg/data/maps/{map_name}.yaml
```

**That's it!** Just two commands for the entire workflow:
1. One command for mapping and tagging
2. One command for location tagging after map is loaded

## For Complete Guides

- **Map Creation and Location Tagging:** See `docs/MAPPING_AND_LOCATION_TAGGING.md`
- **Installation:** See `INSTALLATION.md`
- **Time Synchronization:** See `docs/TIME_SYNCHRONIZATION.md`
