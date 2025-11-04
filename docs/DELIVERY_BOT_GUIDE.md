# Delivery Bot Guide - Using the Delivery Bot System

This guide walks you through using the delivery bot system to navigate to tagged locations using a saved map.

## System Architecture

This process uses a **distributed setup** with two computers:

1. **TurtleBot 4 (Raspberry Pi)** - Onboard computer with robot hardware
2. **Host Computer (Intel NUC)** - High-level computer running navigation, GUI, and delivery bot nodes

> **⚠️ Important:** Commands are clearly labeled with which computer they should run on.

---

## Prerequisites

- ✅ A saved SLAM map (created using `MAPPING_GUIDE.md`)
- ✅ Tagged delivery locations (see `LOCATION_TAGGING_GUIDE.md`)
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

Open a terminal on the TurtleBot 4 Raspberry Pi and run (if its is not running after the boot):

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

### Step 2: Load Saved Map with Localization and Set Initial Pose

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer and run:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 launch initial_pose_setter localization_with_pose_setter.launch.py map:=$HOME/delivery_bot_ws/data/maps/planetary_office_map.yaml
```

**Replace `planetary_office_map.yaml` with your actual map filename** if different.

**What this does:**
- Loads the saved map file
- Starts AMCL (Adaptive Monte Carlo Localization)
- **Automatically opens Initial Pose GUI** (after 3 seconds)
- Allows you to easily set initial pose

**The Initial Pose GUI will open automatically.** It provides three options:

1. **Use Tagged Location** (if available):
   - Select a known location from dropdown
   - Click "Use This Location"
   - Initial pose is set from that location's coordinates

2. **Manual Entry**:
   - Enter X, Y position (meters)
   - Enter Yaw angle (degrees, 0 = north)
   - Click "Set Initial Pose (Manual)"

3. **Visual Method (RViz2)**:
   - Click "Open RViz2 to Set Pose Visually"
   - In RViz2: Add Map display (topic: `/map`)
   - Use "2D Pose Estimate" tool to click on map

**After setting initial pose:**
- AMCL will start localizing
- Robot transform becomes available
- You can proceed to navigation

**Keep this terminal open** - Localization must continue running.

---

### Step 3: Start Nav2 Navigation Stack

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 launch launch/nav2.launch.py
```

**What this does:**
- Starts Nav2 navigation stack with optimized parameters for:
  - Smooth spot turning (reduced rotation speed and better thresholds)
  - Better obstacle avoidance in confined spaces (increased inflation radius)
  - More precise path planning (A* algorithm enabled)
- Provides path planning and obstacle avoidance
- Handles navigation goal requests
- Provides action server for `navigate_to_pose`

**Expected output:**
- Nav2 nodes started
- Navigation stack ready
- Action server available

**Keep this terminal open** - Nav2 must continue running for navigation to work.

---

### Step 4: Start Delivery Navigator

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 run delivery_navigator goal_navigator_node
```

**What this does:**
- Subscribes to `/delivery_goal` topic (receives location names from GUI)
- Reads location data from `locations.json`
- Converts location names to poses
- Sends navigation goals to Nav2
- Publishes navigation status updates

**Expected output:**
```
[INFO] Delivery Navigator Node started
[INFO] Loaded X locations from locations.json
[INFO] Waiting for delivery goals...
```

**Keep this terminal open** - Navigator must be running to handle navigation requests.

---

### Step 5: Start Delivery Bot GUI

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 run delivery_bot_gui delivery_gui
```

**What this does:**
- Opens a graphical interface
- Shows list of available delivery locations
- Allows you to select a location
- Sends navigation goal when "Go to Location" is clicked
- Displays navigation status

**Expected output:**
- GUI window opens
- Location dropdown populated with tagged locations
- Status display showing "Ready"

---

### Step 6: Navigate to a Location

**📍 On: Host Computer (Intel NUC)**

**Using the GUI:**

1. **Select a location** from the dropdown menu
2. **Click "Go to Location"** button
3. **Monitor the status** in the GUI:
   - "Navigating to [Location]..." - Robot is moving
   - "Arrived at [Location]" - Navigation complete
   - "Navigation failed" - Error occurred

