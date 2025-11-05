# Delivery Bot Architecture

## System Architecture Overview

The delivery bot system consists of five main ROS2 packages that work together to provide mapping, location tagging, and navigation capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                      │
│                  (delivery_bot_gui)                           │
│         - GUI for selecting delivery locations                │
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
│         - Tags current robot position                         │
│         - Stores locations in JSON                            │
│         - Retrieves location poses                            │
│         - Works during SLAM or after AMCL initialization     │
└───────────────┬───────────────────────────────────────────────┘
                │
                │ TF: map -> base_link
┌───────────────▼───────────────────────────────────────────────┐
│                     Robot Platform                            │
│                    (TurtleBot 4)                              │
│         - SLAM / Mapping                                      │
│         - Localization (AMCL)                                │
│         - Navigation (Nav2)                                   │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│                    Map Management                              │
│                   (map_manager)                               │
│         - Saves SLAM maps                                     │
│         - Loads maps for navigation                           │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│              Initial Pose Setter                              │
│            (initial_pose_setter)                              │
│         - GUI for setting initial pose                        │
│         - Uses tagged locations for automatic setup            │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐
│         Unified Mapping and Tagging GUI                       │
│         (location_manager - mapping_and_tagging_gui)           │
│         - Single GUI for mapping, tagging, and map saving     │
│         - JSON filename configuration                          │
│         - Location tagging during SLAM                         │
│         - Map saving from GUI                                  │
└───────────────────────────────────────────────────────────────┘
```

## Package Dependencies

```
delivery_bot_gui
    ├── location_manager (exec_depend)
    └── delivery_navigator (via topic)

delivery_navigator
    ├── location_manager (exec_depend)
    └── nav2_msgs (action client)

location_manager
    ├── tf2_ros (for pose transformation)
    └── geometry_msgs

map_manager
    └── nav2_msgs (map_saver service)

initial_pose_setter
    ├── geometry_msgs
    └── location_manager (for loading locations)
```

## Data Flow

### 1. Map Creation with Location Tagging Flow (Unified GUI)
```
User → Unified Launch (SLAM + Map Saver + Unified GUI)
    → Unified GUI: Set JSON filename → Tag locations → Save map
    → SLAM creates map frame → Get current pose (TF: map -> base_link)
    → Save locations to JSON → Save map to disk
```

**Key Insight:** 
- **Unified GUI** - Single interface handles everything: JSON filename, location tagging, map saving
- **Single Launch Command** - Everything starts with one command: `ros2 launch launch/mapping_with_tagging.launch.py`
- Location tagging works during SLAM because the `map` frame exists during mapping. No initial pose needed!

### 2. Location Tagging Flow (After Loading Saved Map)
```
User → Location Tagging GUI → Get current pose (TF: map -> base_link)
    → Save to JSON → Update GUI
```

### 3. Navigation Flow
```
User (GUI) → /delivery_goal → goal_navigator_node 
    → location_manager (lookup) → Nav2 → Robot Navigation
```

### 4. Initial Pose Setting Flow
```
User → Initial Pose GUI → Select tagged location OR manual entry
    → Publish to /initialpose → AMCL → Robot localized
```

## Topic/Service Architecture

### Topics

| Topic | Type | Publisher | Subscriber | Description |
|-------|------|-----------|------------|-------------|
| `/save_map` | std_msgs/String | User | map_manager | Save current map |
| `/map_save_status` | std_msgs/String | map_manager | User | Map save status |
| `/tag_location` | std_msgs/String | User | location_manager | Tag current position (command-line) |
| `/location_tag_status` | std_msgs/String | location_manager | User | Tagging status |
| `/delivery_goal` | std_msgs/String | delivery_bot_gui | delivery_navigator | Goal location name |
| `/navigation_status` | std_msgs/String | delivery_navigator | delivery_bot_gui | Navigation status |
| `/initialpose` | geometry_msgs/PoseWithCovarianceStamped | initial_pose_setter | AMCL | Set initial pose |
| `/initial_pose_set` | std_msgs/Bool | initial_pose_setter | location_manager | Signal that initial pose is set |

### Services

| Service | Type | Client | Server | Description |
|---------|------|--------|--------|-------------|
| `/map_saver/save_map` | nav2_msgs/SaveMap | map_manager | Nav2 | Save SLAM map |
| `/slam_toolbox/save_map` | slam_toolbox/SaveMap | map_manager | SLAM Toolbox | Save SLAM map |

### Actions

| Action | Type | Client | Server | Description |
|--------|------|--------|--------|-------------|
| `/navigate_to_pose` | nav2_msgs/NavigateToPose | delivery_navigator | Nav2 | Navigate to goal |

## Data Persistence

### Maps
- **Location**: `~/delivery_bot_pkg/data/maps/`
- **Format**: `.yaml` (metadata) + `.pgm` (image)
- **Created by**: SLAM Toolbox / Cartographer
- **Saved by**: map_manager via SLAM Toolbox or Nav2 map_saver service

### Locations
- **Location**: `~/delivery_bot_pkg/data/locations/`
- **Format**: JSON files (filename configured in unified GUI)
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

## Coordinate Frames

- **map**: Global map frame (from SLAM or AMCL)
- **odom**: Odometry frame
- **base_link**: Robot base frame

**Locations are stored in the `map` frame**, and transformations are handled via TF2.

**Key Insight:** During SLAM, the `map` frame exists immediately, allowing location tagging without needing to set initial pose first.

## Workflows

### Workflow 1: Map Creation with Location Tagging (Unified GUI)

1. Start robot hardware (TurtleBot 4 Pi)
2. Start unified mapping and tagging system (Host NUC) - **Single launch command!**
   - `ros2 launch launch/mapping_with_tagging.launch.py`
   - Starts SLAM, map saver node, and unified GUI
3. Configure JSON filename in unified GUI (optional)
4. Drive robot and tag locations - Locations saved to JSON
5. Save map from unified GUI - Map saved to disk

**Result:** 
- Map saved to: `~/delivery_bot_pkg/data/maps/{map_name}.yaml`
- Locations saved to: `~/delivery_bot_pkg/data/locations/{json_filename}.json`
- Ready for navigation.

### Workflow 2: Delivery Bot Navigation

1. Start robot hardware (TurtleBot 4 Pi)
2. Load saved map with AMCL (Host NUC)
3. Set initial pose using Initial Pose GUI:
   - Select tagged location (recommended)
   - OR manual entry
   - OR RViz2 visual method
4. Start Nav2 navigation (Host NUC)
5. Start delivery navigator (Host NUC)
6. Start delivery GUI (Host NUC)
7. Select location and navigate!

**Result:** Robot navigates to selected location autonomously.

## Error Handling

1. **Map Save Failures**: Status published to `/map_save_status`
2. **Location Tagging Failures**: 
   - TF transform errors (no map frame or localization)
   - Status published to `/location_tag_status`
3. **Navigation Failures**:
   - Location not found
   - Nav2 action server unavailable
   - Status published to `/navigation_status`
4. **Initial Pose Failures**:
   - Invalid pose coordinates
   - AMCL not running
   - Error messages displayed in GUI

## Extensibility

The architecture supports easy extension:
- New location types can be added to location_manager
- Additional GUI features can be added to delivery_bot_gui
- Different navigation strategies can be implemented in delivery_navigator
- Multiple map support can be added to map_manager
- Additional initial pose methods can be added to initial_pose_setter
