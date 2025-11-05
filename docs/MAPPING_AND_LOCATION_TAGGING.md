# Mapping and Location Tagging Guide

This guide explains how to create SLAM maps and tag delivery locations using the **unified GUI** - everything in one interface!

## Overview

The unified workflow combines mapping and location tagging into a single process using one GUI:
1. **Start unified launch** - SLAM, map saver, and GUI all start together
2. **Tag locations during mapping** - Save delivery locations as you map
3. **Save map** - Enter map name and save everything (JSON filename auto-updates from map name)
4. **Exit** - Clean shutdown with all data saved

**Key Advantage:** Single GUI handles everything! No need to launch multiple nodes or use multiple terminals.

---

## System Architecture

This process uses a **distributed setup** with two computers:

1. **TurtleBot 4 (Raspberry Pi)** - Onboard computer with robot hardware
2. **Host Computer (Intel NUC)** - High-level computer running SLAM, mapping, and unified GUI

> **⚠️ Important:** Commands are clearly labeled with which computer they should run on.

---

## Prerequisites

- ✅ TurtleBot 4 robot hardware is powered on and ready
- ✅ TurtleBot 4 Raspberry Pi has ROS2 Jazzy installed
- ✅ Host computer has ROS2 Jazzy, Nav2, SLAM Toolbox installed
- ✅ Both computers are on the same network
- ✅ ROS2 workspace is built on the host computer
- ✅ All packages are installed (see `INSTALLATION.md`)

---

## Complete Workflow: Unified Mapping and Location Tagging

### Step 1: Start Robot Hardware

**📍 On: TurtleBot 4 (Raspberry Pi)**

Open a terminal on the TurtleBot 4 Raspberry Pi and run:

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

**⚠️ Note:** This launch file **MUST** run on the TurtleBot 4 Raspberry Pi. It will crash if run on the host computer because it needs direct hardware access.

---

### Step 2: Start Unified Mapping and Tagging System

**📍 On: Host Computer (Intel NUC)**

Open a terminal on the host computer and run:

```bash
cd ~/delivery_bot_pkg
source install/setup.bash
ros2 launch launch/mapping_with_tagging.launch.py
```

**What this does:**
- Starts SLAM Toolbox for simultaneous localization and mapping
- Starts map saver node (runs in background)
- Starts unified Mapping and Tagging GUI (opens after 3 seconds)
- **Everything in one command!**

**Expected output:**
- SLAM Toolbox node started
- Map saver node connected
- Mapping and Tagging GUI opens automatically (after 3 seconds)

**Keep this terminal open** - All systems must continue running.

---

### Step 3: Start Teleoperation

**📍 On: Host Computer (Intel NUC)**

Open a **new terminal** on the host computer:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Controls:**
- `i` - Move forward
- `k` - Stop
- `j` - Turn left
- `l` - Turn right
- `,` - Move backward
- `u` - Forward + left
- `o` - Forward + right

**What this does:**
- Publishes velocity commands (`/cmd_vel`) to move the robot
- Allows you to manually drive the robot to explore the environment

---

### Step 4: Configure and Use the Unified GUI

**📍 On: Host Computer (Intel NUC)**

**The unified GUI opens automatically after 3 seconds.**

#### Understanding the Unified GUI

The GUI has several sections:

**⚙️ Configuration Section:**
- **Locations JSON File**: Enter the filename for your locations (e.g., "my_locations.json")
- **Auto-updates when you enter map name** - The JSON filename automatically matches the map name
- Click "Set" to configure the location file (optional - defaults to "locations.json")
- Locations will be saved to: `~/delivery_bot_pkg/data/locations/{filename}.json`

**🤖 Current Robot Position:**
- Shows real-time X, Y, Z coordinates and yaw angle
- Auto-updates every 0.5 seconds
- Green = position available, Orange = waiting for map frame

**🏷️ Tag New Location:**
- Enter location name in the text field
- Click "💾 Save Location" to tag current position
- Click "🔄 Refresh Position" to manually update

**📋 Tagged Locations:**
- Table shows all tagged locations with positions
- Automatically updates when you tag a location

