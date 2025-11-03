# Mapping Guide - Creating SLAM Maps in Simulation

This guide walks you through the complete process of creating a SLAM map using TurtleBot 4 **in Gazebo simulation** for the delivery bot project.

## System Architecture

This simulation process runs **entirely on a single computer**:

- **Gazebo Simulation** - TurtleBot 4 robot simulation
- **SLAM Toolbox** - For simultaneous localization and mapping

> **⚠️ Important:** This is a **simulation-only** setup. No physical robot hardware is required.

---

## Prerequisites

- ✅ Gazebo is installed and working
- ✅ ROS2 Jazzy is installed on your computer
- ✅ Nav2, SLAM Toolbox, and TurtleBot 4 packages are installed
- ✅ Simulation workspace is built (see `INSTALLATION.md`)
- ✅ All packages are installed (see `INSTALLATION.md`)

---

## Step-by-Step Mapping Process

### Step 1: Build and Source Workspace

Open a terminal and navigate to the simulation directory:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
colcon build
source install/setup.bash
```

---

### Step 2: Start Simulation with SLAM

Launch the simulation with SLAM enabled:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 launch simulation simulation.launch.py
```

**What this does:**
- Starts Gazebo with the `office_world_8desks.world` world
- Spawns TurtleBot 4 robot in the simulation
- Starts SLAM Toolbox for simultaneous localization and mapping
- Starts Nav2 navigation stack
- Creates and updates a map as the robot moves

**Expected output:**
- Gazebo window opens with the office world and robot
- SLAM Toolbox node started
- Map is being generated
- No error messages

**Keep this terminal open** - The simulation and SLAM must continue running during the entire mapping process.

---

### Step 3: (Optional) Start RViz for Visualization

Open a new terminal:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
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

### Step 4: Teleoperate the Robot

Open a new terminal:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Teleoperation Controls:**
- `i` - Move forward
- `k` - Stop
- `,` - Move backward
- `j` - Turn left
- `l` - Turn right
- `q/z` - Increase/decrease linear speed
- `w/x` - Increase/decrease angular speed

**Mapping Strategy:**
1. Drive the robot around the entire office area
2. Make sure to cover all corners and obstacles
3. Navigate around all 8 desks
4. Go through all corridors and open spaces
5. Return to the starting position for a closed loop

---

### Step 5: Start Map Saver Node

Open a new terminal:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 run map_manager map_saver_node
```

**What this does:**
- Starts the map saver node
- Listens for map save commands
- Saves maps to `~/delivery_bot_ws/gazebo_simulation/data/maps/`

**Keep this terminal open** - The map saver must be running when you save the map.

---

### Step 6: Save the Map

After you've explored the entire environment, save the map:

Open a new terminal:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 topic pub /save_map std_msgs/String "data: 'office_map'"
```

**What this does:**
- Saves the current SLAM map
- Creates two files:
  - `office_map.yaml` - Map metadata
  - `office_map.pgm` - Map image file

**Files are saved to:** `~/delivery_bot_ws/gazebo_simulation/data/maps/`

**Expected output:**
- Map saver node logs show "Map saved successfully"
- Files appear in the maps directory

---

### Step 7: Verify Map Files

Check that the map files were created:

```bash
ls -lh ~/delivery_bot_ws/gazebo_simulation/data/maps/
```

You should see:
- `office_map.yaml`
- `office_map.pgm`

---

### Step 8: Stop the Simulation

Press `Ctrl+C` in the simulation terminal to stop:
- Gazebo will close
- SLAM will stop
- Navigation stack will stop

---

## Map Verification

You can verify your map by viewing it:

```bash
# View the map image
eog ~/delivery_bot_ws/gazebo_simulation/data/maps/office_map.pgm

# Or check the YAML file
cat ~/delivery_bot_ws/gazebo_simulation/data/maps/office_map.yaml
```

---

## Next Steps

After creating the map:

1. **Tag locations** - See `LOCATION_TAGGING_GUIDE.md` to tag the 8 desk locations
2. **Use delivery bot** - See `DELIVERY_BOT_GUIDE.md` to navigate to tagged locations

---

## Troubleshooting

### Gazebo Not Starting
- Ensure Gazebo is installed: `gazebo --version`
- Check world file exists: `ls ~/delivery_bot_ws/gazebo_simulation/worlds/office_world_8desks.world`

### SLAM Not Creating Map
- Verify SLAM is running: `ros2 node list | grep slam`
- Check laser scan is publishing: `ros2 topic echo /scan`
- Ensure odometry is available: `ros2 topic echo /odom`

### Map Saver Not Working
- Ensure map saver node is running: `ros2 node list | grep map_saver`
- Check service is available: `ros2 service list | grep map_saver`
- Verify SLAM is active and has created a map

### Robot Not Moving in Teleoperation
- Ensure teleop node is running: `ros2 node list | grep teleop`
- Check cmd_vel topic: `ros2 topic echo /cmd_vel`
- Verify the robot model is correctly loaded in Gazebo

### Poor Map Quality
- Drive slower for better map quality
- Make sure to cover all areas
- Close loops by returning to starting position
- Avoid sharp turns and sudden stops

---

## Tips for Better Maps

1. **Drive Slowly** - Slower exploration produces better quality maps
2. **Complete Coverage** - Make sure to map all areas of interest
3. **Closed Loops** - Return to the starting position to close loops
4. **Avoid Obstacles** - Don't bump into walls or desks
5. **Multiple Passes** - Make multiple passes through the same areas for better map quality

---

**After creating your map, proceed to `LOCATION_TAGGING_GUIDE.md` to tag the 8 desk locations.**
