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

**Single unified launch - one GUI handles everything!**

#### Step 1: Start Robot Hardware

**📍 On: TurtleBot 4 (Raspberry Pi)**

```bash
ros2 launch turtlebot4_bringup robot.launch.py
```

#### Step 2: Launch Unified Delivery Bot GUI

**📍 On: Host Computer (Intel NUC)**

```bash
cd ~/delivery_bot_pkg
source install/setup.bash
ros2 launch launch/delivery_bot.launch.py
```

**The Unified Delivery Bot GUI opens automatically.**

**In the GUI:**

1. **Select Map** - Choose a map from the dropdown
2. **Load Map** - Click "📂 Load Map and Start Localization"
   - GUI automatically loads the map and starts localization (AMCL)
   - Shows "Set Initial Pose" interface
3. **Set Initial Pose** - Choose one method:
   - **Use Tagged Location** (Recommended): Select from dropdown, click "✅ Use This Location"
   - **Manual Entry**: Enter X, Y, Yaw, click "✅ Set Manual"
4. **Navigate** - After initial pose is set:
   - "Select Delivery Location" card appears
   - Select location from dropdown (shows only locations for selected map)
   - Click "🚀 Go to Location"
   - Monitor navigation status

**The GUI automatically manages:**
- Map loading
- Localization (AMCL)
- Nav2 navigation stack
- Delivery navigator
- All nodes are started/stoped automatically

**Click "🚪 Exit" when done** - All nodes are stopped automatically.

---

## Key Commands

```bash
# Workflow 1: Unified mapping and location tagging (first time - ONE COMMAND!)
ros2 launch launch/mapping_with_tagging.launch.py

# Workflow 2: Unified delivery bot application (daily use - ONE COMMAND!)
ros2 launch launch/delivery_bot.launch.py
```

**That's it!** Just two commands for the entire workflow:
1. One command for mapping and tagging
2. One command for delivery bot navigation

## For Complete Guides

- **Map Creation and Location Tagging:** See `docs/MAPPING_AND_LOCATION_TAGGING.md`
- **Delivery Bot Navigation:** See `docs/DELIVERY_BOT_GUIDE.md`
- **Installation:** See `INSTALLATION.md`
- **Time Synchronization:** See `docs/TIME_SYNCHRONIZATION.md`
