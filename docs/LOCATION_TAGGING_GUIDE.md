# Location Tagging Guide

This guide explains how to tag delivery locations so they can be used for autonomous navigation.

## Overview

Location tagging allows you to save specific positions in your environment so the delivery bot can navigate to them later. Each location is saved with:
- Location name (e.g., "Office1", "Desk_A")
- Position (x, y coordinates)
- Orientation (yaw angle)
- Frame ID (typically "map")

All locations are saved to `~/delivery_bot_ws/data/locations.json`

---

## Prerequisites

- ✅ Robot is localized in a map (localization running)
- ✅ Map is loaded and robot knows its position
- ✅ Robot can be teleoperated or manually positioned
- ✅ Location manager package is built and ready

---

## Step-by-Step Location Tagging

### Step 1: Start Robot Hardware

**📍 On: TurtleBot 4 (Raspberry Pi)**

```bash
ros2 launch turtlebot4_bringup robot.launch.py
```

**⚠️ Important:** This must run on the TurtleBot 4 Raspberry Pi.

---

### Step 2: Load Map and Start Localization

**📍 On: Host Computer (Intel NUC)**

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 launch turtlebot4_navigation localization.launch.py map:=~/delivery_bot_ws/data/maps/office_map.yaml
```

Replace `office_map.yaml` with your actual map file.

---

### Step 3: Start Location Tagger Node

**📍 On: Host Computer (Intel NUC)**

Open a new terminal:

```bash
cd ~/delivery_bot_ws
source install/setup.bash
ros2 run location_manager location_tag_node
```

**Expected output:**
```
[INFO] Location Manager Node started
[INFO] Locations file: /home/turtlebot4/delivery_bot_ws/data/locations.json
[INFO] Ready to tag locations. Publish to /tag_location topic
```

**Keep this terminal open** - The location tagger must be running.

---

### Step 4: Navigate Robot to a Location

**📍 On: Host Computer (Intel NUC)**

#### Option A: Using Teleoperation

Open a new terminal:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Use the keyboard controls to drive the robot to the location you want to tag:
- `i` - Move forward
- `j` - Turn left
- `l` - Turn right
- `,` - Move backward
- `k` - Stop

#### Option B: Using Manual Positioning

If your robot allows manual positioning, physically move it to the desired location.

---

### Step 5: Tag the Current Location

**📍 On: Host Computer (Intel NUC)**

Once the robot is at the location you want to tag, open another terminal:

```bash
ros2 topic pub /tag_location std_msgs/String "data: 'Office1'"
```

**Replace `'Office1'` with your desired location name**, for example:

**Office Environments:**
- `'Office1'`, `'Office2'`, `'Office3'`
- `'Desk_A'`, `'Desk_B'`, `'Desk_C'`
- `'Reception'`, `'Kitchen'`, `'Conference_Room'`

**Lab Environments:**
- `'Lab_Station1'`, `'Lab_Station2'`
- `'Workbench_A'`, `'Workbench_B'`

**Warehouse/Industrial:**
- `'Station_1'`, `'Station_2'`
- `'Loading_Dock'`, `'Storage_Area'`

**What happens:**
- Location tagger reads current robot pose (position + orientation)
- Converts it to a pose in the map frame
- Saves it to `locations.json` with the given name

**Expected output in location_tag_node terminal:**
```
[INFO] Received location tag request: Office1
[INFO] Tagging location: Office1
[INFO] Location saved successfully: Office1
[INFO] Position: x=1.23, y=4.56, theta=0.78
```

---

### Step 6: Repeat for Additional Locations

**📍 On: Host Computer (Intel NUC)**

For each additional location:

1. **Navigate robot** to the new location (using teleop or manually)
2. **Tag the location** with a unique name:
   ```bash
   ros2 topic pub /tag_location std_msgs/String "data: 'Office2'"
   ```

3. **Repeat** until all desired locations are tagged

**Example sequence:**
```bash
# Tag first location
ros2 topic pub /tag_location std_msgs/String "data: 'Office1'"

# Move robot to second location (using teleop)
# Then tag it
ros2 topic pub /tag_location std_msgs/String "data: 'Office2'"

