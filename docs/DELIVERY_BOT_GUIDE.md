# Delivery Bot Guide - Using the Delivery Bot System

This guide walks you through using the delivery bot system to navigate to tagged locations using a saved map.

## System Architecture

This process uses a **distributed setup** with two computers:

1. **TurtleBot 4 (Raspberry Pi)** - Onboard computer with robot hardware
2. **Host Computer (Intel NUC)** - High-level computer running navigation, GUI, and delivery bot nodes

> **⚠️ Important:** Commands are clearly labeled with which computer they should run on.

---

## Prerequisites

- ✅ A saved SLAM map (created using `MAPPING_AND_LOCATION_TAGGING.md`)
- ✅ Tagged delivery locations (created using `MAPPING_AND_LOCATION_TAGGING.md`)
- ✅ TurtleBot 4 robot hardware is powered on and ready
- ✅ TurtleBot 4 Raspberry Pi has ROS2 Jazzy installed
- ✅ Host computer has ROS2 Jazzy, Nav2, and all delivery bot packages installed
- ✅ Both computers are on the same network
- ✅ ROS2 workspace is built on the host computer
- ✅ **⚠️ CLOCK SYNCHRONIZATION**: Raspberry Pi clock must be synchronized (see `TIME_SYNCHRONIZATION.md` or `INSTALLATION.md` Step 0). **Clock sync is critical** - without it, navigation will fail with transform timeout errors.

---

## Step-by-Step Delivery Bot Process

### Step 1: Start Robot Hardware

**📍 On: TurtleBot 4 (Raspberry Pi)**

