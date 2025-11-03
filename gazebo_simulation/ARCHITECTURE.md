# Delivery Bot Architecture - Simulation

## System Architecture Overview

The delivery bot system **in Gazebo simulation** consists of five main ROS2 packages that work together to provide mapping, location tagging, and navigation capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                      │
│                  (delivery_bot_gui)                           │
│         - GUI for selecting delivery locations (8 desks)     │
│         - Status monitoring                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ /delivery_goal
┌─────────────────────▼───────────────────────────────────────┐
│                   Navigation Layer                            │
│              (delivery_navigator)                             │
│         - Receives goal location names                        │
│         - Converts to poses                                   │
│         - Sends to Nav2                                       │
└───────────────┬───────────────────────┬──────────────────────┘
                │                       │
                │ location lookup       │ /delivery_goal
┌───────────────▼───────────────────────┴──────────────────────┐
│                  Location Management                          │
│                 (location_manager)                            │
│         - Tags current robot position                        │
│         - Stores locations in JSON (8 desks)                 │
│         - Retrieves location poses                            │
└───────────────┬───────────────────────────────────────────────┘
                │
                │ TF: map -> base_link
┌───────────────▼───────────────────────────────────────────────┐
│                  Simulation Layer                              │
│              (Gazebo + TurtleBot 4)                           │
│         - Gazebo simulation with custom world                  │
│         - SLAM / Mapping (SLAM Toolbox)                       │
│         - Localization (AMCL)                                  │
│         - Navigation (Nav2)                                   │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│                    Map Management                              │
│                   (map_manager)                                │
│         - Saves SLAM maps                                     │
│         - Loads maps for navigation                           │
└───────────────────────────────────────────────────────────────┘
```

## Simulation Architecture

### Gazebo Simulation
- **World**: `office_world_8desks.world` - Custom office environment
- **Robot**: TurtleBot 4 model in Gazebo
- **Environment**: 20x20 meter office with 8 desks

### System Components

1. **Gazebo**: Physical simulation environment
2. **SLAM Toolbox**: Creates maps during exploration
3. **Nav2**: Navigation stack for path planning
4. **AMCL**: Localization with saved maps
5. **Delivery Bot Nodes**: Custom ROS2 packages

## Package Dependencies

```
delivery_bot_gui
  ├── location_manager (for location lookup)
  ├── rclpy
  └── tkinter (GUI framework)

delivery_navigator
  ├── location_manager (for location lookup)
  ├── nav2_msgs (Nav2 action interface)
  └── rclpy

location_manager
  ├── geometry_msgs (PoseStamped)
  ├── tf2_ros (transform lookup)
  ├── std_msgs (String messages)
  └── rclpy

map_manager
  ├── nav2_msgs (map saver service)
  ├── slam_toolbox (SLAM map saver)
  ├── std_msgs (String messages)
  └── rclpy
```

## Topic Flow

### Location Tagging Flow
```
User Command -> /tag_location (std_msgs/String)
  -> location_tag_node
  -> TF lookup (map -> base_link)
  -> location_handler.add_location()
  -> Save to locations.json
  -> /location_tag_status (std_msgs/String)
```

### Navigation Flow
```
GUI Selection -> /delivery_goal (std_msgs/String)
  -> goal_navigator_node
  -> location_handler.get_location()
  -> Convert to PoseStamped
  -> Nav2 navigate_to_pose action
  -> Gazebo robot moves
  -> /navigation_status (std_msgs/String)
  -> GUI updates
```

### Map Saving Flow
```
User Command -> /save_map (std_msgs/String)
  -> map_saver_node
  -> SLAM Toolbox or Nav2 map_saver service
  -> Save map files (.yaml, .pgm)
  -> /map_save_status (std_msgs/String)
```

## Data Flow

### Mapping Phase
1. Gazebo simulation starts
2. SLAM Toolbox creates map from laser scan
3. User teleoperates robot to explore
4. Map saver saves map to `data/maps/`

### Location Tagging Phase
1. Simulation loads saved map with AMCL
2. User navigates robot to each desk
3. Location tagger saves desk positions to `data/locations.json`
4. All 8 desks are tagged

### Navigation Phase
1. Simulation loads saved map with AMCL
2. Navigator node connects to Nav2
3. GUI loads locations from JSON
4. User selects desk location
5. Navigator sends goal to Nav2
6. Nav2 plans path and navigates robot
7. Status updates sent to GUI

## File Structure

```
gazebo_simulation/
├── data/
│   ├── maps/
│   │   ├── office_map.yaml
│   │   └── office_map.pgm
│   └── locations.json
│       └── {Desk1, Desk2, ..., Desk8}
├── worlds/
│   └── office_world_8desks.world
└── launch/
    └── simulation.launch.py
```

## Launch File Architecture

`simulation.launch.py` orchestrates:
1. **Gazebo Launch**: Starts simulation with custom world
2. **SLAM Launch** (if `use_slam=true`): For mapping
3. **Localization Launch** (if `use_slam=false`): For navigation
4. **Nav2 Launch**: Navigation stack

## Key Design Decisions

1. **Single Computer**: Everything runs on one machine (simulation)
2. **Custom World**: Simple office world with 8 desks for testing
3. **JSON Storage**: Simple, human-readable location format
4. **Modular Packages**: Each component is a separate package
5. **ROS2 Topics**: Loose coupling between components
6. **Simulation Paths**: All data uses `gazebo_simulation` directory

## Scalability Considerations

- Easy to add more desks/locations
- Can extend world file with more furniture
- GUI can handle any number of locations
- Map format is standard (compatible with real hardware maps)

## Differences from Real Hardware

| Aspect | Real Hardware | Simulation |
|--------|---------------|------------|
| Robot | Physical TurtleBot 4 | Gazebo model |
| Computers | 2 (Pi + Host) | 1 |
| World | Real environment | `office_world_8desks.world` |
| Network | ROS2 distributed | Local only |
| Data Path | `delivery_bot_ws/data/` | `gazebo_simulation/data/` |

## Future Enhancements

- Add more furniture/obstacles to world
- Support multiple maps
- Add location editing in GUI
- Visualize map in GUI
- Add more delivery scenarios
