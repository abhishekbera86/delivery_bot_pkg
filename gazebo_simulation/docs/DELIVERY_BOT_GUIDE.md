# Delivery Bot Guide - Using the Delivery Bot System in Simulation

This guide walks you through using the delivery bot system to navigate to tagged locations using a saved map **in Gazebo simulation**.

## System Architecture

This simulation process runs **entirely on a single computer**:

- **Gazebo Simulation** - TurtleBot 4 robot simulation
- **Nav2 Navigation** - Autonomous navigation stack
- **Delivery Bot Nodes** - GUI, navigator, and location manager

> **⚠️ Important:** This is a **simulation-only** setup. No physical robot hardware is required.

---

## Prerequisites

- ✅ A saved SLAM map (created using `MAPPING_GUIDE.md`)
- ✅ Tagged delivery locations (see `LOCATION_TAGGING_GUIDE.md` or Step 3 below)
- ✅ All 8 desk locations are tagged
- ✅ Simulation workspace is built
- ✅ All packages are installed (see `INSTALLATION.md`)

---

## Step-by-Step Delivery Bot Process

### Step 1: Start Simulation with Localization

Open a terminal and start the simulation with your saved map:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 launch simulation simulation.launch.py use_slam:=false map:=~/delivery_bot_ws/gazebo_simulation/data/maps/office_map.yaml
```

**What this does:**
- Starts Gazebo with the office world
- Spawns TurtleBot 4 robot in simulation
- Loads the saved map with AMCL localization
- Starts Nav2 navigation stack
- Robot is ready for navigation

**Expected output:**
- Gazebo window opens
- Robot appears in the simulation
- Localization is active
- Nav2 is running
- No error messages

**Keep this terminal open** - The simulation must continue running.

---

### Step 2: Wait for Localization

Wait a few seconds for AMCL to localize the robot. You can check localization status:

```bash
ros2 topic echo /amcl_pose
```

The robot should have a localized pose in the map frame.

---

### Step 3: Start Navigation Node

Open a new terminal:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 run delivery_navigator goal_navigator_node
```

**What this does:**
- Starts the delivery navigator node
- Connects to Nav2 navigation action server
- Listens for delivery goals from GUI
- Publishes navigation status

**Expected output:**
```
[INFO] Goal Navigator Node started
[INFO] Connected to navigate_to_pose action server
[INFO] Send location name to /delivery_goal topic to navigate
```

**Keep this terminal open** - The navigator must be running.

---

### Step 4: Start GUI

Open a new terminal:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 run delivery_bot_gui delivery_gui
```

**What this does:**
- Launches the delivery bot GUI window
- Loads all tagged locations
- Allows you to select destinations
- Sends navigation goals to the navigator
- Shows navigation status

**GUI Features:**
- **Location Dropdown** - Select from all tagged locations (Desk1, Desk2, ..., Desk8)
- **Go to Location Button** - Navigate to selected location
- **Refresh Locations Button** - Reload locations from file
- **Location List** - View all available locations
- **Status Display** - See current navigation status
- **Status Log** - View detailed navigation messages

---

### Step 5: Navigate to a Location

**Using the GUI:**

1. **Select a location** from the dropdown (e.g., "Desk1")
2. **Click "Go to Location"** button
3. **Confirm** when prompted
4. **Watch the robot navigate** in Gazebo

**What happens:**
- GUI sends goal location name to navigator
- Navigator looks up location coordinates
- Navigator sends navigation goal to Nav2
- Nav2 plans path and navigates robot
- Robot autonomously moves to the destination
- Status updates appear in GUI

**Expected behavior:**
- Robot starts moving toward the selected desk
- Path is planned avoiding obstacles
- Robot arrives at the destination
- Status shows "SUCCESS: Arrived at [Location]"

---

### Step 6: Navigate to Multiple Locations

You can navigate to any of the 8 tagged desk locations:

1. Select a different desk from the dropdown
2. Click "Go to Location"
3. Wait for robot to arrive
4. Repeat for other desks

**Try navigating to all 8 desks:**
- Desk1 (Bottom Left)
- Desk2 (Bottom Center)
- Desk3 (Bottom Right)
- Desk4 (Center Left)
- Desk5 (Center Right)
- Desk6 (Top Left)
- Desk7 (Top Center)
- Desk8 (Top Right)

---

### Step 7: Monitor Navigation

**In Gazebo:**
- Watch the robot move autonomously
- See the robot avoid obstacles
- Observe path planning in action

**In GUI:**
- Status shows current navigation state
- Status log shows detailed messages
- Status updates in real-time

**In Navigator Terminal:**
- Logs show navigation progress
- Goal acceptance/rejection messages
- Navigation completion status

---

## Using Command Line (Alternative)

Instead of using the GUI, you can also send navigation goals via command line:

**Open a new terminal:**

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash

# Navigate to Desk1
ros2 topic pub /delivery_goal std_msgs/String "data: 'Desk1'"

# Navigate to Desk2
ros2 topic pub /delivery_goal std_msgs/String "data: 'Desk2'"

# ... etc for other desks
```

---

## Stopping Navigation

**To stop navigation:**
- Close the GUI window
- Press `Ctrl+C` in navigator terminal
- Press `Ctrl+C` in simulation terminal to stop everything

---

## Troubleshooting

### Navigation Not Starting
- Verify Nav2 action server is running:
  ```bash
  ros2 action list | grep navigate_to_pose
  ```
- Check that the map is loaded correctly
- Ensure locations are in the correct frame (typically "map")
- Verify navigator node is running:
  ```bash
  ros2 node list | grep goal_navigator
  ```

### GUI Not Showing Locations
- Click "Refresh Locations" button in GUI
- Verify `locations.json` file exists:
  ```bash
  cat ~/delivery_bot_ws/gazebo_simulation/data/locations.json
  ```
- Check file permissions:
  ```bash
  ls -l ~/delivery_bot_ws/gazebo_simulation/data/locations.json
  ```
- Ensure locations are properly tagged (see `LOCATION_TAGGING_GUIDE.md`)

### Robot Not Moving
- Check that navigator received the goal:
  ```bash
  ros2 topic echo /delivery_goal
  ```
- Verify Nav2 is running:
  ```bash
  ros2 node list | grep nav2
  ```
- Check for errors in navigator terminal
- Ensure robot is localized:
  ```bash
  ros2 topic echo /amcl_pose
  ```

### Navigation Fails
- Check that the goal location is reachable
- Verify the map is loaded correctly
- Check for obstacles blocking the path
- Ensure robot is properly localized
- Check Nav2 logs for errors

### Goal Rejected
- Verify location exists in locations.json
- Check location coordinates are valid
- Ensure location is within map bounds
- Check that Nav2 can plan to the location

---

## Tips for Better Navigation

1. **Wait for Localization** - Make sure robot is localized before navigating
2. **Clear Paths** - Ensure paths between desks are clear of obstacles
3. **Start Simple** - Test with nearby desks first
4. **Monitor Status** - Watch GUI status for navigation progress
5. **Use RViz** - Start RViz to visualize navigation in real-time:
   ```bash
   rviz2
   ```
   Add displays for:
   - Map
   - RobotModel
   - Path (Nav2 plan)
   - LaserScan
   - Goal Pose

---

## Next Steps

After successfully navigating to all locations:

1. **Experiment** - Try different navigation scenarios
2. **Customize** - Tag additional locations if needed
3. **Optimize** - Fine-tune Nav2 parameters for better performance

---

**You've successfully set up and used the delivery bot simulation system!**
