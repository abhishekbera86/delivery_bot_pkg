# Mapping Guide - Creating SLAM Maps

This guide walks you through the complete process of creating a SLAM map using TurtleBot 4 for the delivery bot project.

## System Architecture

This process uses a **distributed setup** with two computers:

1. **TurtleBot 4 (Raspberry Pi)** - Onboard computer with robot hardware
2. **Host Computer (Intel NUC)** - High-level computer running SLAM and mapping

> **⚠️ Important:** Commands are clearly labeled with which computer they should run on.

---

## Prerequisites

- ✅ TurtleBot 4 robot hardware is powered on and ready
- ✅ TurtleBot 4 Raspberry Pi has ROS2 Jazzy installed
- ✅ Host computer has ROS2 Jazzy, Nav2, and SLAM Toolbox installed
- ✅ Both computers are on the same network
- ✅ ROS2 workspace is built on the host computer
- ✅ All packages are installed (see `INSTALLATION.md`)

---

## Step-by-Step Mapping Process

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

### Step 2: Start SLAM

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer and run:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 launch turtlebot4_navigation slam.launch.py
```

**What this does:**
- Starts SLAM Toolbox for simultaneous localization and mapping
- Subscribes to laser scan data from the robot
- Subscribes to odometry data
- Creates and updates a map as the robot moves
- Publishes the map on `/map` topic

**Expected output:**
- SLAM Toolbox node started
- Map is being generated (visible in RViz if running)
- No error messages

**Keep this terminal open** - SLAM must continue running during the entire mapping process.

---

### Step 3: (Optional) Start RViz for Visualization

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
rviz2
```

**In RViz:**
1. Add "Map" display - set topic to `/map`
2. Add "LaserScan" display - set topic to `/scan`
3. Add "TF" display - to see coordinate frames
4. Add "RobotModel" display - to see the robot

This allows you to visualize the map being created in real-time.

---

### Step 4: Start Teleoperation

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer:

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

### Step 5: Drive the Robot to Create Map

**📍 On: Host Computer (Intel NUC)**

**Instructions:**
1. Use the teleop keyboard to slowly drive the robot
2. Navigate through the entire area you want to map
3. Drive at moderate speed (not too fast)
4. Cover all areas you want in the map
5. Make sure the robot passes through doorways and corridors
6. The map will be built in real-time as the robot moves

**Tips:**
- Move slowly for better map quality
- Go back and forth in areas to refine the map
- Make sure the laser scanner has a clear view
- Avoid moving the robot too quickly (can cause mapping errors)

**Keep driving until:**
- You've covered the entire area you want to map
- The map looks complete in RViz (if using)
- All rooms and corridors are mapped

---

### Step 6: Start Map Saver Node

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 run map_manager map_saver_node
```

**What this does:**
- Connects to SLAM Toolbox's map saver service
- Waits for map save requests
- Handles saving maps to the correct directory

**Expected output:**
```
[INFO] Waiting for map saver service...
[INFO] Connected to SLAM Toolbox map_saver service
[INFO] Map Saver Node started
[INFO] Default map directory: /home/turtlebot4/delivery_bot_ws/data/maps
[INFO] Send map name to /save_map topic to save current map
```

**Keep this terminal open** - The map saver node must be running when you save the map.

---

### Step 7: Save the Map

**📍 On: Host Computer (Intel NUC)**

Open a new terminal on the host computer:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 topic pub /save_map std_msgs/String "data: 'office_map'"
```

**Replace `'office_map'` with your desired map name**, for example:
- `'office_map'` - For office environments
- `'lab_floor1'` - For lab first floor
- `'warehouse'` - For warehouse environments
- `'home_navigation'` - For home environments

**What this does:**
- Sends the map name to the map saver node
- Map saver node calls SLAM Toolbox to save the map
- Map files are saved to `~/delivery_bot_ws/data/maps/`

**Expected output in map_saver_node terminal:**
```
[INFO] Saving map: office_map using slam_toolbox
[INFO] Calling SLAM Toolbox to save map: office_map
[INFO] Waiting for map files to be created...
[INFO] Found map files in workspace root: /home/turtlebot4/delivery_bot_ws
[INFO] Moving map files to target directory...
[INFO] Moved map files to /home/turtlebot4/delivery_bot_ws/data/maps
[INFO] Map saved successfully: /home/turtlebot4/delivery_bot_ws/data/maps/office_map.yaml
```