Open a terminal on the TurtleBot 4 Raspberry Pi and run (if it's not running after boot):

```bash
ros2 launch turtlebot4_bringup robot.launch.py
```

**What this does:**
- Starts the TurtleBot 4 base node (`turtlebot4_base_node`)
- Initializes robot sensors (RPLIDAR, camera, etc.)
- Provides access to robot actuators (Create 3 base)
- Publishes robot state, sensor data, and transforms

**Expected output:**
- Robot hardware initialized
- Sensors publishing data
- No error messages

**⚠️ Note:** This launch file **MUST** run on the TurtleBot 4 Raspberry Pi. It will crash if run on the host computer.

---

### Step 2: Launch Unified Delivery Bot GUI

**📍 On: Host Computer (Intel NUC)**

Open a terminal on the host computer and run:

```bash
cd ~/delivery_bot_pkg
source install/setup.bash
ros2 launch launch/delivery_bot.launch.py
```

**What this does:**
- Opens the unified Delivery Bot Main GUI
- GUI handles all node management automatically
- Provides a single interface for the entire delivery bot workflow

**Expected output:**
- GUI window opens with map selection interface
- Status display showing "Ready - Select a map to begin"

---

### Step 3: Select Map and Load

**📍 On: Host Computer (Intel NUC)**

**Using the GUI:**

1. **Select a map** from the dropdown menu (maps are loaded from `~/delivery_bot_pkg/data/maps/`)
2. **Click "📂 Load Map and Start Localization"** button
3. **Wait for confirmation** - The GUI will:
   - Load the selected map file
   - Start AMCL localization automatically
   - Show the "Set Initial Pose" interface

**What happens automatically:**
- Map file is loaded: `~/delivery_bot_pkg/data/maps/{map_name}.yaml`
- Locations file is loaded: `~/delivery_bot_pkg/data/locations/{map_name}.json`
- Localization (AMCL) starts in the background
- Initial pose card appears in the GUI

**Status display will show:** "✅ Map loaded. Set initial pose to continue."

---

### Step 4: Set Initial Pose

**📍 On: Host Computer (Intel NUC)**

**Using the GUI:**

The "Set Initial Pose" card provides two options:

1. **Use Tagged Location** (Recommended):
   - Select a known location from the dropdown
   - Click "✅ Use This Location"
   - Initial pose is automatically set from that location's coordinates

2. **Manual Entry**:
   - Enter X, Y position (meters) and Yaw angle (degrees)
   - Click "✅ Set Manual"
   - Initial pose is set from your entered values

**After setting initial pose:**
- The "Set Initial Pose" card will hide
- The "Select Delivery Location" card will appear
- Nav2 and Delivery Navigator start automatically in the background
- Navigation is now ready!

**Status display will show:** "✅ Initial pose set. Navigation ready!"

---

### Step 5: Navigate to a Location

**📍 On: Host Computer (Intel NUC)**

**Using the GUI:**

1. **Select a location** from the dropdown menu (locations are loaded from `{map_name}.json`)
2. **Click "🚀 Go to Location"** button
3. **Confirm navigation** in the popup dialog
4. **Monitor the status** in the GUI:
   - "🚀 Navigating to: [Location]..." - Robot is moving
   - "✅ SUCCESS: Arrived at [Location]" - Navigation complete
   - "❌ ERROR: [message]" - Error occurred

**The robot will:**
- Plan a path to the selected location
- Navigate autonomously
- Avoid obstacles
- Arrive at the tagged location

**Watch the robot** navigate to verify it reaches the correct location.

---

### Step 6: Navigate to Another Location

**📍 On: Host Computer (Intel NUC)**

1. **Select a different location** from the dropdown
2. **Click "🚀 Go to Location"** again
3. The robot will navigate to the new location

**You can navigate to multiple locations** sequentially using the GUI.

---

### Step 7: Exit (When Done)

**📍 On: Host Computer (Intel NUC)**

**Using the GUI:**

1. **Click "🚪 Exit"** button in the GUI
2. **Confirm exit** in the popup dialog
3. All nodes will be stopped automatically:
   - Localization
   - Nav2
   - Delivery Navigator

**📍 On: TurtleBot 4 (Raspberry Pi)**

Stop the robot launch:
1. Press `Ctrl+C` in the terminal running `robot.launch.py`

---

## Troubleshooting

### Robot Not Localizing / AMCL Warnings

**Problem:** AMCL shows warnings about needing initial pose, or robot position is incorrect.

**Solution:**
- Use the "Set Initial Pose" interface in the main GUI
- Select a tagged location from the dropdown (recommended)
- Or enter pose manually (X, Y, Yaw)
- Verify map file exists: `ls ~/delivery_bot_pkg/data/maps/`
- Check that `/map` topic is publishing: `ros2 topic echo /map --once`
- Verify TF transform after setting pose: `ros2 run tf2_ros tf2_echo map base_link`

### Navigation Goal Not Working

**Problem:** Robot doesn't move when goal is sent.

**Solutions:**
- Verify Nav2 action server is running: `ros2 action list | grep navigate_to_pose`
- Check delivery navigator is running
- Verify location exists in `locations.json`
- Check navigator terminal for error messages
- Ensure robot is localized in the map

### GUI Not Showing Locations

**Problem:** Location dropdown is empty or locations not listed.

**Solutions:**
- Verify locations file exists for the selected map: `ls ~/delivery_bot_pkg/data/locations/{map_name}.json`
- Make sure the locations file name matches the map name (e.g., `office_map.yaml` → `office_map.json`)
- Click "🔄 Refresh" button in the location selection card
- Check that locations were tagged using the mapping GUI for this specific map
- Verify JSON file has valid format
- Ensure you selected the correct map in the map selection dropdown

### Robot Hitting Obstacles

**Problem:** Robot collides with obstacles during navigation.

**Solutions:**
- Check that laser scan is publishing: `ros2 topic echo /scan --once`
- Verify costmap is being generated (check RViz)
- Slow down maximum velocity in Nav2 parameters
- Check for obstacles not in the map (dynamic objects)

### Navigation Takes Too Long

**Problem:** Robot takes very long to reach goal or gets stuck.

**Solutions:**
- Check if robot is stuck in a loop
- Verify path is being planned: `ros2 topic echo /plan --once`
- Check for obstacles blocking the path
- Try sending a different goal to test
- Restart navigation stack if needed

### Robot Getting Stuck During Spot Turning

**Problem:** Robot gets stuck or hesitates when turning in place to start a new goal.

**Solutions:**
- Check if robot wheels are blocked or stuck
- Verify laser scan is working: `ros2 topic echo /scan --once`
- Check Nav2 controller logs for rotation errors
- If needed, adjust parameters in `~/delivery_bot_pkg/config/nav2.yaml`:
  - Increase `movement_time_allowance` to 20.0 for more rotation time
  - Reduce `min_theta_velocity_threshold` to 0.03 if rotation is too sensitive

### Paths Going Through Obstacles

**Problem:** Robot plans paths that go through obstacles (like desks) instead of around them.

**Solutions:**
- Increase safety distance (`inflation_radius`) in `~/delivery_bot_pkg/config/nav2.yaml`:
  - Current value: `0.6` meters
  - Increase to `0.7` or `0.8` for larger safety margin
  - Edit both `local_costmap` and `global_costmap` sections
- Increase `cost_scaling_factor` to 6.0 for stronger obstacle avoidance
- Verify obstacles are properly marked in the map
- Check laser scan is detecting obstacles correctly

### Customizing Nav2 Parameters

**To adjust navigation behavior**, edit the configuration file:

```bash
nano ~/delivery_bot_pkg/config/nav2.yaml
```

**Common adjustments:**
- **Safety distance**: Change `inflation_radius` (default: 0.6 meters)
  - Larger value = robot stays farther from obstacles
  - Smaller value = robot can navigate closer to obstacles
- **Rotation speed**: Change `wz_max` in `FollowPath` section (default: 1.2)
  - Larger value = faster rotation (but may be less smooth)
  - Smaller value = slower, smoother rotation
- **Forward speed**: Change `vx_max` in `FollowPath` section (default: 0.5)

After editing, restart Nav2 for changes to take effect.

---

## Summary

**TurtleBot 4 (Raspberry Pi) runs:**
- ✅ `ros2 launch turtlebot4_bringup robot.launch.py` - Robot hardware

**Host Computer (NUC) runs:**
- ✅ `ros2 launch launch/delivery_bot.launch.py` - Unified Delivery Bot GUI (handles all nodes automatically)

**Result:**
- ✅ Robot navigates autonomously to selected delivery locations
- ✅ Single GUI provides complete workflow from map selection to navigation
- ✅ All nodes (localization, Nav2, navigator) are managed automatically
- ✅ System handles path planning and obstacle avoidance

---

## Quick Reference

| Step | System | Command |
|------|--------|---------|
| 1. Start robot | TurtleBot 4 Pi | `ros2 launch turtlebot4_bringup robot.launch.py` |
| 2. Launch GUI | Host NUC | `ros2 launch launch/delivery_bot.launch.py` |
| 3. Select map | Host NUC | Use GUI to select map from dropdown |
| 4. Set initial pose | Host NUC | Use GUI to set pose (location or manual) |
| 5. Navigate | Host NUC | Select location in GUI and click "Go to Location" |

---

## Next Steps

For more information:
- **Creating Maps:** See `MAPPING_GUIDE.md`
- **Tagging Locations:** See `LOCATION_TAGGING_GUIDE.md`
- **Architecture:** See `../ARCHITECTURE.md`
- **Installation:** See `../INSTALLATION.md`