**💾 Save Map:**
- Enter map name in the text field (e.g., "office_map")
- **JSON filename automatically updates** to match the map name (e.g., "office_map.json")
- Click "💾 Save Map" to save the current map
- Map will be saved to: `~/delivery_bot_pkg/data/maps/{map_name}.yaml` and `.pgm`
- Locations will be saved to: `~/delivery_bot_pkg/data/locations/{map_name}.json`
- Status message shows save progress

**🚪 Exit Button:**
- Click "🚪 Exit" to cleanly shut down everything
- Prompts for confirmation before exiting

#### Workflow in the GUI

1. **Wait for map frame** (happens automatically):
   - GUI shows "Waiting for map frame..." initially
   - Once SLAM creates the map frame, position display turns green
   - You can now tag locations!

2. **Tag locations**:
   - Drive robot to a location you want to tag
   - Enter location name in "Location Name" field
   - Click "💾 Save Location"
   - Location appears in the "Tagged Locations" table
   - Repeat for all desired locations

3. **Save map** (when done mapping):
   - Enter map name in "Map Name" field (e.g., "office_map")
   - **JSON filename automatically updates** to match the map name (e.g., "office_map.json")
   - Click "💾 Save Map"
   - Confirm the save dialog
   - Status shows: "Saving map '{map_name}'..."
   - When complete, status shows: "✅ Map saved successfully!"
   - Map saved to: `~/delivery_bot_pkg/data/maps/{map_name}.yaml`
   - Locations saved to: `~/delivery_bot_pkg/data/locations/{map_name}.json`

4. **Optional - Set custom JSON filename** (if you want a different name):
   - Enter filename in "Locations JSON File" field
   - Click "Set" button
   - Status shows: "Locations will be saved to: {filename}.json"
   - Note: This will be overridden when you enter a map name

5. **Exit**:
   - Click "🚪 Exit" button
   - Confirm exit dialog
   - All nodes shut down cleanly

---

### Step 5: Verify Files

**📍 On: Host Computer (Intel NUC)**

Verify that the map and locations were saved:

```bash
# Check map files
ls -lh ~/delivery_bot_pkg/data/maps/

# Check locations file
ls -lh ~/delivery_bot_pkg/data/locations/
cat ~/delivery_bot_pkg/data/locations/your_filename.json
```

You should see:
- Map files (`your_map_name.yaml` and `.pgm`) in `data/maps/`
- Locations file (`your_filename.json`) in `data/locations/`

---

## Understanding the Unified GUI

### Configuration Section
- **Locations JSON File**: Set the filename for saving locations
- Default: "locations.json"
- Saved to: `~/delivery_bot_pkg/data/locations/{filename}.json`
- Click "Set" to apply the filename

### Current Robot Position
- Shows real-time X, Y, Z coordinates and yaw angle
- Auto-updates every 0.5 seconds
- **Green** = position available (map frame exists)
- **Orange** = waiting for map frame (SLAM starting)

### Tag New Location
- Enter location name in the text field
- Click "💾 Save Location" to tag current position
- Click "🔄 Refresh Position" to manually update
- Locations are saved immediately to the JSON file

### Tagged Locations
- Table shows all tagged locations with positions
- Automatically refreshes when you tag a location
- Shows: Name, X (m), Y (m), Yaw (deg)

### Save Map
- Enter map name in the text field
- Click "💾 Save Map" to save the current map
- Confirmation dialog shows save location
- Status message shows save progress and result
- Map saved to: `~/delivery_bot_pkg/data/maps/{map_name}.yaml` and `.pgm`

### Exit Button
- Click "🚪 Exit" to stop all nodes and close GUI
- Prompts for confirmation
- Cleanly shuts down SLAM, map saver, and GUI

---

## Data Storage

### Maps
- **Location**: `~/delivery_bot_pkg/data/maps/`
- **Format**: `.yaml` (metadata) + `.pgm` (occupancy grid image)
- **Created by**: SLAM Toolbox during mapping
- **Saved by**: Map saver node (via GUI or topic)

