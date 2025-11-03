# Location Tagging Guide - Simulation

This guide explains how to tag delivery locations (the 8 desks) in the simulation so they can be used for autonomous navigation.

## Overview

Location tagging allows you to save specific positions in the simulation environment so the delivery bot can navigate to them later. The simulation world has **8 desks** that should be tagged:

- **Desk 1**: Bottom Left (-6, -6)
- **Desk 2**: Bottom Center (0, -6)
- **Desk 3**: Bottom Right (6, -6)
- **Desk 4**: Center Left (-6, 0)
- **Desk 5**: Center Right (6, 0)
- **Desk 6**: Top Left (-6, 6)
- **Desk 7**: Top Center (0, 6)
- **Desk 8**: Top Right (6, 6)

Each location is saved with:
- Location name (e.g., "Desk1", "Desk2", etc.)
- Position (x, y coordinates)
- Orientation (yaw angle)
- Frame ID (typically "map")

All locations are saved to `~/delivery_bot_ws/gazebo_simulation/data/locations.json`

---

## Prerequisites

- ✅ A saved SLAM map (created using `MAPPING_GUIDE.md`)
- ✅ Robot simulation is running with localization
- ✅ Robot can be teleoperated or positioned
- ✅ Location manager package is built and ready

---

## Step-by-Step Location Tagging

### Step 1: Start Simulation with Localization

**Start simulation with saved map:**

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

**Expected output:**
- Gazebo window opens
- Robot appears in the simulation
- Localization is active
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

### Step 3: Start Location Tagger Node

**Open a new terminal:**

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 run location_manager location_tag_node
```

**Expected output:**
```
[INFO] Location Tag Node started. Send location name to /tag_location topic.
[INFO] Example: ros2 topic pub /tag_location std_msgs/String "data: 'Desk1'"
```

**Keep this terminal open** - The location tagger must be running.

---

### Step 4: Navigate Robot to First Desk (Desk1)

**Option A: Using Teleoperation**

Open a new terminal:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Use keyboard controls to drive the robot to **Desk 1** (bottom left, around coordinates -6, -6).

**Teleoperation Controls:**
- `i` - Move forward
- `k` - Stop
- `,` - Move backward
- `j` - Turn left
- `l` - Turn right

**Option B: Using Navigation (if you've already tagged some locations)**

You can use the GUI and navigator to move to approximate positions, then fine-tune with teleoperation.

---

### Step 5: Tag Desk1 Location

When the robot is positioned near Desk1, tag the location:

**Open a new terminal:**

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 topic pub /tag_location std_msgs/String "data: 'Desk1'"
```

**Expected output in location tagger terminal:**
```
[INFO] Tagging location: Desk1
[INFO] Successfully tagged location: Desk1
[INFO]   Position: x=-6.00, y=-6.00, z=0.00
[SUCCESS] Tagged Desk1
```

---

### Step 6: Repeat for All 8 Desks

Repeat Steps 4-5 for each desk:

1. **Desk1** - Bottom Left
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Desk1'"
   ```

2. **Desk2** - Bottom Center
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Desk2'"
   ```

3. **Desk3** - Bottom Right
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Desk3'"
   ```

4. **Desk4** - Center Left
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Desk4'"
   ```

5. **Desk5** - Center Right
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Desk5'"
   ```

6. **Desk6** - Top Left
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Desk6'"
   ```

7. **Desk7** - Top Center
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Desk7'"
   ```

8. **Desk8** - Top Right
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Desk8'"
   ```

---

### Step 7: Verify Tagged Locations

Check that all locations were saved:

```bash
cat ~/delivery_bot_ws/gazebo_simulation/data/locations.json
```

You should see a JSON file with all 8 desk locations.

**Example output:**
```json
{
  "Desk1": {
    "name": "Desk1",
    "frame_id": "map",
    "position": {"x": -6.0, "y": -6.0, "z": 0.0},
    "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
    "description": "Tagged location: Desk1"
  },
  "Desk2": {
    ...
  },
  ...
}
```

---

## Viewing Tagged Locations

You can view all tagged locations using the GUI:

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
ros2 run delivery_bot_gui delivery_gui
```

The GUI will show all tagged locations in the list.

---

## Tips for Better Location Tagging

1. **Position Carefully** - Position the robot exactly where you want it to arrive
2. **Face Desired Direction** - Rotate the robot to face the desired orientation
3. **Tag While Stationary** - Make sure the robot is not moving when tagging
4. **Verify Transform** - Check that TF transform from `base_link` to `map` is available
5. **Use Clear Names** - Use descriptive names like "Desk1", "Desk2", etc.

---

## Troubleshooting

### Location Tagging Fails
- Verify TF transform from `base_link` to `map` is available:
  ```bash
  ros2 run tf2_ros tf2_echo map base_link
  ```
- Ensure robot localization is active (AMCL):
  ```bash
  ros2 topic echo /amcl_pose
  ```
- Check location tagger node is running:
  ```bash
  ros2 node list | grep location_tag
  ```

### Transform Not Available
- Wait a few seconds for AMCL to localize
- Ensure simulation is running with localization (not SLAM)
- Check that the map is loaded correctly

### Location Not Saved
- Check file permissions in `~/delivery_bot_ws/gazebo_simulation/data/`
- Verify location tagger node is running
- Check for error messages in location tagger terminal

### Robot Position Not Accurate
- Make sure robot is stationary when tagging
- Wait for localization to stabilize
- Check AMCL pose estimate: `ros2 topic echo /amcl_pose`

---

## Next Steps

After tagging all 8 desk locations:

1. **Use delivery bot** - See `DELIVERY_BOT_GUIDE.md` to navigate to tagged locations using the GUI

---

**After tagging all locations, proceed to `DELIVERY_BOT_GUIDE.md` to use the delivery bot system.**
