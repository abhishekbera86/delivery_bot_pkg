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

### Workflow 2: Delivery Bot Application (Daily Use)

**Use saved map and locations for navigation:**

#### Step 1: Start Robot Hardware

**📍 On: TurtleBot 4 (Raspberry Pi)**

```bash
ros2 launch turtlebot4_bringup robot.launch.py
```

#### Step 2: Load Map and Set Initial Pose

**📍 On: Host Computer (Intel NUC)**

```bash
cd ~/delivery_bot_pkg
source install/setup.bash
ros2 launch launch/localization_with_location_tagging.launch.py map:=$HOME/delivery_bot_pkg/data/maps/your_map_name.yaml
```

**The Initial Pose GUI opens automatically after 3 seconds.**

**In the GUI, choose one method:**
1. **Use Tagged Location** - Select from dropdown and click "Use This Location"
2. **Manual Entry** - Enter X, Y, Yaw and click "Set Initial Pose (Manual)"
3. **RViz2** - Click "Open RViz2" and use "2D Pose Estimate" tool

**After setting initial pose:**
- Location Tagging GUI opens automatically
- You can tag more locations if needed

#### Step 3: Start Navigation

```bash
ros2 launch launch/nav2.launch.py
```

#### Step 4: Start Delivery Navigator

```bash
ros2 run delivery_navigator goal_navigator_node
```

#### Step 5: Start Delivery GUI

```bash
ros2 run delivery_bot_gui delivery_gui
```

**Select a location and click "Go to Location"!**

---

## Key Commands

```bash
# Unified mapping and location tagging (first time - ONE COMMAND!)
ros2 launch launch/mapping_with_tagging.launch.py

# Delivery bot application (daily use)
ros2 launch launch/localization_with_location_tagging.launch.py map:=$HOME/delivery_bot_pkg/data/maps/map_name.yaml
ros2 launch launch/nav2.launch.py
ros2 run delivery_navigator goal_navigator_node
ros2 run delivery_bot_gui delivery_gui
```

## For Complete Guides

- **Map Creation and Location Tagging:** See `docs/MAPPING_AND_LOCATION_TAGGING.md`
- **Delivery Bot Navigation:** See `docs/DELIVERY_BOT_GUIDE.md`
- **Installation:** See `INSTALLATION.md`
- **Time Synchronization:** See `docs/TIME_SYNCHRONIZATION.md`