# Move robot to third location
# Then tag it
ros2 topic pub /tag_location std_msgs/String "data: 'Office3'"
```

---

### Step 7: Verify Tagged Locations

**📍 On: Host Computer (Intel NUC)**

Check that locations were saved correctly:

```bash
cat ~/delivery_bot_ws/data/locations.json
```

**Expected output:**
```json
{
  "Office1": {
    "name": "Office1",
    "frame_id": "map",
    "position": {
      "x": 1.234,
      "y": 4.567,
      "z": 0.0
    },
    "orientation": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.383,
      "w": 0.924
    },
    "description": "Tagged location: Office1"
  },
  "Office2": {
    ...
  }
}
```

---

### Step 8: Stop Location Tagging

**📍 On: Host Computer (Intel NUC)**

When done tagging locations:
1. Press `Ctrl+C` in the location_tag_node terminal
2. Stop teleoperation (if running)
3. Stop localization (if you're done with the session)

---

## Location Naming Guidelines

### Best Practices

1. **Use descriptive names:**
   - ✅ `'Office1'`, `'Reception'`, `'Conference_Room'`
   - ❌ `'loc1'`, `'a'`, `'123'`

2. **Use consistent naming:**
   - All offices: `'Office1'`, `'Office2'`, `'Office3'`
   - All desks: `'Desk_A'`, `'Desk_B'`, `'Desk_C'`

3. **Avoid special characters:**
   - ✅ Use letters, numbers, and underscores
   - ❌ Avoid spaces, hyphens, special symbols

4. **Make names unique:**
   - Each location must have a different name
   - Duplicate names will overwrite previous locations

---

## Viewing and Editing Locations

### View All Locations

```bash
cat ~/delivery_bot_ws/data/locations.json
```

### Edit Locations Manually

**⚠️ Advanced Users Only**

You can manually edit `~/delivery_bot_ws/data/locations.json` to:
- Fix incorrect positions
- Rename locations
- Delete locations
- Add descriptions

**Important:** Make sure JSON syntax is valid or the file won't load correctly.

---

## Troubleshooting

### Location Not Saving

**Problem:** No output when tagging location.

**Solutions:**
- Verify location_tag_node is running
- Check that robot is localized: `ros2 run tf2_ros tf2_echo map base_link`
- Verify `/tag_location` topic exists: `ros2 topic list | grep tag_location`
- Check location_tag_node terminal for error messages

### Incorrect Position Tagged

**Problem:** Tagged location doesn't match robot's actual position.

**Solutions:**
- Ensure robot is fully localized before tagging
- Wait a moment after moving robot before tagging
- Check TF transform is stable: `ros2 run tf2_ros tf2_echo map base_link`
- Verify map is loaded correctly

### Location Name Already Exists

**Problem:** Want to update an existing location.

**Solutions:**
- Use the same name to overwrite the existing location
- Or manually edit `locations.json` to change the name
- Or delete the old entry and tag with a new name

### Locations File Not Found

**Problem:** `locations.json` doesn't exist.

**Solutions:**
- The file is created automatically on first tag
- Verify `data/` directory exists: `mkdir -p ~/delivery_bot_ws/data`
- Check file permissions
- Verify location_manager package is built

---

## Summary

**TurtleBot 4 (Raspberry Pi) runs:**
- ✅ `ros2 launch turtlebot4_bringup robot.launch.py` - Robot hardware

**Host Computer (NUC) runs:**
- ✅ `ros2 launch turtlebot4_navigation localization.launch.py map:=path/to/map.yaml` - Localization
- ✅ `ros2 run location_manager location_tag_node` - Location tagger
- ✅ `ros2 run teleop_twist_keyboard teleop_twist_keyboard` - Teleoperation (optional)
- ✅ `ros2 topic pub /tag_location std_msgs/String "data: 'LocationName'"` - Tag command

**Result:**
- ✅ Locations saved to `~/delivery_bot_ws/data/locations.json`
- ✅ Locations can be used for autonomous navigation
- ✅ Locations appear in delivery bot GUI

---

## Next Steps

After tagging locations:
- **Use Delivery Bot:** See `DELIVERY_BOT_GUIDE.md` to navigate to tagged locations
- **Create More Maps:** See `MAPPING_GUIDE.md` to create additional maps

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start location tagger | `ros2 run location_manager location_tag_node` |
| Tag current location | `ros2 topic pub /tag_location std_msgs/String "data: 'LocationName'"` |
| View locations | `cat ~/delivery_bot_ws/data/locations.json` |
| Verify TF available | `ros2 run tf2_ros tf2_echo map base_link` |