### Locations
- **Location**: `~/delivery_bot_pkg/data/locations/`
- **Format**: JSON
- **Filename**: Set in GUI (default: "locations.json")
- **Structure**:
  ```json
  {
    "location_name": {
      "name": "location_name",
      "frame_id": "map",
      "position": {"x": float, "y": float, "z": float},
      "orientation": {"x": float, "y": float, "z": float, "w": float},
      "description": "string"
    }
  }
  ```

---

## Troubleshooting

### Unified GUI Doesn't Open

**Problem:** GUI doesn't appear after 3 seconds.

**Solutions:**
- Wait a few more seconds (SLAM may take time to initialize)
- Check terminal for error messages
- Verify SLAM is running: `ros2 node list | grep slam`
- Try launching manually: `ros2 run location_manager mapping_and_tagging_gui`

### Cannot Tag Locations

**Problem:** GUI shows "Waiting for map frame..." or position not available.

**Solutions:**
- Ensure SLAM is running: `ros2 node list | grep slam`
- Verify map frame exists: `ros2 run tf2_ros tf2_echo map base_link`
- Check if robot is moving (SLAM needs movement to build map)
- Wait a few seconds after starting SLAM

### Map Not Saving

**Problem:** Map save button doesn't work or map files not created.

**Solutions:**
- Verify map saver node is running: `ros2 node list | grep map_saver`
- Check GUI status message for errors
- Wait up to 15 seconds after clicking save (SLAM Toolbox may take time)
- Check workspace root directory: `ls ~/delivery_bot_pkg/*.yaml`
- Verify map saver node terminal for error messages

### Locations Not Saved

**Problem:** Tagged locations don't appear in the locations file.

**Solutions:**
- Verify JSON filename is set (click "Set" button)
- Check file permissions: `ls -l ~/delivery_bot_pkg/data/locations/`
- Verify GUI shows "Location saved successfully" message
- Check GUI terminal for error messages
- Manually check file: `cat ~/delivery_bot_pkg/data/locations/your_filename.json`

### JSON Filename Not Working

**Problem:** Locations saved to wrong file or default file.

**Solutions:**
- Make sure to click "Set" button after entering filename
- Verify status shows "Locations will be saved to: {filename}.json"
- Check that filename ends with `.json` (added automatically)
- Verify location handler is initialized (check terminal logs)

---

## Summary

**Complete Workflow:**
1. ✅ Start robot hardware (TurtleBot 4 Pi)
2. ✅ Start unified mapping and tagging system (Host NUC) - **One command!**
3. ✅ Start teleoperation (Host NUC)
4. ✅ Configure JSON filename in GUI (optional)
5. ✅ Drive robot and tag locations simultaneously
6. ✅ Save map when complete (via GUI)
7. ✅ Exit when done

**Result:**
- ✅ Map saved to `~/delivery_bot_pkg/data/maps/{map_name}.yaml`
- ✅ Locations saved to `~/delivery_bot_pkg/data/locations/{json_filename}.json`
- ✅ Ready for delivery bot navigation!

---

## Next Steps

After creating the map and tagging locations, proceed to:
- **Using the Delivery Bot:** See `DELIVERY_BOT_GUIDE.md` for navigation instructions

---

## Quick Reference

| Step | System | Command |
|------|--------|---------|
| 1. Start robot | TurtleBot 4 Pi | `ros2 launch turtlebot4_bringup robot.launch.py` |
| 2. Start unified system | Host NUC | `ros2 launch launch/mapping_with_tagging.launch.py` |
| 3. Start teleop | Host NUC | `ros2 run teleop_twist_keyboard teleop_twist_keyboard` |
| 4. Use GUI | Host NUC | Set JSON filename, tag locations, save map |
| 5. Exit | Host NUC | Click "🚪 Exit" in GUI |

---

## Key Features

✅ **Single Launch Command** - Everything starts with one command  
✅ **Unified GUI** - One interface for all operations  
✅ **JSON Filename Configuration** - Set custom location file names  
✅ **Map Saving from GUI** - Save maps directly from the interface  
✅ **Real-time Position Display** - See robot position as you map  
✅ **Clean Shutdown** - Exit button closes everything properly  
