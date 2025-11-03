# Quick Start Guide - Gazebo Simulation

Quick reference guide for getting started with the Delivery Bot simulation.

## Installation (First Time Only)

1. **Install dependencies:**
   ```bash
   cd ~/delivery_bot_ws/gazebo_simulation
   # Follow INSTALLATION.md for complete dependencies
   ```

2. **Build workspace:**
   ```bash
   cd ~/delivery_bot_ws/gazebo_simulation
   ./setup.sh
   # OR manually:
   colcon build
   source install/setup.bash
   ```

## Quick Workflow

### 1. Create a Map (One Time)

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash

# Terminal 1: Start simulation with SLAM
ros2 launch simulation simulation.launch.py

# Terminal 2: Start map saver
ros2 run map_manager map_saver_node

# Terminal 3: Teleoperate robot
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Drive around the office, then save map:
# Terminal 4:
ros2 topic pub /save_map std_msgs/String "data: 'office_map'"
```

### 2. Tag Locations (One Time)

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash

# Terminal 1: Start simulation with saved map
ros2 launch simulation simulation.launch.py use_slam:=false map:=~/delivery_bot_ws/gazebo_simulation/data/maps/office_map.yaml

# Terminal 2: Start location tagger
ros2 run location_manager location_tag_node

# Terminal 3: Teleoperate to each desk
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Terminal 4: Tag all 8 desks
ros2 topic pub /tag_location std_msgs/String "data: 'Desk1'"
ros2 topic pub /tag_location std_msgs/String "data: 'Desk2'"
# ... repeat for Desk3 through Desk8
```

### 3. Use Delivery Bot (Daily Use)

```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash

# Terminal 1: Start simulation with saved map
ros2 launch simulation simulation.launch.py use_slam:=false map:=~/delivery_bot_ws/gazebo_simulation/data/maps/office_map.yaml

# Terminal 2: Start navigator
ros2 run delivery_navigator goal_navigator_node

# Terminal 3: Start GUI
ros2 run delivery_bot_gui delivery_gui

# In GUI: Select a desk and click "Go to Location"
```

## Common Commands

### Start Simulation
```bash
# With SLAM (for mapping)
ros2 launch simulation simulation.launch.py

# With saved map (for navigation)
ros2 launch simulation simulation.launch.py use_slam:=false map:=~/delivery_bot_ws/gazebo_simulation/data/maps/office_map.yaml
```

### Save Map
```bash
ros2 run map_manager map_saver_node
ros2 topic pub /save_map std_msgs/String "data: 'office_map'"
```

### Tag Location
```bash
ros2 run location_manager location_tag_node
ros2 topic pub /tag_location std_msgs/String "data: 'Desk1'"
```

### Navigate
```bash
ros2 run delivery_navigator goal_navigator_node
ros2 run delivery_bot_gui delivery_gui
```

## File Locations

- **Maps:** `~/delivery_bot_ws/gazebo_simulation/data/maps/`
- **Locations:** `~/delivery_bot_ws/gazebo_simulation/data/locations.json`
- **World:** `~/delivery_bot_ws/gazebo_simulation/worlds/office_world_8desks.world`

## 8 Desk Locations

The world has 8 desks to tag:
- Desk1: Bottom Left (-6, -6)
- Desk2: Bottom Center (0, -6)
- Desk3: Bottom Right (6, -6)
- Desk4: Center Left (-6, 0)
- Desk5: Center Right (6, 0)
- Desk6: Top Left (-6, 6)
- Desk7: Top Center (0, 6)
- Desk8: Top Right (6, 6)

## Troubleshooting Quick Fixes

**Simulation won't start:**
- Check Gazebo is installed: `gazebo --version`
- Verify world file exists

**Can't find packages:**
```bash
cd ~/delivery_bot_ws/gazebo_simulation
source install/setup.bash
```

**Navigation not working:**
- Ensure map is loaded correctly
- Check navigator node is running
- Verify locations are tagged

## Detailed Guides

For complete instructions, see:
- **[INSTALLATION.md](INSTALLATION.md)** - Full installation guide
- **[docs/MAPPING_GUIDE.md](docs/MAPPING_GUIDE.md)** - Detailed mapping guide
- **[docs/LOCATION_TAGGING_GUIDE.md](docs/LOCATION_TAGGING_GUIDE.md)** - Location tagging guide
- **[docs/DELIVERY_BOT_GUIDE.md](docs/DELIVERY_BOT_GUIDE.md)** - Delivery bot usage guide