**The robot will:**
- Plan a path to the selected location
- Navigate autonomously
- Avoid obstacles
- Arrive at the tagged location

**Watch the robot** navigate to verify it reaches the correct location.

---

### Step 7: Navigate to Another Location

**📍 On: Host Computer (Intel NUC)**

1. **Select a different location** from the dropdown
2. **Click "Go to Location"** again
3. The robot will navigate to the new location

**You can navigate to multiple locations** sequentially using the GUI.

---

### Step 8: Stop All Nodes (When Done)

**📍 On: Host Computer (Intel NUC)**

Stop all nodes by pressing `Ctrl+C` in each terminal:
1. GUI (close window or `Ctrl+C`)
2. Delivery Navigator
3. Nav2 Navigation
4. Localization

**📍 On: TurtleBot 4 (Raspberry Pi)**

Stop the robot launch:
1. Press `Ctrl+C` in the terminal running `robot.launch.py`

---

## Troubleshooting

### Robot Not Localizing / AMCL Warnings

**Problem:** AMCL shows warnings about needing initial pose, or robot position is incorrect.

**Solution:**
- Use the Initial Pose GUI that opens automatically with the launch file
- Or manually run: `ros2 run initial_pose_setter initial_pose_gui`
- Select a known location or enter position manually
- Verify map file exists: `ls ~/delivery_bot_ws/data/maps/`
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
- Verify `locations.json` file exists: `cat ~/delivery_bot_ws/data/locations.json`
- Click "Refresh Locations" button in GUI
- Check location_manager was running when locations were tagged
- Verify JSON file has valid format

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
- If needed, adjust parameters in `~/delivery_bot_ws/config/nav2.yaml`:
  - Increase `movement_time_allowance` to 20.0 for more rotation time
  - Reduce `min_theta_velocity_threshold` to 0.03 if rotation is too sensitive

### Paths Going Through Obstacles

**Problem:** Robot plans paths that go through obstacles (like desks) instead of around them.

**Solutions:**
- Increase safety distance (`inflation_radius`) in `~/delivery_bot_ws/config/nav2.yaml`:
  - Current value: `0.6` meters
  - Increase to `0.7` or `0.8` for larger safety margin
  - Edit both `local_costmap` and `global_costmap` sections
- Increase `cost_scaling_factor` to 6.0 for stronger obstacle avoidance
- Verify obstacles are properly marked in the map
- Check laser scan is detecting obstacles correctly

### Customizing Nav2 Parameters

**To adjust navigation behavior**, edit the configuration file:

```bash
nano ~/delivery_bot_ws/config/nav2.yaml
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
- ✅ `ros2 launch initial_pose_setter localization_with_pose_setter.launch.py map:=path/to/map.yaml` - Localization with Initial Pose GUI
- ✅ `ros2 launch launch/nav2.launch.py` - Navigation stack
- ✅ `ros2 run delivery_navigator goal_navigator_node` - Delivery navigator
- ✅ `ros2 run delivery_bot_gui delivery_gui` - GUI

**Result:**
- ✅ Robot navigates autonomously to selected delivery locations
- ✅ GUI provides easy interface for location selection
- ✅ System handles path planning and obstacle avoidance

---

## Quick Reference

| Step | System | Command |
|------|--------|---------|
| 1. Start robot | TurtleBot 4 Pi | `ros2 launch turtlebot4_bringup robot.launch.py` |
| 2. Load map | Host NUC | `ros2 launch initial_pose_setter localization_with_pose_setter.launch.py map:=~/delivery_bot_ws/data/maps/map_name.yaml` |
| 3. Start Nav2 | Host NUC | `ros2 launch launch/nav2.launch.py` |
| 4. Start navigator | Host NUC | `ros2 run delivery_navigator goal_navigator_node` |
| 5. Start GUI | Host NUC | `ros2 run delivery_bot_gui delivery_gui` |
| 6. Navigate | Host NUC | Select location in GUI and click "Go to Location" |

---

## Next Steps

For more information:
- **Creating Maps:** See `MAPPING_GUIDE.md`
- **Tagging Locations:** See `LOCATION_TAGGING_GUIDE.md`
- **Architecture:** See `../ARCHITECTURE.md`
- **Installation:** See `../INSTALLATION.md`

