# Quick Start Guide

## ⚠️ CRITICAL: Clock Synchronization First!

**Before starting, ensure Raspberry Pi clock is synchronized!** See `docs/TIME_SYNCHRONIZATION.md` or `INSTALLATION.md` Step 0 for setup.

The Pi doesn't have a battery-backed clock - without sync, navigation will fail with timestamp errors.

---

## Complete Workflow

### Step 1: Start Robot Hardware

**📍 On: TurtleBot 4 (Raspberry Pi)**

```bash
ros2 launch turtlebot4_bringup robot.launch.py
```

### Step 2: Load Map and Set Initial Pose

**📍 On: Host Computer (Intel NUC)**

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 launch initial_pose_setter localization_with_pose_setter.launch.py map:=$HOME/delivery_bot_ws/data/maps/planetary_office_map.yaml
```

**The Initial Pose GUI opens automatically after 3 seconds.**

**In the GUI, choose one method:**
1. **Use Tagged Location** - Select from dropdown and click "Use This Location"
2. **Manual Entry** - Enter X, Y, Yaw and click "Set Initial Pose (Manual)"
3. **RViz2** - Click "Open RViz2" and use "2D Pose Estimate" tool

### Step 3: Start Navigation

```bash
ros2 launch turtlebot4_navigation nav2.launch.py
```

### Step 4: Start Delivery Navigator

```bash
ros2 run delivery_navigator goal_navigator_node
```

### Step 5: Start Delivery GUI

```bash
ros2 run delivery_bot_gui delivery_gui
```

**Select a location and click "Go to Location"!**

## Key Commands

```bash
# Set initial pose manually (if GUI not working)
ros2 run initial_pose_setter initial_pose_gui

# Tag locations
ros2 run location_manager location_tag_node

# Save map
ros2 run map_manager map_saver_node
```

## For Complete Guides

See `docs/` directory for detailed step-by-step guides.
