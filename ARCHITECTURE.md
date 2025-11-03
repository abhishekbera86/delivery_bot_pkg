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
```

## Data Flow

### 1. Map Creation Flow
```
User → SLAM → Map → map_manager → Save to disk
```

### 2. Location Tagging Flow
```
User → location_tag_node → Get current pose (TF) → Save to JSON
```

### 3. Navigation Flow
```
User (GUI) → /delivery_goal → goal_navigator_node 
    → location_manager (lookup) → Nav2 → Robot Navigation
```

## Topic/Service Architecture

### Topics

| Topic | Type | Publisher | Subscriber | Description |
|-------|------|-----------|------------|-------------|
| `/save_map` | std_msgs/String | User | map_manager | Save current map |
| `/map_save_status` | std_msgs/String | map_manager | User | Map save status |
| `/tag_location` | std_msgs/String | User | location_manager | Tag current position |
| `/location_tag_status` | std_msgs/String | location_manager | User | Tagging status |
| `/delivery_goal` | std_msgs/String | delivery_bot_gui | delivery_navigator | Goal location name |
| `/navigation_status` | std_msgs/String | delivery_navigator | delivery_bot_gui | Navigation status |

### Services

| Service | Type | Client | Server | Description |
|---------|------|--------|--------|-------------|
| `/map_saver/save_map` | nav2_msgs/SaveMap | map_manager | Nav2 | Save SLAM map |

### Actions

| Action | Type | Client | Server | Description |
|--------|------|--------|--------|-------------|
| `/navigate_to_pose` | nav2_msgs/NavigateToPose | delivery_navigator | Nav2 | Navigate to goal |

## Data Persistence

### Maps
- **Location**: `~/delivery_bot_ws/data/maps/`
- **Format**: `.yaml` (metadata) + `.pgm` (image)
- **Created by**: SLAM Toolbox / Cartographer
- **Saved by**: map_manager via Nav2 map_saver service

### Locations
- **Location**: `~/delivery_bot_ws/data/locations.json`
- **Format**: JSON
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

- **map**: Global map frame (from SLAM)
- **odom**: Odometry frame
- **base_link**: Robot base frame

Locations are stored in the `map` frame, and transformations are handled via TF2.

## Error Handling

1. **Map Save Failures**: Status published to `/map_save_status`
2. **Location Tagging Failures**: 
   - TF transform errors (no localization)
   - Status published to `/location_tag_status`
3. **Navigation Failures**:
   - Location not found
   - Nav2 action server unavailable
   - Status published to `/navigation_status`

## Extensibility

The architecture supports easy extension:
- New location types can be added to location_manager
- Additional GUI features can be added to delivery_bot_gui
- Different navigation strategies can be implemented in delivery_navigator
- Multiple map support can be added to map_manager