**Files created:**
- `office_map.yaml` - Map metadata file
- `office_map.pgm` - Map image file (occupancy grid)

Both files will be in `~/delivery_bot_ws/data/maps/`

---

### Step 8: Verify Map Files

**📍 On: Host Computer (Intel NUC)**

Verify that the map files were created:

```bash
ls -lh ~/delivery_bot_ws/data/maps/
```

You should see:
- `office_map.yaml` (small file, ~100-500 bytes)
- `office_map.pgm` (larger file, ~20KB - 2MB depending on map size)

**Verify map content:**

```bash
cat ~/delivery_bot_ws/data/maps/office_map.yaml
```

Should show map metadata including:
- Image file name (`image: office_map.pgm`)
- Resolution
- Origin coordinates

---

### Step 9: Stop All Nodes

**📍 On: Host Computer (Intel NUC)**

Stop all nodes by pressing `Ctrl+C` in each terminal:
1. Stop map saver node
2. Stop teleop keyboard
3. Stop SLAM (if RViz is running, stop it too)

**📍 On: TurtleBot 4 (Raspberry Pi)**

Stop the robot launch:
1. Press `Ctrl+C` in the terminal running `robot.launch.py`

---

## Troubleshooting

### Robot Hardware Not Responding

**Problem:** Robot doesn't move when using teleop.

**Solutions:**
- Verify `robot.launch.py` is running on TurtleBot 4 Raspberry Pi
- Check that `/cmd_vel` topic exists: `ros2 topic list | grep cmd_vel`
- Verify robot is powered on
- Check network connectivity between computers

### SLAM Not Building Map

**Problem:** Map is not being generated.

**Solutions:**
- Verify laser scan data is available: `ros2 topic echo /scan --once`
- Check that SLAM is subscribed to correct topics
- Ensure robot is moving (SLAM needs movement to build map)
- Check TF transforms: `ros2 run tf2_ros tf2_echo map base_link`

### Map Saver Service Not Available

**Problem:** Map saver node can't connect to service.

**Solutions:**
- Ensure SLAM is running before starting map saver node
- Check service is available: `ros2 service list | grep save_map`
- Restart SLAM if needed

### Map Files Not Created

**Problem:** Map save command runs but no files appear.

**Solutions:**
- Wait up to 15 seconds (SLAM Toolbox may take time)
- Check workspace root directory: `ls ~/delivery_bot_ws/*.yaml`
- Verify map_saver_node is running and shows connection messages
- Check map_saver_node terminal for error messages

### Map Saved in Wrong Location

**Problem:** Map files are in workspace root instead of `data/maps/`.

**Solutions:**
- The map_saver_node should automatically move them to the correct location
- If not, manually move: `mv ~/delivery_bot_ws/your_map.* ~/delivery_bot_ws/data/maps/`

---

## Summary

**TurtleBot 4 (Raspberry Pi) runs:**
- ✅ `ros2 launch turtlebot4_bringup robot.launch.py` - Robot hardware

**Host Computer (NUC) runs:**
- ✅ `ros2 launch turtlebot4_navigation slam.launch.py` - SLAM
- ✅ `ros2 run teleop_twist_keyboard teleop_twist_keyboard` - Teleoperation
- ✅ `ros2 run map_manager map_saver_node` - Map saver
- ✅ `ros2 topic pub /save_map std_msgs/String "data: 'map_name'"` - Save command

**Result:**
- ✅ Map saved to `~/delivery_bot_ws/data/maps/map_name.yaml` and `.pgm`

---

## Next Steps

After creating the map, proceed to:
- **Tagging Locations:** See `LOCATION_TAGGING_GUIDE.md`
- **Delivery Bot Usage:** See `DELIVERY_BOT_GUIDE.md`

---

## Quick Reference

| Step | System | Command |
|------|--------|---------|
| 1. Start robot | TurtleBot 4 Pi | `ros2 launch turtlebot4_bringup robot.launch.py` |
| 2. Start SLAM | Host NUC | `ros2 launch turtlebot4_navigation slam.launch.py` |
| 3. Start teleop | Host NUC | `ros2 run teleop_twist_keyboard teleop_twist_keyboard` |
| 4. Drive robot | Host NUC | Use teleop keyboard controls |
| 5. Start map saver | Host NUC | `ros2 run map_manager map_saver_node` |
| 6. Save map | Host NUC | `ros2 topic pub /save_map std_msgs/String "data: 'map_name'"` |

